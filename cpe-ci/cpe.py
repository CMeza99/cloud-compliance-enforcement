#!/usr/bin/env python3
# pylint: disable=missing-class-docstring, missing-function-docstring
""" Validate c7n policies """
import argparse
import logging
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from os import PathLike, environ
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Iterable, List, Optional, Union

import c7n.commands
import pkg_resources
import yaml
from c7n.config import Config


logging.basicConfig(level=environ.get("CPE_LOGLEVEL", "warning").upper())
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("custodian").setLevel(logging.WARNING)
logging.getLogger("custodian.policy").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__name__)

POLICY_MODE_FILE = Path(__file__).parents[1].joinpath("policy-modes.yaml")
POLICY_DIR = Path(__file__).parents[1].joinpath("policies")
MODE_DIR = Path(__file__).parents[1].joinpath("modes")


try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = None


def _read_yaml(yaml_file: Union[Path, PathLike]) -> Dict[str, Iterable[Any]]:
    return yaml.safe_load(Path(yaml_file).with_suffix(".yaml").read_text())


def policy_with_mode(policy_data: Dict[str, Any], mode_data: Dict[str, Any]) -> Dict[str, Any]:
    """

    Args:
        policy_data: policy to have mode applied
        mode_data: mode to be appended to policy

    Returns:
        policy with mode appended
    """
    if not policy_data:
        return dict()
    policy_list = map(lambda policy_: dict(policy_, mode=mode_data), policy_data.get("policies"))
    return {"policies": list(policy_list)}


def create_compiled_files(
    mode_file: [Union[Path, PathLike]],
    policy_files: Iterable[Union[Path, PathLike]],
    outdir: [Union[Path, PathLike]],
) -> None:
    mode_data = _read_yaml(Path(mode_file))
    for policyfile_ in policy_files:
        processed_policy = policy_with_mode(_read_yaml(Path(POLICY_DIR, policyfile_)), mode_data)
        policy_file = Path(outdir, policyfile_).with_suffix(".yaml")
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        policy_file.write_text(yaml.safe_dump(processed_policy))


def process_policies(
    policy_mode_file: Union[Path, PathLike],
    modedir: Union[Path, PathLike],
    outdir: Union[Path, PathLike],
):
    policy_modes = _read_yaml(policy_mode_file)
    for key_, val_ in policy_modes.items():
        create_compiled_files(Path(modedir, key_), val_, outdir)


def is_valid(policy_file: Union[Path, PathLike]) -> bool:
    """

    Args:
        policy_file: file to be validated

    Returns:
        True if policy is valid
    """
    try:
        c7n.commands.validate(Config.empty(configs={Path(policy_file).resolve()}))
    except SystemExit:
        _LOGGER.debug("Invalid policy %s", policy_file.name)
    else:
        _LOGGER.debug("Validated policy %s", policy_file.name)
        return True
    return False


def get_invalid(policy_dir: Union[Path, PathLike]) -> Iterable[str]:
    return [
        str(pfile_.relative_to(policy_dir))
        for pfile_ in filter(
            lambda ppath_: not (is_valid(ppath_)), Path(policy_dir).rglob("*.yaml")
        )
    ]


@dataclass(eq=False)
class C7nDefaults:  # pylint: disable=too-many-instance-attributes
    configs: List[str] = field(default_factory=list)
    output_dir: str = "output"

    profile: Optional[str] = environ.get("AWS_PROFILE", None)
    regions: List[str] = field(default_factory=list)
    cache: str = "~/.cache/cloud-custodian.cache"
    cache_period: int = 15

    policy_filters: List[str] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)

    debug: bool = False

    vars: Optional[List] = None

    def __post_init__(self):
        self.regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


@dataclass(eq=False)
class C7nRunDefaults(C7nDefaults):
    skip_validation: bool = True
    dryrun: bool = bool(int(environ.get("CPE_DRYRUN", 1)))


class C7nCommands:
    @staticmethod
    def exec(command: str, config: C7nDefaults = C7nDefaults(), policies: Iterable[Path] = ()):
        def _new_cfg(policy):
            return replace(
                config,
                cache=str(Path(".cache", config.profile, policy.stem).with_suffix(".cache")),
                configs=[str(policy)],
            )

        c7n_cmd = getattr(c7n.commands, command)
        cfg_gen = (Config.empty(**asdict(_new_cfg(policy_))) for policy_ in policies)
        with ThreadPoolExecutor() as executor:
            list(executor.map(c7n_cmd, cfg_gen))

    @classmethod
    def run(
        cls,
        config: C7nDefaults = C7nRunDefaults(),
        policies: Iterable[Union[Path, PathLike]] = (),
    ):
        cls.exec("run", config, policies)


def _get_params():
    parser = argparse.ArgumentParser(
        description="Cloud Policy Enforcement Script: A workflow manager wrapping Cloud Custodian.",
        epilog="Policies are always validated, even when no c7n command is specified.",
        allow_abbrev=False,
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-x",
        "--c7n-cmd",
        choices=("run",),
        required=False,
        default=None,
        help="Cloud Custodian command to execute",
    )

    return parser.parse_args()


def main() -> None:
    """ Main entry point """
    cli_params = _get_params()
    c7n_cmd = cli_params.c7n_cmd
    with TemporaryDirectory(prefix="c7n-") as tmpdir:
        process_policies(POLICY_MODE_FILE, MODE_DIR, tmpdir)
        invalid_policies = get_invalid(tmpdir)
        if invalid_policies:
            sys.exit(f"INVALID POLICIES:\n{yaml.safe_dump(invalid_policies)}")
        if c7n_cmd:
            getattr(C7nCommands, c7n_cmd)(policies=Path(tmpdir).rglob("*.yaml"))
    sys.exit()


if __name__ == "__main__":
    main()

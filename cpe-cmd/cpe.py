#!/usr/bin/env python3
# pylint: disable=missing-class-docstring, missing-function-docstring
"""
Process and run c7n policies

Environment Variables:
CPE_LOGLEVEL=warning
CPE_DRYRUN=1  # Only for 'run'

Constants:
POLICY_MODE_FILE = policy-modes.yaml
POLICY_DIR = policies
MODE_DIR = modes
"""
import argparse
import io
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

POLICY_MODE_FILE = Path("policy-modes.yaml")
POLICY_DIR = Path("policies")
MODE_DIR = Path("modes")


try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = None


def _parser_params(params: Optional[Iterable[str]] = None):
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
        choices=("run", "report"),
        required=False,
        default=None,
        help="Cloud Custodian command to execute",
    )

    return parser.parse_args(params)


def _read_yaml(yaml_file: Union[Path, PathLike]) -> Dict[str, Iterable[Any]]:
    return yaml.safe_load(Path(yaml_file).with_suffix(".yaml").read_text())


class PolicyProcessor:
    @staticmethod
    def apply_mode(policy_data: Dict[str, Any], mode_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            policy_data: policy to have mode applied
            mode_data: mode to be appended to policy

        Returns:
            policy with mode appended
        """
        if not policy_data:
            return dict()
        policy_list = map(
            lambda policy_: dict(policy_, mode=mode_data), policy_data.get("policies")
        )
        return {"policies": list(policy_list)}

    @classmethod
    def write_all(
        cls, policy_mode_file: Union[Path, PathLike], outdir: Union[Path, PathLike],
    ):
        policy_modes = _read_yaml(policy_mode_file)
        for key_, val_ in policy_modes.items():
            mode_data = _read_yaml(Path(MODE_DIR, key_))
            for policyfile_ in val_:
                processed_policy = cls.apply_mode(
                    _read_yaml(Path(POLICY_DIR, policyfile_)), mode_data
                )
                policy_file = Path(outdir, policyfile_).with_suffix(".yaml")
                policy_file.parent.mkdir(parents=True, exist_ok=True)
                policy_file.write_text(yaml.safe_dump(processed_policy))

    @staticmethod
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

    @classmethod
    def get_invalid_all(cls, policy_dir: Union[Path, PathLike]) -> Iterable[str]:
        return [
            str(pfile_.relative_to(policy_dir))
            for pfile_ in filter(
                lambda ppath_: not (cls.is_valid(ppath_)), Path(policy_dir).rglob("*.yaml")
            )
        ]


@dataclass(eq=False)
class C7nDefaults:  # pylint: disable=too-many-instance-attributes
    configs: List[str] = field(default_factory=list)
    output_dir: str = "output"

    profile: Optional[str] = environ.get("AWS_PROFILE", None)
    regions: List[str] = field(default_factory=list)
    cache: Optional[str] = None
    cache_period: int = 0

    policy_filters: List[str] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)

    debug: bool = False

    # AWS Provider Options
    profile: Optional[str] = None
    region: str = "us-east-1"

    # c7n internal use
    vars: Optional[List] = None

    def __post_init__(self):
        self.regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


@dataclass(eq=False)
class C7nRunDefaults(C7nDefaults):
    skip_validation: bool = True
    dryrun: bool = bool(int(environ.get("CPE_DRYRUN", 1)))


@dataclass(eq=False)
class C7nReportDefaults(C7nDefaults):
    """
    CURRENTLY NOT FUNCTIONAL!
    TODO: check for exec-option and override output_dir
    """
    days: int = 1
    field: Optional[List] = field(default_factory=list)
    no_default_fields: bool = False
    format: str = "csv"
    raw: Optional[io.TextIOWrapper] = None

    def __post_init__(self):
        self.output_dir = "s3://c7n-test/v2020.04.02"


class C7nCommands:
    @staticmethod
    def exec(command: str, config: C7nDefaults = C7nDefaults(), policies: Iterable[Path] = ()):
        def _new_cfg(policy):
            # TODO: Use account_id rather than profile name
            profile = config.profile if config.profile else "default"
            return replace(
                config,
                cache=str(Path(".cache", profile, policy.stem).with_suffix(".cache")),
                configs=[str(policy)],
                output_dir=str(Path("output", profile)),
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

    @classmethod
    def report(
            cls,
            config: C7nDefaults = C7nReportDefaults(),
            policies: Iterable[Union[Path, PathLike]] = (),
    ):
        """
        CURRENTLY NOT FUNCTIONAL!
        TODO: check for exec-option and override output_dir
        """
        cls.exec("report", config, policies)


def run(c7n_cmd: Optional[str] = None) -> Optional[str]:
    with TemporaryDirectory(prefix="c7n-") as tmpdir:
        PolicyProcessor.write_all(POLICY_MODE_FILE, tmpdir)
        invalid_policies = PolicyProcessor.get_invalid_all(tmpdir)
        if invalid_policies:
            return f"INVALID POLICIES:\n{yaml.safe_dump(invalid_policies)}"
        if c7n_cmd:
            getattr(C7nCommands, c7n_cmd)(policies=Path(tmpdir).rglob("*.yaml"))


def main() -> None:
    """ Main entry point """
    cli_params = _parser_params()
    sys.exit(run(cli_params.c7n_cmd))


if __name__ == "__main__":
    main()

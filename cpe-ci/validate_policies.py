#!/usr/bin/env python3
""" Validate c7n policies """
import logging
import sys
from os import PathLike, environ
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Sequence, Union

import c7n.commands
import yaml
from c7n.config import Config


logging.basicConfig(level=environ.get("CPE_LOGLEVEL", "warning").upper())
logging.getLogger("custodian").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__name__)

POLICY_MODE_FILE = Path(__file__).parents[1].joinpath("policy-modes.yaml")
POLICY_DIR = Path(__file__).parents[1].joinpath("policies")
MODE_DIR = Path(__file__).parents[1].joinpath("modes")


def _read_yaml(yaml_file: Union[Path, PathLike]) -> Dict[str, Sequence[Any]]:
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
    policy_files: Sequence[Union[Path, PathLike]],
    outdir: [Union[Path, PathLike]],
):
    mode_data = _read_yaml(Path(mode_file))
    for policyfile_ in policy_files:
        processed_policy = policy_with_mode(_read_yaml(Path(POLICY_DIR, policyfile_)), mode_data)
        policy_file = Path(outdir, policyfile_).with_suffix(".yaml")
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        policy_file.write_text(yaml.safe_dump(processed_policy))


def process_policies(policy_mode_file: Union[Path, PathLike], modedir: Union[Path, PathLike], outdir: Union[Path, PathLike]):
    policy_modes = _read_yaml(policy_mode_file)
    _ = [
        create_compiled_files(Path(modedir, key_), val_, outdir)
        for key_, val_ in policy_modes.items()
    ]


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


def get_invalid(policy_dir: Union[Path, PathLike]) -> Sequence[str]:
    return [
        str(pfile_.relative_to(policy_dir))
        for pfile_ in filter(
            lambda ppath_: not (is_valid(ppath_)), Path(policy_dir).rglob("*.yaml")
        )
    ]


def main() -> None:
    """ Main entry point """
    with TemporaryDirectory(prefix="c7n-") as tmpdir:
        process_policies(POLICY_MODE_FILE, MODE_DIR, tmpdir)
        invalid_policies = get_invalid(tmpdir)
    if invalid_policies:
        sys.exit(f"INVALID POLICIES:\n{yaml.safe_dump(invalid_policies)}")


if __name__ == "__main__":
    main()

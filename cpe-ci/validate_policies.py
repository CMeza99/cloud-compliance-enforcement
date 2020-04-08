#!/usr/bin/env python3
""" Validate c7n policies """
import logging
import sys
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Sequence, Union

import c7n.commands
import yaml
from c7n.config import Config


logging.basicConfig()
logging.getLogger("custodian").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__name__)

POLICY_DIR = Path(__file__).parents[1].joinpath("policies")
MODE_DIR = Path(__file__).parents[1].joinpath("policy.modes")
MODE_FILE = Path(MODE_DIR, "periodic.yml")


def _read_yaml(yaml_file: Union[Path, PathLike]) -> Dict[str, Sequence[Any]]:
    return yaml.safe_load(Path(yaml_file).read_text())


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
    policy_list = map(lambda policy_: dict(policy_, mode=mode_data), policy_data.get("policies"))
    return {"policies": list(policy_list)}


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
        _LOGGER.error("Invalid policy %s", policy_file.name)
    else:
        _LOGGER.info("Validated policy %s", policy_file.name)
        return True
    return False


def apply_mode_all(policy_dir: Union[Path, PathLike], outdir: Union[Path, PathLike], mode_data):
    for policy_file_ in Path(policy_dir).rglob("*.yaml"):
        processed_policy = apply_mode(_read_yaml(policy_file_), mode_data)
        tmpfile = Path(outdir, policy_file_.relative_to(policy_dir))
        tmpfile.parent.mkdir(parents=True, exist_ok=True)
        tmpfile.write_text(yaml.safe_dump(processed_policy))


def get_invalid(policy_dir: Union[Path, PathLike]) -> Sequence[str]:
    return [
        str(pfile_.relative_to(policy_dir))
        for pfile_ in filter(
            lambda ppath_: not (is_valid(ppath_)), Path(policy_dir).rglob("*.yaml")
        )
    ]


def main() -> None:
    """ Main entrypoint """
    with TemporaryDirectory(prefix="c7n-") as tmpdir:
        apply_mode_all(POLICY_DIR, tmpdir, _read_yaml(MODE_FILE))
        invalid_policies = get_invalid(tmpdir)
    if invalid_policies:
        sys.exit(f"INVALID POLICIES:\n{yaml.safe_dump(invalid_policies)}")


if __name__ == "__main__":
    main()

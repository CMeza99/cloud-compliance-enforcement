#!/usr/bin/env python3
""" Setuptools """

import sys

from pkg_resources import VersionConflict, require
from setuptools import setup


# Check for minimal version of setuptools
SETUPTOOLS_VER = "30.5.0"

try:
    require(f"setuptools>={SETUPTOOLS_VER}")
except VersionConflict:
    print(f"Error: version of setuptools is too old (<{SETUPTOOLS_VER})!")
    sys.exit(1)

setup(
    use_scm_version={"root": "..", "relative_to": __file__,}
)

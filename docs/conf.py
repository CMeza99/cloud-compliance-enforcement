# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata
from datetime import datetime
# from pathlib import Path

import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

_metadata = importlib.metadata.metadata("cpe_cmd")

project = _metadata.get("Summary")
author = _metadata.get("Author")
copyright = f"{datetime.now().year}, {author}"

# The short X.Y version
version = _metadata.get("Version")
# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.mermaid",
    "sphinx_rtd_theme",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

# templates_path = ["_templates"]
# exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_show_sphinx = False
html_static_path = ["_static"]
html_css_files = [
    "css/rtd_width.css",
]

# -- Extension configuration -------------------------------------------------

todo_include_todos = True
# intersphinx_mapping = {'https://docs.python.org/3/': None}
autodoc_default_options = {
    "members": None,
    "undoc-members": True,
    "inherited-members": True,
}
mermaid_version = "8.5.0"
# mermaid_output_format = "svg"
# mermaid_cmd = f"{Path(__file__).parent.parent.joinpath('node_modules','.bin', 'mmdc')}"
# mermaid_params = ['--backgroundColor', 'transparent']
# mermaid_verbose = True

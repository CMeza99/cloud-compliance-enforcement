# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata
import re
from datetime import datetime

# from pathlib import Path

import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

_metadata = importlib.metadata.metadata("cpe_cmd")

project = _metadata.get("Summary")
author = _metadata.get("Author")
copyright = f"{datetime.now().year}, {author}"

# The full version, including alpha/beta/rc tags
release = _metadata.get("Version")
# The short X.Y version
version = re.match(r"v?\d+(\.\d+)*", release)[0]


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.mermaid",
    "sphinx_rtd_theme",
    "recommonmark",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

# templates_path = ["_templates"]
# exclude_patterns = []

rst_epilog = "\n".join(
    [
        "\nBuild: |release|\n",
        ".. _Cloud Custodian: https://cloudcustodian.io/",
        f".. |project| replace:: {project}",
    ]
)

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_show_sphinx = False
html_static_path = ["_static"]
html_css_files = [
    "css/rtd_width.css",
    "css/mermaid_arch_diag.css",
]

# -- Extension configuration -------------------------------------------------

todo_include_todos = True
extlinks = {
    "c7n": ("https://github.com/cloud-custodian/cloud-custodian/%s", "GitHub"),
    "c7n_docs": ("https://cloudcustodian.io/docs/%s", "docs"),
}
autosectionlabel_prefix_document = True
autodoc_default_options = {
    "members": None,
    "undoc-members": True,
    "inherited-members": True,
    "autodoc_typehints": "description",
}
mermaid_version = "8.5.0"
# mermaid_output_format = "svg"
# mermaid_cmd = f"{Path(__file__).parent.parent.joinpath('node_modules','.bin', 'mmdc')}"
# mermaid_params = ['--backgroundColor', 'transparent']
# mermaid_verbose = True

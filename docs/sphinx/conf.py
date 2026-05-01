"""Sphinx configuration for the mortgagemath documentation site.

Builds the Read the Docs / Furo-themed reference at
https://mortgagemath.readthedocs.io/.

The rich vignettes (validation matrix, ARM walkthrough, payment caps,
Canadian j_2) are authored in Quarto and hosted at
https://murraystokely.github.io/mortgagemath/.  This Sphinx site
focuses on the reference material that Sphinx does well — installation,
quickstart, autodoc API reference, changelog — and links out to the
vignettes for everything else.
"""

from importlib.metadata import version as _pkg_version

# -- Project information -----------------------------------------------------

project = "mortgagemath"
author = "Murray Stokely"
copyright = "2026, Murray Stokely"

# Sourced from installed package metadata so the Sphinx site always
# reports the same version as `pip show` and the in-Python __version__.
release = _pkg_version("mortgagemath")
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_copybutton",
]

# Allow Markdown source files alongside reStructuredText so the changelog
# and other top-level docs can be included verbatim.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Top-level index, then standard sections.
master_doc = "index"

# Allow internal cross-references between pages.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Project-style language.
language = "en"

# -- Autodoc / napoleon ------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- MyST -------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "smartquotes",
]

# -- Intersphinx ------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- HTML output ------------------------------------------------------------

html_theme = "furo"
html_title = f"mortgagemath {release}"
html_static_path = ["_static"]
html_logo = "_static/mortgagemath.svg"
html_favicon = None

html_theme_options = {
    "source_repository": "https://github.com/murraystokely/mortgagemath/",
    "source_branch": "main",
    "source_directory": "docs/sphinx/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/murraystokely/mortgagemath",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-2x",
        },
    ],
    "sidebar_hide_name": False,
}

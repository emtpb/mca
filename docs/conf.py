import os
from pkg_resources import get_distribution
import sys

# Add source code directory to path (required for autodoc)
sys.path.insert(0, os.path.abspath('..'))


# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.imgmath',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
]

# Show members of modules/classes and parent classes by default
autodoc_default_options = {'members': True, 'show-inheritance': True}

# Set up napoleon for parsing Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True

# Configure remote documenation via intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']


# -- Project-specific configuration ------------------------------------
project = 'Multi Channel Analyzer'
copyright = "2019, Measurement Engineering Group"

# Get version number from git via setuptools_scm
release = get_distribution('mca').version
version = '.'.join(release.split('.')[:3])

today_fmt = '%Y-%m-%d'

# -- Options for HTML output -------------------------------------------

html_theme = 'sphinx_rtd_theme'

#html_theme_options = {}
#html_logo = None
#html_favicon = None

#html_static_path = ['_static']

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Output file base name for HTML help builder.
htmlhelp_basename = 'mcadoc'


# -- Options for LaTeX output ------------------------------------------

latex_engine = 'pdflatex'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

latex_documents = [
    ('index', 'mca.tex',
     'Multi Channel Analyzer Documentation',
     'Measurement Engineering Group', 'manual'),
]

# The name of an image file (relative to this directory) to place at
# the top of the title page.
#latex_logo = None

# If true, show page references after internal links.
#latex_show_pagerefs = False

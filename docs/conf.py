import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('../..'))

# Project information
project = 'Portfolio Optimization System'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0.0'

# Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme'
]

# Templates path
templates_path = ['_templates']

# The suffix of source filenames
source_suffix = '.rst'

# The master toctree document
master_doc = 'index'

# HTML theme
html_theme = 'sphinx_rtd_theme'

# Theme options
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True
}

# Output file base name for HTML help builder
htmlhelp_basename = 'PortfolioOptimizationSystemdoc'
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join('../../')))
sys.path.insert(0, os.path.abspath(os.path.abspath(os.path.join('..', '..', 'data', 'shop.db'))))



project = 'TG-BOT-ONLINE-SHOP'
copyright = '2025, Dedevshin A, Ilyushin Y, Alekseev A'
author = 'Dedevshin A, Ilyushin Y, Alekseev A'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', 
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]

auto_doc_default_options = {'autosummary': True}

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'classic'
html_theme = 'alabaster'


#!/bin/bash
pip install lxml beautifulsoup4 jupyterlab markdownify html2text
./scrape_python_modules.py
jupyter lab
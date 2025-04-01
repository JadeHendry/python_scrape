#!/bin/bash
pip install lxml beautifulsoup4 jupyterlab markdownify
./scrape_python_modules.py
jupyter lab
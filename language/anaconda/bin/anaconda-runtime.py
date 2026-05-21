# anaconda-runtime.py
# Project ANACONDA Secure Runtime Wrapper v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import sys
import os

# Align PYTHONPATH
sys.path.insert(0, r"C:\RegimeOS\language\anaconda")

from src.compiler import loader

if __name__ == "__main__":
    loader.main()

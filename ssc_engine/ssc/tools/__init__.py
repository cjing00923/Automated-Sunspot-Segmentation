"""
This is the data downloader and loader module.
"""
from os.path import dirname, basename, isfile
import glob

# Import all python script in this folder.
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
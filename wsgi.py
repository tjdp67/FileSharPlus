import sys
import os
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f'{basedir}')  # Replace with the actual path to your project

from app import app as application
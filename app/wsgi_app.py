"""wsgi module"""
from cold_ones import create_app
import sys
import os


PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PATH)

application = create_app()
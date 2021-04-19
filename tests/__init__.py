import os
import sys

# Allow "pytest tests" instead of "python -m pytest tests"
sys.path.insert(0, os.path.join(os.getcwd(), 'tests'))

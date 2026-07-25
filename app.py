import sys
import os

# Directly inject the root workspace path so Python can see the 'backend' folder
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import your frontend layout dynamically using Python's module importer
import importlib.util
spec = importlib.util.spec_from_file_location("frontend_app", os.path.join("frontend", "app.py"))
frontend_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend_app)

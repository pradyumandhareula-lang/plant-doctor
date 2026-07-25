import sys
import os

# Dynamically force Python to recognize the root folder from inside frontend/
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Your original code continues right below this line:
import streamlit as st
from backend.main import diagnose_plant

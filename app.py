"""Streamlit Cloud entry point — delegates to apps/streamlit_app.py."""
import os as _os
import runpy as _runpy

_app_path = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)), "apps", "streamlit_app.py"
)

_runpy.run_path(_app_path, run_name="__main__")

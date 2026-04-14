"""Streamlit Cloud entry point — delegates to apps/streamlit_app.py."""
import os as _os

_app_path = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)), "apps", "streamlit_app.py"
)

# Override __file__ so the delegate script resolves _REPO_ROOT correctly.
__file__ = _app_path  # noqa: A001

with open(_app_path) as _f:
    exec(compile(_f.read(), _app_path, "exec"))

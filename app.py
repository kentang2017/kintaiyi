"""Streamlit Cloud entry point — delegates to apps/streamlit_app.py."""

import os as _os
import sys as _sys

_repo_root = _os.path.dirname(_os.path.abspath(__file__))
_app_path = _os.path.join(_repo_root, "apps", "streamlit_app.py")

# Ensure the src directory is on sys.path so that kintaiyi can be imported
# when the package is not installed (e.g. on Streamlit Cloud).
_src_dir = _os.path.join(_repo_root, "src")
if _src_dir not in _sys.path:
    _sys.path.insert(0, _src_dir)

# Execute the delegate script with __file__ pointing at the real location
# so that _REPO_ROOT resolves correctly inside the delegate.
_globals = {**globals(), "__file__": _app_path}

with open(_app_path, encoding="utf-8") as _f:
    exec(compile(_f.read(), _app_path, "exec"), _globals)  # noqa: S102

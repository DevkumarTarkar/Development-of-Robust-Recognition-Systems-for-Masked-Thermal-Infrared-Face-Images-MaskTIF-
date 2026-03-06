"""Top-level configuration shim for MaskTIF.

This file exists to make imports like `from config import Config` resolve
correctly for linters and tooling when working from the project root.

The actual configuration class used by the backend lives in
`backend/config.py` and is re-exported here.
"""

from backend.config import Config  # re-export for convenience


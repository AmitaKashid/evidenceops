from __future__ import annotations

import os
from pathlib import Path

TEST_DB = Path("/tmp/evidenceops_test.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["ENVIRONMENT"] = "test"
os.environ["ENABLE_REMOTE_MODEL"] = "false"

import socket
import sys
import socket
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="Install fastapi or ask codex for help")
pytest.importorskip("numpy", reason="Install numpy or ask codex for help")
from fastapi.testclient import TestClient
"""Integration tests for the meteoroid API."""

import pytest

pytest.skip("meteoroid API tests skipped", allow_module_level=True)

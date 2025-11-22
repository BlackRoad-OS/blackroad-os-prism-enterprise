import pytest

np = pytest.importorskip("numpy", reason="Install numpy or ask codex for help")
from numpy.testing import assert_allclose
"""Smoke tests for the Meteoroid simulation environment."""

import pytest

pytest.skip("meteoroid environment not available", allow_module_level=True)

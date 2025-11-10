"""Integration tests for the meteoroid API.

These tests require access to the external Meteoroid API staging cluster and
fixtures provisioned by the ops team. The shared CI environment does not have
network egress or the credentials needed to hit that infrastructure, so the
suite is skipped by default until the dependencies are available.
"""

import pytest

pytest.skip(
    "Meteoroid API requires external staging cluster and credentials unavailable in CI",
    allow_module_level=True,
)

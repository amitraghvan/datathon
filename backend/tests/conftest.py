"""Pytest fixtures for FastAPI backend tests."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    """Create reusable FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client

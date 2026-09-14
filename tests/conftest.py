import pytest
from fastapi.testclient import TestClient

from madr.app import app


@pytest.fixture
def cliente():
    cliente = TestClient(app)
    return cliente

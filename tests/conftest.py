import pytest
import os
import sqlite3

# Set the DB path to a shared in-memory instance for testing
os.environ["DB_PATH"] = "file::memory:?cache=shared"

from app import createApp
from database import initDb

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    app = createApp(testing=True)
    with app.test_client() as c:
        with app.app_context():
            # Initialize and seed the in-memory database
            initDb(seed=True)
        yield c

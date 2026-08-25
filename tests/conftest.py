"""
Test setup. Points the app at an in-memory database and turns off CSRF
(so test form submissions don't need a token) BEFORE app.py is imported —
app.py reads these as environment variables when it creates the app.
"""
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['WTF_CSRF_ENABLED'] = 'False'

import pytest  # noqa: E402
from app import app as flask_app  # noqa: E402

flask_app.config['TESTING'] = True


@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

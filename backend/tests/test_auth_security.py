from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from pydantic import ValidationError

from app.auth import security
from app.config import Settings


class NoUserDb:
    def get(self, model, user_id):
        return None


class ShouldNotBeCalledDb:
    def get(self, model, user_id):
        raise AssertionError("DB lookup should not run for invalid token subject.")


def make_token(payload):
    return jwt.encode(payload, security.settings.secret_key, algorithm=security.settings.algorithm)


def assert_unauthorized(token, db=None):
    with pytest.raises(HTTPException) as exc:
        security.get_current_user(token=token, db=db or ShouldNotBeCalledDb())
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"


def test_expired_token_returns_401():
    token = make_token({"sub": "1", "exp": datetime.utcnow() - timedelta(minutes=1)})
    assert_unauthorized(token)


def test_missing_sub_returns_401():
    token = make_token({"exp": datetime.utcnow() + timedelta(minutes=5)})
    assert_unauthorized(token)


def test_non_integer_sub_returns_401():
    token = make_token({"sub": "not-an-int", "exp": datetime.utcnow() + timedelta(minutes=5)})
    assert_unauthorized(token)


def test_malformed_token_returns_401():
    assert_unauthorized("this-is-not-a-jwt")


def test_valid_token_for_missing_user_returns_401():
    token = make_token({"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=5)})
    assert_unauthorized(token, db=NoUserDb())


def test_production_rejects_default_secret():
    with pytest.raises(ValidationError, match="SECRET_KEY must be changed"):
        Settings(environment="production", secret_key="change-me-in-production")


def test_test_environment_allows_default_secret():
    settings = Settings(environment="test", secret_key="change-me-in-production")
    assert settings.secret_key == "change-me-in-production"

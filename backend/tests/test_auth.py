"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    resp = client.post("/api/auth/register", json={
        "username": "newuser1", "email": "newuser1@test.com", "password": "password123"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser1"
    assert data["email"] == "newuser1@test.com"
    assert "id" in data


def test_register_duplicate_username(client: TestClient, registered_user):
    resp = client.post("/api/auth/register", json={
        "username": "testuser", "email": "other@test.com", "password": "password123"
    })
    assert resp.status_code == 409


def test_register_duplicate_email(client: TestClient, registered_user):
    resp = client.post("/api/auth/register", json={
        "username": "otherusername", "email": "test@test.com", "password": "password123"
    })
    assert resp.status_code == 409


def test_register_short_password(client: TestClient):
    resp = client.post("/api/auth/register", json={
        "username": "shortpw", "email": "short@test.com", "password": "abc"
    })
    assert resp.status_code == 422


def test_login_success(client: TestClient, registered_user):
    resp = client.post("/api/auth/login", json={
        "username": "testuser", "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, registered_user):
    resp = client.post("/api/auth/login", json={
        "username": "testuser", "password": "wrongpassword"
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    resp = client.post("/api/auth/login", json={
        "username": "ghost", "password": "password123"
    })
    assert resp.status_code == 401


def test_get_profile_authenticated(client: TestClient, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"


def test_get_profile_unauthenticated(client: TestClient):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_get_profile_invalid_token(client: TestClient):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401

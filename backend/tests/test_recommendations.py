"""Tests for recommendations and ratings endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_popular_recommendations(client: TestClient):
    resp = client.get("/api/recommendations/popular")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_personal_recommendations_unauthenticated(client: TestClient):
    resp = client.get("/api/recommendations/personal")
    assert resp.status_code == 401


def test_personal_recommendations_authenticated(client: TestClient, auth_headers):
    resp = client.get("/api/recommendations/personal", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_similar_movies_not_found(client: TestClient):
    resp = client.get("/api/recommendations/similar/99999")
    assert resp.status_code == 404


def test_submit_rating_unauthenticated(client: TestClient):
    resp = client.post("/api/ratings", json={"movie_id": 1, "score": 4.0})
    assert resp.status_code == 401


def test_submit_rating_authenticated(client: TestClient, auth_headers):
    # Get a valid movie id first
    movies_resp = client.get("/api/movies?per_page=1")
    if movies_resp.json()["total"] == 0:
        pytest.skip("No movies in test DB")
    movie_id = movies_resp.json()["movies"][0]["id"]

    resp = client.post("/api/ratings", json={"movie_id": movie_id, "score": 4.0}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 4.0
    assert data["movie_id"] == movie_id


def test_submit_rating_invalid_score(client: TestClient, auth_headers):
    movies_resp = client.get("/api/movies?per_page=1")
    if movies_resp.json()["total"] == 0:
        pytest.skip("No movies in test DB")
    movie_id = movies_resp.json()["movies"][0]["id"]
    resp = client.post("/api/ratings", json={"movie_id": movie_id, "score": 6.0}, headers=auth_headers)
    assert resp.status_code == 422


def test_upsert_rating(client: TestClient, auth_headers):
    movies_resp = client.get("/api/movies?per_page=1")
    if movies_resp.json()["total"] == 0:
        pytest.skip("No movies in test DB")
    movie_id = movies_resp.json()["movies"][0]["id"]
    # First rating
    client.post("/api/ratings", json={"movie_id": movie_id, "score": 3.0}, headers=auth_headers)
    # Update rating
    resp = client.post("/api/ratings", json={"movie_id": movie_id, "score": 5.0}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["score"] == 5.0


def test_get_my_ratings(client: TestClient, auth_headers):
    resp = client.get("/api/ratings/my-ratings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "ratings" in data
    assert "total" in data


def test_retrain_non_admin(client: TestClient, auth_headers):
    resp = client.post("/api/recommendations/retrain", headers=auth_headers)
    assert resp.status_code == 403


def test_health_check(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

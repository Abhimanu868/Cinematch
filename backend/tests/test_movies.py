"""Tests for movies endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.movie import Movie


@pytest.fixture(scope="module")
def seed_test_movies(client: TestClient):
    """Seed a few movies into the test DB via the internal session."""
    from tests.conftest import TestingSessionLocal
    db: Session = TestingSessionLocal()
    movies = [
        Movie(title="Test Action Movie", genres="Action", overview="An action movie.", release_year=2020,
              vote_average=7.5, vote_count=100, popularity=50.0,
              poster_url="https://picsum.photos/seed/testaction/300/450"),
        Movie(title="Test Drama Film", genres="Drama", overview="A drama film.", release_year=2018,
              vote_average=8.0, vote_count=200, popularity=60.0,
              poster_url="https://picsum.photos/seed/testdrama/300/450"),
        Movie(title="Test Comedy Show", genres="Comedy, Romance", overview="A funny comedy.", release_year=2022,
              vote_average=6.5, vote_count=80, popularity=40.0,
              poster_url="https://picsum.photos/seed/testcomedy/300/450"),
    ]
    for m in movies:
        db.add(m)
    db.commit()
    db.close()
    yield
    db2: Session = TestingSessionLocal()
    db2.query(Movie).delete()
    db2.commit()
    db2.close()


def test_list_movies(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies")
    assert resp.status_code == 200
    data = resp.json()
    assert "movies" in data
    assert "total" in data
    assert data["total"] >= 3


def test_list_movies_pagination(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies?page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["movies"]) <= 2
    assert data["per_page"] == 2


def test_list_movies_genre_filter(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies?genre=Drama")
    assert resp.status_code == 200
    data = resp.json()
    for m in data["movies"]:
        assert "Drama" in m["genres"]


def test_search_movies(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies/search?q=action")
    assert resp.status_code == 200
    data = resp.json()
    assert "movies" in data
    assert "query" in data
    assert data["query"] == "action"


def test_search_movies_empty_query(client: TestClient):
    resp = client.get("/api/movies/search?q=")
    assert resp.status_code == 422


def test_trending_movies(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies/trending")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_movie_not_found(client: TestClient):
    resp = client.get("/api/movies/99999")
    assert resp.status_code == 404


def test_get_movie_by_id(client: TestClient, seed_test_movies):
    list_resp = client.get("/api/movies?per_page=1")
    movie_id = list_resp.json()["movies"][0]["id"]
    resp = client.get(f"/api/movies/{movie_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == movie_id


def test_get_genres(client: TestClient, seed_test_movies):
    resp = client.get("/api/movies/genres")
    assert resp.status_code == 200
    genres = resp.json()
    assert isinstance(genres, list)
    assert len(genres) > 0

# CineAI - Movie Recommendation System

A complete, production-ready Movie Recommendation System built with a Machine Learning backend, REST API, and a modern React frontend.

![CineAI Banner](https://picsum.photos/seed/cineai/1200/400)

## Features

- **Personalized Recommendations**: Uses AI to suggest movies you'll love based on your rating history.
- **Hybrid ML Engine**: Combines **Collaborative Filtering** (TruncatedSVD) and **Content-Based Filtering** (TF-IDF & Cosine Similarity).
- **Cinematic Frontend**: A stunning dark-mode UI built with React, Vite, and custom CSS.
- **Robust API**: Built with FastAPI, featuring JWT authentication, pagination, search, and more.
- **Ready to Deploy**: Fully dockerized with development and production `docker-compose` setups.

---

## Architecture / Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Machine Learning**: Scikit-learn (TruncatedSVD, TF-IDF, Cosine Similarity), Pandas, Numpy
- **Frontend**: React.js (Vite), React Router, Zustand (State Management), Axios
- **Deployment**: Docker, Nginx

---

## 🚀 Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.
- Or, Node.js v20+ and Python 3.11+ for local setup.

### Getting TMDB API Key
1. Go to https://www.themoviedb.org/settings/api
2. Register for a free account
3. Request an API key (free for non-commercial use)
4. Add it to your backend `.env` file as `TMDB_API_KEY` and frontend `.env` file as `VITE_TMDB_API_KEY`.

### Option 1: Docker (Recommended)

1. Clone or open the repository.
2. Run development environment:
   ```bash
   make dev
   # or
   docker-compose up
   ```
3. Visit the app at [http://localhost:5173](http://localhost:5173). The API is available at `http://localhost:8000`.

### Option 2: Local Setup (Without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Seed the database and train the models
python -c "from app.database import SessionLocal, init_db; from app.utils.seed_data import seed_movies_and_ratings; init_db(); db=SessionLocal(); print(seed_movies_and_ratings(db)); db.close()"
python -c "from app.database import SessionLocal; from app.ml.trainer import train_models; db=SessionLocal(); print(train_models(db)); db.close()"

uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🛠 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/register` | `POST` | Register a new user | No |
| `/api/auth/login` | `POST` | Get JWT token | No |
| `/api/movies` | `GET` | Paginated movie listing & filters | No |
| `/api/movies/search` | `GET` | Full-text search across titles/genres/cast | No |
| `/api/movies/trending` | `GET` | Top rated / popular movies | No |
| `/api/movies/{id}` | `GET` | Get detailed movie info | No |
| `/api/ratings` | `POST` | Submit a user rating (1-5) | **Yes** |
| `/api/recommendations/personal`| `GET` | Get personalized hybrid recommendations | **Yes** |
| `/api/recommendations/similar/{id}`| `GET`| Get content-based similar movies | No |
| `/api/recommendations/popular` | `GET` | Fallback popular recommendations | No |

*Note: The API has interactive Swagger docs available at `http://localhost:8000/docs`.*

---

## 🧠 How the ML Engine Works

1. **Content-Based Filtering**: We apply TF-IDF vectorization on movie text features (genres, overview, cast, keywords). When you look at a specific movie, we compute cosine similarity against the whole database to find the closest matches.
2. **Collaborative Filtering**: Uses Truncated SVD matrix factorization. We build a sparse matrix of users vs. movie ratings and extract latent features to predict how a user would rate unseen movies.
3. **Hybrid Recommender**: Blends both approaches. If a user has enough ratings, we weight predictions (60% Collaborative, 40% Content). If they are new (Cold Start), we fall back gracefully to purely content-based or popularity-based recommendations.

---

## 🧪 Testing

The backend includes a comprehensive pytest suite covering authentication, movie endpoints, and recommendation algorithms.

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🚢 Production Deployment

The project includes a `docker-compose.prod.yml` which serves the React frontend via Nginx and runs the FastAPI backend with Uvicorn workers.

```bash
make build
docker-compose -f docker-compose.prod.yml up -d
```

---

Enjoy discovering your next favorite movie with **CineAI**!

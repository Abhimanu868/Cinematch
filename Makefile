.PHONY: dev build test seed train stop

dev:
	docker-compose up

build:
	docker-compose -f docker-compose.prod.yml build

test:
	cd backend && python -m pytest tests/ -v

seed:
	cd backend && python -c "from app.database import SessionLocal, init_db; from app.utils.seed_data import seed_movies_and_ratings; init_db(); db=SessionLocal(); print(seed_movies_and_ratings(db)); db.close()"

train:
	cd backend && python -c "from app.database import SessionLocal; from app.ml.trainer import train_models; db=SessionLocal(); print(train_models(db)); db.close()"

stop:
	docker-compose down

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

setup: install-backend install-frontend
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env

# AegisNet Project Management

.PHONY: help build run stop clean dev-backend dev-frontend cli-install

help:
	@echo "AegisNet v3 — Enterprise AI Control Plane"
	@echo "----------------------------------------"
	@echo "build         - Build all Docker services"
	@echo "run           - Start all services with Docker Compose"
	@echo "stop          - Stop all Docker services"
	@echo "clean         - Remove Docker volumes and images"
	@echo "dev-backend   - Run Python backend locally (requires venv)"
	@echo "dev-frontend  - Run React frontend locally (requires node)"
	@echo "cli-install   - Install AegisNet CLI locally"

build:
	docker compose build

run:
	docker compose up -d

stop:
	docker compose down

clean:
	docker compose down -v --rmi all

dev-backend:
	cd backend && pip install -r requirements.txt && uvicorn main:app --reload

dev-worker:
	cd backend && python worker.py

dev-frontend:
	cd frontend && npm install && npm run dev

cli-install:
	pip install -e ./cli

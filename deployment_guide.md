# AegisNet v3 — Deployment & Troubleshooting Guide

## 🛠️ Production Deployment Options

### 1. Docker Compose (Recommended)
This is the easiest way to run the full stack (Gateway, Frontend, Workers, Redis, DB).

```bash
docker compose up -d --build
```

**Common Docker Issues:**
*   **"error during connect: open //./pipe/dockerDesktopLinuxEngine"**: This means **Docker Desktop is NOT running**. Please open the Docker Desktop application on your Windows PC and wait until the status bar turns green ("Running").
*   **"unable to get image"**: This happens if Docker Desktop is closed. Once you open Docker Desktop, the error will go away.

---

### 2. Manual/Local Setup (No Docker)
If you cannot use Docker, follow these steps in order:

#### A. Database & Redis
Ensure you have **PostgreSQL** and **Redis** installed and running on their default ports.

#### B. Backend (Python/FastAPI)
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Install all required libraries
pip install -r requirements.txt
uvicorn main:app --reload
```

#### C. Worker (Background Tasks)
In a *separate* terminal (but ensure venv is active):
```bash
cd backend
python worker.py
```

#### D. Frontend (React/Vite)
In a *third* terminal:
```bash
cd frontend
npm install
npm run dev
```

---

## 🧭 Troubleshooting FAQ

**Q: I get `ModuleNotFoundError: No module named 'rq'` when running the worker?**
**A:** You need to install the dependencies in your Python environment. Run `pip install -r requirements.txt` while your virtual environment is active.

**Q: `npm run dev` in the backend folder failed.**
**A:** The backend uses Python. Only run `npm` commands inside the `frontend` folder.

**Q: How do I test the API?**
**A:** Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger documentation.

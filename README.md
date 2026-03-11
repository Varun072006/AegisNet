# AegisNet — Local AI Control Plane

A universal AI control plane that sits between your applications and local AI models (Ollama, LMStudio, etc.).

```
Application → AegisNet → Local AI Models
```

AegisNet manages **model routing**, **cost optimization**, **performance monitoring**, **compliance logging**, and **vendor failover** — all through a single unified API.

---

## Architecture

```
                 ┌─────────────────┐
                 │   Application   │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │    AegisNet     │
                 │  Control Plane  │
                 └────────┬────────┘
                          │
        ┌─────────┬───────┼───────┬──────────┐
        ▼         ▼       ▼       ▼          ▼
    ┌────────┐ ┌───────┐ ┌──────┐ ┌────────┐
    │ Llama3 │ │Mistral│ │Qwen  │ │ Phi-3  │
    └────────┘ └───────┘ └──────┘ └────────┘
```

## Features

- **Smart Routing** — auto, cost-optimized, performance, or quality routing
- **Multi-Provider** — Route between different local models like Llama 3, Mistral, CodeLlama natively
- **Automatic Failover** — retries with next provider on failure
- **Compliance Logging** — full audit trail of every request
- **Real-time Analytics** — cost, latency, and usage dashboards
- **Interactive Playground** — test models through the dashboard

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd AegisNet
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** for the dashboard.

### 4. Docker (Alternative)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/chat` | POST | Send a chat request through the gateway |
| `/api/v1/models` | GET | List available providers and models |
| `/api/v1/logs` | GET | Query audit logs |
| `/api/v1/analytics` | GET | Get aggregated metrics |
| `/api/v1/health` | GET | Health check |

### Chat Example

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "routing_strategy": "auto"
  }'
```

---

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite, Recharts, Lucide Icons
- **Infrastructure**: Docker, Nginx

---

## Project Structure

```
AegisNet/
├── backend/
│   ├── adapters/          # AI provider adapters
│   ├── routes/            # API endpoints
│   ├── main.py            # FastAPI app
│   ├── gateway.py         # Core gateway logic
│   ├── router_engine.py   # Smart routing
│   ├── compliance.py      # Audit logging
│   └── observability.py   # Metrics collection
├── frontend/
│   ├── src/
│   │   ├── pages/         # Dashboard, Playground, Logs, Models, Analytics
│   │   ├── components/    # Sidebar, shared UI
│   │   └── api.js         # Backend API client
│   └── index.html
├── docker-compose.yml
└── .env.example
```

## License

MIT
# AegisNet

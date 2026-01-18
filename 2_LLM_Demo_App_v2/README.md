# LLM Demo App v2

A demonstration of an LLM pipeline with semantic search capabilities, featuring a FastAPI backend and Streamlit frontend.

## Architecture

This application uses a client-server architecture:
- **FastAPI Backend** (`api.py`): Provides REST API endpoints for tokenization, embedding generation, and vector search operations
- **Streamlit Frontend** (`streamlit_app.py`): A web UI that communicates with the backend via HTTP requests

The frontend is a pure HTTP client and does not execute backend logic directly.

## Setup

1. Install dependencies:
```bash
cd app
uv sync
```

## Launch Applications

⚠️ **Important**: Both the FastAPI backend and Streamlit frontend must be running for the application to work.

### Step 1: Start the FastAPI Backend

In the first terminal:
```bash
cd app
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

You can verify it's running by visiting: http://localhost:8000/health

### Step 2: Start the Streamlit Frontend

In a second terminal:
```bash
cd app
uv run streamlit run streamlit_app.py
```

The frontend will be available at: http://localhost:8501

**Note**: If the backend is not running, the frontend will display error messages indicating the backend is unavailable.

### Configuration

The frontend connects to the backend at `http://localhost:8000` by default. To use a different backend URL, set the `API_BASE_URL` environment variable:

```bash
export API_BASE_URL=http://your-backend-url:8000
uv run streamlit run streamlit_app.py
```

## Deployment

### Local Development
Nothing has changed for local development - you still need **2 separate terminals** (one for FastAPI, one for Streamlit).

### Production Deployment

**The architecture change makes deployment better and more flexible:**

**Before**: Frontend and backend were tightly coupled (frontend imported backend modules directly), which was problematic for deployment.

**Now**: Frontend and backend are properly decoupled and communicate only via HTTP. This enables:

1. **Separate deployment** - Deploy backend and frontend to different services/hosts
2. **Independent scaling** - Scale backend and frontend independently based on load
3. **Different hosting options** - Backend can be on one service (e.g., AWS ECS) while frontend is on another (e.g., Streamlit Cloud)
4. **API flexibility** - Backend can serve multiple clients (web, mobile, etc.)

### Deployment Options

**Option 1: Container Deployment**
- Backend: Deploy FastAPI as a container (Docker/Kubernetes) with ChromaDB persistence
- Frontend: Deploy Streamlit as a separate container or use Streamlit Cloud
- Set `API_BASE_URL` in the frontend container to point to the backend service URL

**Option 2: Platform Services**
- Backend: Deploy FastAPI to services like Railway, Render, AWS ECS/Fargate, or Google Cloud Run
- Frontend: Deploy Streamlit to Streamlit Cloud, Heroku, or similar
- Configure `API_BASE_URL` to the backend's public URL

**Option 3: Single Server (Simpler)**
- Run both services on the same server (but still as separate processes)
- Use a reverse proxy (nginx/traefik) to route traffic
- Backend on internal port, frontend accessible via public port

**Key Point**: Both services still need to run, but they can now be deployed separately and communicate over HTTP, making the architecture production-ready and scalable.

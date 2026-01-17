# LLM Demo App v2

## Launch Applications

### FastAPI Backend

```bash
cd app
uv sync
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Available at: http://localhost:8000

### Streamlit Frontend

```bash
cd app
uv sync
uv run streamlit run streamlit_app.py
```

Available at: http://localhost:8501

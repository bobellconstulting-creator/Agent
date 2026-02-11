web: uvicorn agent.main:app --host 0.0.0.0 --port ${PORT:-8080}
worker: python -m agent.worker_cli --loop --interval 2

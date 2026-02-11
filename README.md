# BuckGrid Agent (working baseline)

This repo is now a runnable baseline agent service designed to avoid the prior build/deploy failures.

## What is included

- FastAPI **API service** with required routes:
  - `GET /`
  - `GET /health`
  - `POST /webhook/telegram`
  - `POST /tasks`
  - `GET /tasks`
  - `GET /tasks/{id}`
  - `POST /manager/run-once`
- SQLite-backed task queue for simple, low-cost operation.
- Manager loop that processes queued tasks and dispatches to specialist workers.
- Policy guardrails (money/destructive/external_commitment => approval required).
- Worker CLI process for continuous execution (`worker` process).
- Dockerfile + Procfile for Railway/Render/Cloud Run style deployment.
- Basic pytest coverage for health endpoint, task lifecycle, and risk-gated approvals.

## Quickstart (local verification)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn agent.main:app --host 0.0.0.0 --port 8080
```

Then verify:

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code","objective":"Fix lint issue","risk_tags":[]}'
curl -X POST http://localhost:8080/manager/run-once
```

## Deploy (low-friction)

### Railway / Render

- Use `Procfile` to run:
  - `web` process for API
  - `worker` process for queue processing
- Set `PORT` automatically from platform.

### Cloud Run

- Build from `Dockerfile`.
- Expose container port `8080`.
- Keep API public for Telegram webhook endpoint.


## Build-failure hardening (important)

If your platform says **build failed**, check these first:

1. Runtime version must be Python **3.11+** (`.python-version` is included).
2. Dependencies are intentionally ranged (not over-pinned) to avoid index/mirror resolution failures.
3. If platform ignores `Procfile`, set start command manually:
   - web: `uvicorn agent.main:app --host 0.0.0.0 --port $PORT`
   - worker: `python -m agent.worker_cli --loop --interval 2`
4. Ensure `web` service is deployed (not worker-only).

## 404 fix checklist

If you still see `404`:

1. Confirm your deployed URL responds at `/health`.
2. Confirm Telegram webhook points to `/webhook/telegram`.
3. Confirm the running process is `web` service, not only `worker`.
4. Confirm app binds to `0.0.0.0:$PORT`.

## Security note

This is a baseline scaffold. Before production:

- add auth for non-webhook routes,
- move from SQLite to managed Postgres,
- store secrets in platform secret manager,
- add structured audit logs and alerts.

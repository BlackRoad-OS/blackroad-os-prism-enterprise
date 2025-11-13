import os
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel
import uvicorn
from agent import telemetry, jobs

app = FastAPI(title="BlackRoad API")

JETSON_HOST = os.getenv("JETSON_HOST", "jetson.local")
JETSON_USER = os.getenv("JETSON_USER", "jetson")
AUTH_TOKEN = os.getenv("AGENT_AUTH_TOKEN")

if not AUTH_TOKEN:
    raise RuntimeError("AGENT_AUTH_TOKEN environment variable must be set for the API service")


def require_bearer_token(authorization: str = Header(default="")):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


class JobRequest(BaseModel):
    command: str


@app.get("/status")
def status(_: None = Depends(require_bearer_token)):
    return {
        "target": {"host": JETSON_HOST, "user": JETSON_USER},
        "pi": telemetry.collect_local(),
        "jetson": telemetry.collect_remote(JETSON_HOST, JETSON_USER),
    }


@app.post("/run")
def run_job(req: JobRequest, _: None = Depends(require_bearer_token)):
    jobs.run_remote(JETSON_HOST, req.command, JETSON_USER)
    return {"ok": True, "command": req.command}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8080)

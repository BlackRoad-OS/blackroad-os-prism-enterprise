"""FastAPI endpoints for streaming local model tokens to the dashboard."""

from __future__ import annotations

import asyncio
import contextlib

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from . import models

app = FastAPI(title="BlackRoad Local Models")


@app.get("/models")
async def get_models() -> JSONResponse:
    """Return the available local models."""

    return JSONResponse({"models": models.list_local_models()})


@app.websocket("/ws/model")
async def ws_model(ws: WebSocket) -> None:
    """Stream llama.cpp output over the websocket connection."""

    await ws.accept()
    try:
        message = await ws.receive_json()
        model = message.get("model")
        prompt = message.get("prompt", "")
        try:
            n_predict = int(message.get("n", 128))
        except (TypeError, ValueError):
            n_predict = 128

        if not model:
            await ws.send_text("[error] model path missing")
            await ws.send_text("[[BLACKROAD_MODEL_DONE]]")
            return

        loop = asyncio.get_running_loop()
        done_event = asyncio.Event()

        def stream_tokens() -> None:
            try:
                for token in models.run_llama_stream(
                    model, prompt, n_predict=n_predict
                ):
                    send_future = asyncio.run_coroutine_threadsafe(
                        ws.send_text(token), loop
                    )
                    try:
                        send_future.result()
                    except WebSocketDisconnect:
                        break
            except Exception as stream_exc:  # pragma: no cover - defensive in thread
                asyncio.run_coroutine_threadsafe(
                    ws.send_text(f"[error] {stream_exc}"), loop
                ).result()
            finally:
                asyncio.run_coroutine_threadsafe(
                    ws.send_text("[[BLACKROAD_MODEL_DONE]]"), loop
                ).result()
                loop.call_soon_threadsafe(done_event.set)

        await asyncio.gather(asyncio.to_thread(stream_tokens), done_event.wait())
    except WebSocketDisconnect:
        return
    except Exception as exc:  # pragma: no cover - defensive; websocket lifecycle
        await ws.send_text(f"[error] {exc}")
        await ws.send_text("[[BLACKROAD_MODEL_DONE]]")
    finally:
        with contextlib.suppress(RuntimeError):
            await ws.close()

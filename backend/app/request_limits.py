"""Bound JSON requests without trusting Content-Length or logging user content."""

import asyncio

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RequestLimitsMiddleware:
    def __init__(self, app: ASGIApp, timeout_seconds: float, max_bytes: int):
        self.app = app
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not scope["path"].startswith("/api/"):
            await self.app(scope, receive, send)
            return
        response_started = False

        async def track_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        async def reject(status: int, code: str, message: str):
            response = JSONResponse(
                {"error": {"code": code, "message": message, "details": []}},
                status_code=status,
            )
            await response(scope, receive, send)

        async def process():
            # Buffer at most max_bytes before FastAPI parses JSON. Count streamed
            # chunks as well, so a missing or dishonest Content-Length cannot bypass it.
            if scope["method"] in {"POST", "PUT", "PATCH"}:
                headers = dict(scope["headers"])
                if headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower() != b"application/json":
                    await reject(415, "UNSUPPORTED_MEDIA_TYPE", "Only application/json requests are accepted; uploads are disabled.")
                    return
                body = bytearray()
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    chunk = message.get("body", b"")
                    if len(body) + len(chunk) > self.max_bytes:
                        await reject(413, "PAYLOAD_TOO_LARGE", "The request body exceeds the configured limit.")
                        return
                    body.extend(chunk)
                    if not message.get("more_body", False):
                        break
                delivered = False

                async def buffered_receive():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {"type": "http.request", "body": bytes(body), "more_body": False}
                    return await receive()

                await self.app(scope, buffered_receive, track_send)
            else:
                await self.app(scope, receive, track_send)

        try:
            await asyncio.wait_for(process(), timeout=self.timeout_seconds)
        except TimeoutError:
            if not response_started:
                await reject(504, "REQUEST_TIMEOUT", "The request timed out. Please retry.")

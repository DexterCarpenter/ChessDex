"""Local HTTP server: JSON API + static play UI."""

from __future__ import annotations

import json
import mimetypes
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from game.session import PlayMode, PlaySession

STATIC_DIR = Path(__file__).resolve().parent / "static"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

SESSION_HEADER = "X-Session-Id"
SESSION_IDLE_SECONDS = 3600


@dataclass
class _SessionEntry:
    session: PlaySession
    lock: threading.Lock = field(default_factory=threading.Lock)
    last_access: float = field(default_factory=time.monotonic)


_sessions: dict[str, _SessionEntry] = {}
_sessions_lock = threading.Lock()


def _prune_idle_sessions() -> None:
    cutoff = time.monotonic() - SESSION_IDLE_SECONDS
    with _sessions_lock:
        stale = [sid for sid, e in _sessions.items() if e.last_access < cutoff]
        for sid in stale:
            del _sessions[sid]


def _session_id_from(handler: BaseHTTPRequestHandler) -> str:
    raw = handler.headers.get(SESSION_HEADER, "").strip()
    if raw:
        return raw
    return str(uuid.uuid4())


def _get_entry(handler: BaseHTTPRequestHandler) -> _SessionEntry:
    _prune_idle_sessions()
    sid = _session_id_from(handler)
    with _sessions_lock:
        entry = _sessions.get(sid)
        if entry is None:
            entry = _SessionEntry(session=PlaySession())
            _sessions[sid] = entry
        entry.last_access = time.monotonic()
        return entry


def _json_response(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    data = json.dumps(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))


def _serve_file(handler: BaseHTTPRequestHandler, base_dir: Path, rel: str) -> None:
    if rel == "" or rel.endswith("/"):
        rel = "index.html"
    file_path = (base_dir / rel).resolve()
    if not str(file_path).startswith(str(base_dir.resolve())):
        handler.send_error(HTTPStatus.FORBIDDEN)
        return
    if not file_path.is_file():
        handler.send_error(HTTPStatus.NOT_FOUND)
        return
    content = file_path.read_bytes()
    mime, _ = mimetypes.guess_type(str(file_path))
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", mime or "application/octet-stream")
    handler.send_header("Content-Length", str(len(content)))
    handler.end_headers()
    handler.wfile.write(content)


class PlayUIHandler(BaseHTTPRequestHandler):
    """Serve /api/* JSON and static assets."""

    def log_message(self, format: str, *args: object) -> None:
        pass

    def _handle_api_error(self, exc: Exception) -> None:
        _json_response(
            self,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {"error": str(exc)},
        )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            try:
                entry = _get_entry(self)
                with entry.lock:
                    if path == "/api/state":
                        _json_response(
                            self,
                            HTTPStatus.OK,
                            entry.session.to_state(include_hint=True),
                        )
                        return
                    if path.startswith("/api/legal_moves"):
                        qs = parse_qs(urlparse(self.path).query)
                        sq = (qs.get("sq") or [""])[0]
                        _json_response(
                            self,
                            HTTPStatus.OK,
                            {"moves": entry.session.legal_moves_from(sq)},
                        )
                        return
                    _json_response(
                        self, HTTPStatus.NOT_FOUND, {"error": "Not found"}
                    )
            except Exception as exc:
                self._handle_api_error(exc)
            return
        if path.startswith("/assets/"):
            rel = path[len("/assets/") :].lstrip("/")
            self._serve_assets(rel)
            return
        self._serve_static(path if path != "/" else "/index.html")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        try:
            body = _read_json(self)
        except json.JSONDecodeError:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return

        try:
            entry = _get_entry(self)
            with entry.lock:
                session = entry.session

                if path == "/api/new":
                    mode_str = body.get("mode", PlayMode.HUMAN_WHITE.value)
                    try:
                        mode = PlayMode(mode_str)
                    except ValueError:
                        _json_response(
                            self,
                            HTTPStatus.BAD_REQUEST,
                            {"error": f"Unknown mode: {mode_str}"},
                        )
                        return
                    session.new_game(
                        mode=mode,
                        engine_depth=body.get("engine_depth"),
                        show_engine_hint=body.get("show_engine_hint"),
                    )
                    _json_response(
                        self,
                        HTTPStatus.OK,
                        session.to_state(include_hint=False),
                    )
                    return

                if path == "/api/move":
                    result = session.play_move(
                        body.get("from", ""),
                        body.get("to", ""),
                        body.get("promotion"),
                    )
                    status = (
                        HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
                    )
                    _json_response(
                        self,
                        status,
                        {
                            **result,
                            "state": session.to_state(include_hint=False),
                        },
                    )
                    return

                if path == "/api/undo":
                    ok = session.undo()
                    _json_response(
                        self,
                        HTTPStatus.OK,
                        {"ok": ok, "state": session.to_state(include_hint=False)},
                    )
                    return

                if path == "/api/engine_step":
                    result = session.engine_step()
                    status = (
                        HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
                    )
                    _json_response(
                        self,
                        status,
                        {
                            **result,
                            "state": session.to_state(include_hint=False),
                        },
                    )
                    return

                if path == "/api/config":
                    if "show_engine_hint" in body:
                        session.show_engine_hint = bool(body["show_engine_hint"])
                    if "engine_depth" in body:
                        session.engine_depth = max(
                            1, min(int(body["engine_depth"]), 8)
                        )
                    if "mode" in body:
                        try:
                            session.mode = PlayMode(body["mode"])
                        except ValueError:
                            _json_response(
                                self,
                                HTTPStatus.BAD_REQUEST,
                                {"error": f"Unknown mode: {body['mode']}"},
                            )
                            return
                    _json_response(
                        self,
                        HTTPStatus.OK,
                        session.to_state(include_hint=False),
                    )
                    return

                _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except Exception as exc:
            self._handle_api_error(exc)

    def _serve_static(self, url_path: str) -> None:
        rel = url_path.lstrip("/")
        _serve_file(self, STATIC_DIR, rel)

    def _serve_assets(self, rel: str) -> None:
        _serve_file(self, ASSETS_DIR, rel)


def run_server(host: str | None = None, port: int | None = None) -> None:
    host = host or os.environ.get("HOST", "127.0.0.1")
    port = port if port is not None else int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), PlayUIHandler)
    print(f"ChessDex play UI: http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()

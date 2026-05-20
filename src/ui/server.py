"""Local HTTP server: JSON API + static play UI."""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from game.session import PlayMode, PlaySession

STATIC_DIR = Path(__file__).resolve().parent / "static"

_session = PlaySession()


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


class PlayUIHandler(BaseHTTPRequestHandler):
    """Serve /api/* JSON and static assets."""

    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/state":
            _json_response(self, HTTPStatus.OK, _session.to_state())
            return
        if path.startswith("/api/legal_moves"):
            qs = parse_qs(urlparse(self.path).query)
            sq = (qs.get("sq") or [""])[0]
            _json_response(
                self,
                HTTPStatus.OK,
                {"moves": _session.legal_moves_from(sq)},
            )
            return
        self._serve_static(path if path != "/" else "/index.html")

    def do_POST(self) -> None:
        global _session
        path = urlparse(self.path).path
        try:
            body = _read_json(self)
        except json.JSONDecodeError:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return

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
            _session.new_game(
                mode=mode,
                engine_depth=body.get("engine_depth"),
                show_engine_hint=body.get("show_engine_hint"),
            )
            _json_response(self, HTTPStatus.OK, _session.to_state())
            return

        if path == "/api/move":
            result = _session.play_move(
                body.get("from", ""),
                body.get("to", ""),
                body.get("promotion"),
            )
            status = HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
            _json_response(self, status, {**result, "state": _session.to_state()})
            return

        if path == "/api/undo":
            ok = _session.undo()
            _json_response(self, HTTPStatus.OK, {"ok": ok, "state": _session.to_state()})
            return

        if path == "/api/engine_step":
            result = _session.engine_step()
            status = HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
            _json_response(self, status, {**result, "state": _session.to_state()})
            return

        if path == "/api/config":
            if "show_engine_hint" in body:
                _session.show_engine_hint = bool(body["show_engine_hint"])
            if "engine_depth" in body:
                _session.engine_depth = max(1, min(int(body["engine_depth"]), 8))
            if "mode" in body:
                try:
                    _session.mode = PlayMode(body["mode"])
                except ValueError:
                    _json_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        {"error": f"Unknown mode: {body['mode']}"},
                    )
                    return
            _json_response(self, HTTPStatus.OK, _session.to_state())
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def _serve_static(self, url_path: str) -> None:
        rel = url_path.lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel = "index.html"
        file_path = (STATIC_DIR / rel).resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())):
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
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

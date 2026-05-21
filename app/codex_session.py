from __future__ import annotations

from dataclasses import dataclass
import json
import os
import queue
import shutil
import subprocess
import threading
import time
from typing import Optional

from parser import StatusSnapshot


@dataclass
class _JsonRpcResponse:
    id: int
    result: dict


class CodexStatusPoller:
    def __init__(self, output_queue: queue.Queue[object], interval_seconds: int = 5) -> None:
        self.output_queue = output_queue
        self.interval_seconds = interval_seconds
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._proc: Optional[subprocess.Popen[str]] = None
        self._next_id = 1
        self._codex_command = self._resolve_codex_command()

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._restart_process()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._ensure_process()
                snapshot = self._poll_status()
                self.output_queue.put(snapshot)
            except Exception as exc:
                self.output_queue.put(exc)
                self._restart_process()

            self._stop.wait(self.interval_seconds)

    def _ensure_process(self) -> None:
        if self._proc and self._proc.poll() is None:
            return

        creationflags = 0
        startupinfo = None
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

        self._proc = subprocess.Popen(
            self._codex_command + ["app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
            startupinfo=startupinfo,
        )
        self._next_id = 1
        self._initialize()

    def _restart_process(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2)
            except Exception:
                self._proc.kill()
        self._proc = None

    def _resolve_codex_command(self) -> list[str]:
        override = os.environ.get("CODEX_WATCHER_COMMAND", "").strip()
        if override:
            return [override]

        candidates = [
            shutil.which("codex.cmd"),
            shutil.which("codex.exe"),
            shutil.which("codex"),
        ]
        for path in candidates:
            if path:
                return [path]

        raise RuntimeError(
            "Could not locate Codex CLI. Ensure it is installed and on PATH, "
            "or set CODEX_WATCHER_COMMAND to a full executable path."
        )

    def _initialize(self) -> None:
        req_id = self._send_request(
            "initialize",
            {"clientInfo": {"name": "codex-status-credits-watcher", "version": "0.1.0"}},
        )
        _ = self._wait_for_response(req_id, timeout=20)

    def _send_request(self, method: str, params: dict) -> int:
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("Codex app-server process not ready")

        req_id = self._next_id
        self._next_id += 1

        payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        self._proc.stdin.write(json.dumps(payload) + "\n")
        self._proc.stdin.flush()
        return req_id

    def _wait_for_response(self, req_id: int, timeout: int) -> _JsonRpcResponse:
        if not self._proc or not self._proc.stdout:
            raise RuntimeError("Codex app-server process not ready")

        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self._proc.stdout.readline()
            if not line:
                if self._proc.poll() is not None:
                    raise RuntimeError("Codex app-server exited")
                time.sleep(0.05)
                continue

            line = line.strip()
            if not line:
                continue

            obj = self._try_parse_json(line)
            if not obj:
                continue

            if obj.get("id") != req_id:
                continue

            if "error" in obj:
                message = obj["error"].get("message", "Unknown error")
                raise RuntimeError(f"Codex app-server error: {message}")

            result = obj.get("result")
            if not isinstance(result, dict):
                raise RuntimeError("Codex app-server returned invalid result payload")

            return _JsonRpcResponse(id=req_id, result=result)

        raise RuntimeError("Timed out waiting for Codex app-server response")

    def _try_parse_json(self, text: str) -> Optional[dict]:
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None

        if isinstance(value, dict):
            return value
        return None

    def _poll_status(self) -> StatusSnapshot:
        req_id = self._send_request("account/rateLimits/read", {})
        resp = self._wait_for_response(req_id, timeout=20)

        limits = resp.result.get("rateLimits")
        if not isinstance(limits, dict):
            raise RuntimeError("Missing rate limits in app-server response")

        primary = limits.get("primary") or {}
        secondary = limits.get("secondary") or {}
        credits = limits.get("credits") or {}

        used_5h = int(primary.get("usedPercent", 0))
        used_week = int(secondary.get("usedPercent", 0))

        left_5h = max(0, min(100, 100 - used_5h))
        left_week = max(0, min(100, 100 - used_week))

        reset_5h = self._format_reset_countdown(primary.get("resetsAt"))
        reset_week = self._format_reset_countdown(secondary.get("resetsAt"))
        balance_text = self._format_balance(credits)

        return StatusSnapshot(
            five_hour_percent=left_5h,
            five_hour_reset=f"resets in {reset_5h}",
            weekly_percent=left_week,
            weekly_reset=f"resets in {reset_week}",
            credit_balance_text=balance_text,
        )

    def _format_reset_countdown(self, value: object) -> str:
        if not isinstance(value, (int, float)):
            return "unknown"

        remaining = max(0, int(value - time.time()))
        days = remaining // 86400
        hours = (remaining % 86400) // 3600
        minutes = (remaining % 3600) // 60

        if days > 0:
            return f"{days}d+"

        parts: list[str] = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")

        if not parts:
            return "<1m"

        return " ".join(parts)

    def _format_balance(self, credits: dict) -> str:
        balance = credits.get("balance")
        unlimited = bool(credits.get("unlimited"))
        has_credits = bool(credits.get("hasCredits"))

        if unlimited:
            return "available"

        if isinstance(balance, (int, float)):
            return "available"

        if has_credits:
            return "available"

        return "not available"

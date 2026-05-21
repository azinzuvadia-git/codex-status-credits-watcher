from __future__ import annotations

import queue
import sys
import tkinter as tk
import webbrowser
import traceback
import msvcrt
import atexit
import tempfile
from datetime import datetime
from pathlib import Path

from codex_session import CodexStatusPoller
from parser import StatusSnapshot

WIDGET_WIDTH = 168
WIDGET_HEIGHT = 112
RADIUS = 10
HELP_URL = "https://azinzuvadia-git.github.io/codex-status-credits-watcher/help.html"
LOG_FILE = Path.home() / "codex-credits-watcher.log"
LOCK_FILE = Path(tempfile.gettempdir()) / "codex-credits-watcher.lock"


def _log_error(context: str, err: BaseException) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {context}: {err}\n")
            f.write("".join(traceback.format_exception(type(err), err, err.__traceback__)))
            f.write("\n")
    except OSError:
        # Never let logging itself crash the app.
        pass


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip: tk.Toplevel | None = None
        self.widget.bind("<Enter>", self._show)
        self.widget.bind("<Leave>", self._hide)

    def _show(self, _event: tk.Event) -> None:
        if self.tip:
            return
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        self.tip.geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip,
            text=self.text,
            bg="#172238",
            fg="#e8efff",
            padx=6,
            pady=3,
            font=("Segoe UI", 8),
            relief="solid",
            borderwidth=1,
            justify="left",
            wraplength=130,
        )
        label.pack()

    def _hide(self, _event: tk.Event) -> None:
        if self.tip:
            self.tip.destroy()
            self.tip = None


class StatusWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Codex Credits")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="#00ff00")
        self.root.wm_attributes("-transparentcolor", "#00ff00")

        self._drag_start_x = 0
        self._drag_start_y = 0
        self.last_5h_percent = 0
        self.last_wk_percent = 0
        self.version_text = self._load_version()
        self._topmost_counter = 0

        self.queue: queue.Queue[object] = queue.Queue()
        self.poller = CodexStatusPoller(self.queue)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDGET_WIDTH,
            height=WIDGET_HEIGHT,
            bg="#00ff00",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self._draw_shell()
        self._bind_drag()

    def _draw_shell(self) -> None:
        self._rounded_rect(2, 2, WIDGET_WIDTH - 2, WIDGET_HEIGHT - 2, RADIUS, fill="#101827", outline="#26324b")

        self.title_label = tk.Label(
            self.root,
            text="Codex",
            fg="#e8efff",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.title_label.place(x=10, y=10)

        self.balance_label = tk.Label(
            self.root,
            text="$ ?",
            fg="#a8b5cb",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.balance_label.place(x=56, y=10)

        self.close_label = tk.Label(
            self.root,
            text="X",
            fg="#91a4c6",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
            cursor="hand2",
        )
        self.close_label.place(x=WIDGET_WIDTH - 10, y=10, anchor="ne")
        self.close_label.bind("<Button-1>", self._on_close)

        self.help_label = tk.Label(
            self.root,
            text="?",
            fg="#91a4c6",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
            cursor="hand2",
        )
        self.help_label.place(x=WIDGET_WIDTH - 26, y=10, anchor="ne")
        self.help_label.bind("<Button-1>", self._open_help)

        self.line_5h = tk.Label(
            self.root,
            text="5h",
            fg="#dce7ff",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.line_5h.place(x=10, y=36)

        self.line_5h_reset = tk.Label(
            self.root,
            text="⏳ --",
            fg="#8ea3c7",
            bg="#101827",
            font=("Segoe UI", 9),
        )
        self.line_5h_reset.place(x=78, y=36)

        self.line_week = tk.Label(
            self.root,
            text="Wk",
            fg="#dce7ff",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.line_week.place(x=10, y=56)

        self.line_week_reset = tk.Label(
            self.root,
            text="⏳ --",
            fg="#8ea3c7",
            bg="#101827",
            font=("Segoe UI", 9),
        )
        self.line_week_reset.place(x=78, y=56)

        self.error_label = tk.Label(
            self.root,
            text="",
            fg="#ff8a98",
            bg="#101827",
            font=("Segoe UI", 8),
        )
        self.error_label.place(x=114, y=10)

        self.powered_label = tk.Label(
            self.root,
            text="Apoorva Consulting",
            fg="#7fb0ff",
            bg="#101827",
            font=("Segoe UI", 7, "underline"),
            cursor="hand2",
        )
        self.powered_label.place(x=WIDGET_WIDTH - 10, y=WIDGET_HEIGHT - 10, anchor="se")
        self.powered_label.bind("<Button-1>", lambda _e: webbrowser.open("https://www.zinzuvadia-online.com"))

        self._draw_battery_shells()
        self._attach_tooltips()

    def _draw_battery_shells(self) -> None:
        # 5h battery
        self.batt_5h_outer = self.canvas.create_rectangle(
            38, 42, 58, 50, outline="#d8e0ef", fill="", width=1
        )
        self.batt_5h_tip = self.canvas.create_rectangle(
            58, 45, 60, 48, outline="#d8e0ef", fill="#d8e0ef", width=1
        )
        self.batt_5h_fill = self.canvas.create_rectangle(
            39, 43, 57, 49, outline="", fill="#6de08a", width=0
        )
        self.batt_5h_hit = self.canvas.create_rectangle(
            38, 42, 60, 50, outline="", fill="", width=0
        )

        # Weekly battery
        self.batt_wk_outer = self.canvas.create_rectangle(
            38, 62, 58, 70, outline="#d8e0ef", fill="", width=1
        )
        self.batt_wk_tip = self.canvas.create_rectangle(
            58, 65, 60, 68, outline="#d8e0ef", fill="#d8e0ef", width=1
        )
        self.batt_wk_fill = self.canvas.create_rectangle(
            39, 63, 57, 69, outline="", fill="#6de08a", width=0
        )
        self.batt_wk_hit = self.canvas.create_rectangle(
            38, 62, 60, 70, outline="", fill="", width=0
        )

    def _rounded_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, fill: str, outline: str) -> None:
        points = [
            x1 + r,
            y1,
            x2 - r,
            y1,
            x2,
            y1,
            x2,
            y1 + r,
            x2,
            y2 - r,
            x2,
            y2,
            x2 - r,
            y2,
            x1 + r,
            y2,
            x1,
            y2,
            x1,
            y2 - r,
            x1,
            y1 + r,
            x1,
            y1,
        ]
        self.canvas.create_polygon(points, smooth=True, splinesteps=36, fill=fill, outline=outline, width=1)

    def _bind_drag(self) -> None:
        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)

    def _attach_tooltips(self) -> None:
        Tooltip(self.line_5h, "5h window\nCurrent quota band")
        Tooltip(self.line_5h_reset, "⏳ 5h reset timer\nTime left")
        Tooltip(self.line_week, "Weekly window\nCurrent quota band")
        Tooltip(self.line_week_reset, "⏳ Weekly reset timer\nTime left")
        Tooltip(self.balance_label, "$ credit status\n✓ available\n✕ unavailable\n? unknown")
        Tooltip(self.help_label, f"Version:\n{self.version_text}")
        self._bind_canvas_tooltip(self.batt_5h_outer, lambda: f"5h Quota\n{self.last_5h_percent}% left")
        self._bind_canvas_tooltip(self.batt_5h_fill, lambda: f"5h Quota\n{self.last_5h_percent}% left")
        self._bind_canvas_tooltip(self.batt_5h_hit, lambda: f"5h Quota\n{self.last_5h_percent}% left")
        self._bind_canvas_tooltip(self.batt_wk_outer, lambda: f"Wk Quota\n{self.last_wk_percent}% left")
        self._bind_canvas_tooltip(self.batt_wk_fill, lambda: f"Wk Quota\n{self.last_wk_percent}% left")
        self._bind_canvas_tooltip(self.batt_wk_hit, lambda: f"Wk Quota\n{self.last_wk_percent}% left")

    def _bind_canvas_tooltip(self, item_id: int, text_fn) -> None:
        state = {"tip": None}

        def on_enter(_event):
            if state["tip"]:
                return
            tip = tk.Toplevel(self.root)
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            x = self.root.winfo_pointerx() + 10
            y = self.root.winfo_pointery() + 10
            tip.geometry(f"+{x}+{y}")
            label = tk.Label(
                tip,
                text=text_fn(),
                bg="#172238",
                fg="#e8efff",
                padx=6,
                pady=3,
                font=("Segoe UI", 8),
                relief="solid",
                borderwidth=1,
                justify="left",
                wraplength=130,
            )
            label.pack()
            state["tip"] = tip

        def on_leave(_event):
            tip = state.get("tip")
            if tip:
                tip.destroy()
                state["tip"] = None

        self.canvas.tag_bind(item_id, "<Enter>", on_enter)
        self.canvas.tag_bind(item_id, "<Leave>", on_leave)

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event) -> None:
        x = self.root.winfo_pointerx() - self._drag_start_x
        y = self.root.winfo_pointery() - self._drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def _on_close(self, _event: tk.Event) -> None:
        self.stop()
        self.root.destroy()

    def _open_help(self, _event: tk.Event) -> None:
        webbrowser.open(HELP_URL)

    def _load_version(self) -> str:
        candidates: list[Path] = []
        # Dev mode candidate
        candidates.append(Path(__file__).resolve().parent.parent / "VERSION")
        # PyInstaller onefile/onedir bundled data candidate
        if hasattr(sys, "_MEIPASS"):
            candidates.append(Path(getattr(sys, "_MEIPASS")) / "VERSION")
        # EXE directory fallback
        candidates.append(Path(sys.executable).resolve().parent / "VERSION")

        for version_file in candidates:
            try:
                version = version_file.read_text(encoding="utf-8").strip()
                if version:
                    return version
            except OSError:
                continue
        return "unknown"

    def start(self) -> None:
        self.poller.start()
        self._tick()

    def stop(self) -> None:
        self.poller.stop()

    def _tick(self) -> None:
        try:
            while True:
                item = self.queue.get_nowait()
                if isinstance(item, StatusSnapshot):
                    try:
                        self._render_status(item)
                    except Exception as exc:
                        _log_error("render_status", exc)
                        self._render_error(exc)
                elif isinstance(item, Exception):
                    _log_error("poller_exception", item)
                    self._render_error(item)
        except queue.Empty:
            pass
        except Exception as exc:
            _log_error("tick_loop", exc)
            self._render_error(exc)

        # Reinforce topmost periodically (some Windows focus transitions can demote it).
        self._topmost_counter += 1
        if self._topmost_counter >= 8:  # ~2s with 250ms tick
            self._topmost_counter = 0
            try:
                self.root.attributes("-topmost", True)
                self.root.lift()
            except Exception as exc:
                _log_error("topmost_refresh", exc)

        self.root.after(250, self._tick)

    def _render_status(self, status: StatusSnapshot) -> None:
        self.error_label.configure(text="")
        self.last_5h_percent = status.five_hour_percent
        self.last_wk_percent = status.weekly_percent
        self._set_battery_level(self.batt_5h_fill, status.five_hour_percent, 39, 57, 43, 49)
        self._set_battery_level(self.batt_wk_fill, status.weekly_percent, 39, 57, 63, 69)
        self.line_5h_reset.configure(text=f"⏳ {status.five_hour_reset.removeprefix('resets in ')}")
        self.line_week_reset.configure(text=f"⏳ {status.weekly_reset.removeprefix('resets in ')}")
        if status.credit_balance_text == "available":
            self.balance_label.configure(text="$ ✓", fg="#7de2b8")
        elif status.credit_balance_text == "not available":
            self.balance_label.configure(text="$ ✕", fg="#ff7b8a")
        else:
            self.balance_label.configure(text="$ ?", fg="#a8b5cb")

    def _render_error(self, err: Exception) -> None:
        self.last_5h_percent = 0
        self.last_wk_percent = 0
        self._set_battery_level(self.batt_5h_fill, 0, 39, 57, 43, 49)
        self._set_battery_level(self.batt_wk_fill, 0, 39, 57, 63, 69)
        self.line_5h_reset.configure(text="⏳ unavailable")
        self.line_week_reset.configure(text="⏳ unavailable")
        self.error_label.configure(text="sync failed")
        self.balance_label.configure(text="$ ?", fg="#a8b5cb")

    def _set_battery_level(self, item_id: int, percent: int, x_left: int, x_right: int, y_top: int, y_bottom: int) -> None:
        p = max(0, min(100, percent))
        width = x_right - x_left
        fill_width = max(2, int(width * (p / 100.0))) if p > 0 else 0
        color = self._battery_color(p)

        if fill_width <= 0:
            self.canvas.coords(item_id, x_left, y_top, x_left, y_bottom)
            self.canvas.itemconfig(item_id, fill="")
            return

        self.canvas.coords(item_id, x_left, y_top, x_left + fill_width, y_bottom)
        self.canvas.itemconfig(item_id, fill=color)

    def _battery_color(self, percent: int) -> str:
        # Gradient from red (low) to green (high).
        p = max(0, min(100, percent)) / 100.0
        r = int(235 - (130 * p))
        g = int(72 + (150 * p))
        b = int(75 + (45 * p))
        return f"#{r:02x}{g:02x}{b:02x}"


def main() -> None:
    lock_handle = _acquire_single_instance_lock()
    if not lock_handle:
        return

    def _release_lock() -> None:
        try:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        try:
            lock_handle.close()
        except OSError:
            pass

    atexit.register(_release_lock)

    root = tk.Tk()
    app = StatusWindow(root)

    def _report_tk_exception(exc_type, exc_value, exc_traceback) -> None:
        err = exc_value if isinstance(exc_value, BaseException) else RuntimeError(str(exc_value))
        _log_error("tk_callback", err)
        app._render_error(err)

    root.report_callback_exception = _report_tk_exception

    def _on_close() -> None:
        app.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    app.start()
    root.mainloop()


def _acquire_single_instance_lock():
    try:
        lock_file = LOCK_FILE
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        fh = open(lock_file, "w")
        try:
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            fh.close()
            return None
        fh.write(str(Path(sys.executable)))
        fh.flush()
        return fh
    except OSError as exc:
        _log_error("single_instance_lock", exc)
        return None


if __name__ == "__main__":
    main()

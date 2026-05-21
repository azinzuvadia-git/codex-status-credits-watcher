from __future__ import annotations

import queue
import tkinter as tk

from codex_session import CodexStatusPoller
from parser import StatusSnapshot

WIDGET_WIDTH = 226
WIDGET_HEIGHT = 76
RADIUS = 10


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
            text="x",
            fg="#91a4c6",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
            cursor="hand2",
        )
        self.close_label.place(x=WIDGET_WIDTH - 16, y=10)
        self.close_label.bind("<Button-1>", self._on_close)

        self.line_5h = tk.Label(
            self.root,
            text="5h",
            fg="#dce7ff",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.line_5h.place(x=10, y=34)

        self.line_5h_reset = tk.Label(
            self.root,
            text="⏳ --",
            fg="#8ea3c7",
            bg="#101827",
            font=("Segoe UI", 9),
        )
        self.line_5h_reset.place(x=88, y=34)

        self.line_week = tk.Label(
            self.root,
            text="Wk",
            fg="#dce7ff",
            bg="#101827",
            font=("Segoe UI Semibold", 9),
        )
        self.line_week.place(x=10, y=52)

        self.line_week_reset = tk.Label(
            self.root,
            text="⏳ --",
            fg="#8ea3c7",
            bg="#101827",
            font=("Segoe UI", 9),
        )
        self.line_week_reset.place(x=88, y=52)

        self.error_label = tk.Label(
            self.root,
            text="",
            fg="#ff8a98",
            bg="#101827",
            font=("Segoe UI", 8),
        )
        self.error_label.place(x=148, y=10)

        self._draw_battery_shells()

    def _draw_battery_shells(self) -> None:
        # 5h battery
        self.batt_5h_outer = self.canvas.create_rectangle(
            32, 40, 52, 48, outline="#d8e0ef", fill="", width=1
        )
        self.batt_5h_tip = self.canvas.create_rectangle(
            52, 43, 54, 46, outline="#d8e0ef", fill="#d8e0ef", width=1
        )
        self.batt_5h_fill = self.canvas.create_rectangle(
            33, 41, 51, 47, outline="", fill="#6de08a", width=0
        )

        # Weekly battery
        self.batt_wk_outer = self.canvas.create_rectangle(
            32, 58, 52, 66, outline="#d8e0ef", fill="", width=1
        )
        self.batt_wk_tip = self.canvas.create_rectangle(
            52, 61, 54, 64, outline="#d8e0ef", fill="#d8e0ef", width=1
        )
        self.batt_wk_fill = self.canvas.create_rectangle(
            33, 59, 51, 65, outline="", fill="#6de08a", width=0
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
                    self._render_status(item)
                elif isinstance(item, Exception):
                    self._render_error(item)
        except queue.Empty:
            pass

        self.root.after(250, self._tick)

    def _render_status(self, status: StatusSnapshot) -> None:
        self.error_label.configure(text="")
        self._set_battery_level(self.batt_5h_fill, status.five_hour_percent, 33, 51, 41, 47)
        self._set_battery_level(self.batt_wk_fill, status.weekly_percent, 33, 51, 59, 65)
        self.line_5h_reset.configure(text=f"⏳ {status.five_hour_reset.removeprefix('resets in ')}")
        self.line_week_reset.configure(text=f"⏳ {status.weekly_reset.removeprefix('resets in ')}")
        if status.credit_balance_text == "available":
            self.balance_label.configure(text="$ ✓", fg="#7de2b8")
        elif status.credit_balance_text == "not available":
            self.balance_label.configure(text="$ ✕", fg="#ff7b8a")
        else:
            self.balance_label.configure(text="$ ?", fg="#a8b5cb")

    def _render_error(self, err: Exception) -> None:
        self._set_battery_level(self.batt_5h_fill, 0, 33, 51, 41, 47)
        self._set_battery_level(self.batt_wk_fill, 0, 33, 51, 59, 65)
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
    root = tk.Tk()
    app = StatusWindow(root)

    def _on_close() -> None:
        app.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    app.start()
    root.mainloop()


if __name__ == "__main__":
    main()

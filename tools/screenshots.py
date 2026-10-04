"""Drive the connected client (player "Claude") through camera positions and capture each view.

  python tools/screenshots.py shots.json out_dir
shots.json: [{"name": "aerial", "pos": [x, y, z], "look_at": [x, y, z], "wait": 6}, ...]
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import window as W  # noqa: E402
from mcmcp.engine import Engine  # noqa: E402

WM_KEYDOWN, WM_KEYUP = 0x0100, 0x0101


def post_key(hwnd: int, vk: int) -> None:
    """Send a key straight to the window's message queue (works without stealing focus)."""
    user32 = ctypes.windll.user32
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0x00000001)
    time.sleep(0.05)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0xC0000001)
    time.sleep(0.2)


def aim(pos, target) -> tuple[float, float]:
    dx, dy, dz = (target[i] - pos[i] for i in range(3))
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return round(yaw, 1), round(pitch, 1)


def main(spec_path: str, out_dir: str, player: str = "Claude") -> None:
    os.makedirs(out_dir, exist_ok=True)
    with open(spec_path, encoding="utf-8") as f:
        shots = json.load(f)
    e = Engine()
    hwnd = W.find_window()
    if not hwnd:
        raise SystemExit("Minecraft window not found")
    for c in ("gamemode spectator " + player, "time set 6000", "weather clear", "gamerule advance_time false",
              "gamerule advance_weather false", f"effect give {player} night_vision infinite 0 true"):
        e.cmd(c)
    hidden = False
    for s in shots:
        if "time" in s:
            e.cmd(f"time set {s['time']}")
        yaw, pitch = aim(s["pos"], s["look_at"])
        x, y, z = s["pos"]
        e.cmd(f"tp {player} {x} {y} {z} {yaw} {pitch}")
        time.sleep(s.get("wait", 5))
        if not hidden:
            post_key(hwnd, 0x70)  # F1: hide HUD
            hidden = True
            time.sleep(0.5)
        path = os.path.join(out_dir, f"{s['name']}.png")
        W.capture_background(hwnd, path)
        print("saved", path, "yaw", yaw, "pitch", pitch, flush=True)
    e.cmd("time set 6000")
    e.cmd("gamerule advance_time true")
    e.cmd("gamerule advance_weather true")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

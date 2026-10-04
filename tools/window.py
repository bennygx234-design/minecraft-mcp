"""Find, focus, capture and send keys to the Minecraft client window (Windows only)."""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import time

from PIL import ImageGrab

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32")
# 64-bit handles: declare pointer-sized types so they aren't truncated to int
user32.GetDC.restype = wt.HDC
user32.GetDC.argtypes = [wt.HWND]
user32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
user32.PrintWindow.argtypes = [wt.HWND, wt.HDC, wt.UINT]
gdi32.CreateCompatibleDC.restype = wt.HDC
gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
gdi32.CreateCompatibleBitmap.restype = wt.HBITMAP
gdi32.CreateCompatibleBitmap.argtypes = [wt.HDC, ctypes.c_int, ctypes.c_int]
gdi32.SelectObject.restype = wt.HGDIOBJ
gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
gdi32.GetDIBits.argtypes = [wt.HDC, wt.HBITMAP, wt.UINT, wt.UINT, ctypes.c_void_p, ctypes.c_void_p, wt.UINT]
gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
gdi32.DeleteDC.argtypes = [wt.HDC]
try:
    ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)  # real pixel coordinates on scaled displays
except Exception:
    pass


def find_window(title_prefix: str = "Minecraft") -> int | None:
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if buf.value.startswith(title_prefix) and "Launcher" not in buf.value:
                found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    return found[0] if found else None


def client_rect(hwnd: int) -> tuple[int, int, int, int]:
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    pt = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y, pt.x + r.right, pt.y + r.bottom


def focus(hwnd: int) -> None:
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    # Windows only lets the foreground process hand over focus; an Alt tap makes it allowed.
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)


def capture(hwnd: int, path: str) -> str:
    focus(hwnd)
    img = ImageGrab.grab(bbox=client_rect(hwnd), all_screens=True)
    img.save(path)
    return path


VK = {"F1": 0x70, "F2": 0x71, "F3": 0x72, "ESC": 0x1B, "ENTER": 0x0D, "TAB": 0x09, "SPACE": 0x20}


def press(hwnd: int, key: str) -> None:
    focus(hwnd)
    vk = VK[key]
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, 2, 0)
    time.sleep(0.2)


def click(hwnd: int, fx: float, fy: float) -> None:
    """Left-click at a fraction of the client area (0..1, 0..1)."""
    focus(hwnd)
    x1, y1, x2, y2 = client_rect(hwnd)
    user32.SetCursorPos(int(x1 + (x2 - x1) * fx), int(y1 + (y2 - y1) * fy))
    time.sleep(0.1)
    user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.3)



def capture_background(hwnd: int, path: str | None = None):
    """Capture the window's own pixels even when it is covered (PrintWindow + PW_RENDERFULLCONTENT)."""
    from PIL import Image
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    w, h = r.right, r.bottom
    hdc = user32.GetDC(hwnd)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(hwnd, mdc, 0x1 | 0x2)  # PW_CLIENTONLY | PW_RENDERFULLCONTENT
    class BMI(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                    ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                    ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                    ("biClrImportant", wt.DWORD)]
    bmi = BMI(ctypes.sizeof(BMI), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(hwnd, hdc)
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB")
    if path:
        img.save(path)
    return img


def title(hwnd: int) -> str:
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


if __name__ == "__main__":
    import sys
    h = find_window()
    print("hwnd", h)
    if h and len(sys.argv) > 1:
        print(capture(h, sys.argv[1]))

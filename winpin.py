import ctypes
from ctypes import wintypes
import win32con
import win32gui

def is_window_visible(hwnd):
    if not win32gui.IsWindow(hwnd):
        return False
    if not win32gui.IsWindowVisible(hwnd):
        return False
    ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if ex & win32con.WS_EX_TOOLWINDOW:
        return False
    title = win32gui.GetWindowText(hwnd)
    if not title.strip():
        return False
    return True

def enum_windows():
    res = []
    def cb(hwnd, _):
        if is_window_visible(hwnd):
            res.append({
                "hwnd": hwnd,
                "title": win32gui.GetWindowText(hwnd),
                "cls": win32gui.GetClassName(hwnd),
            })
    win32gui.EnumWindows(cb, None)
    res.sort(key=lambda x: x["title"].lower())
    return res

def get_foreground():
    return win32gui.GetForegroundWindow()

def _set_pos(hwnd, topmost=True):
    flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
    if topmost:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
    else:
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)

def set_topmost(hwnd, enable=True):
    if not win32gui.IsWindow(hwnd):
        return False
    _set_pos(hwnd, topmost=enable)
    return True

def is_topmost(hwnd):
    ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    return bool(ex & win32con.WS_EX_TOPMOST)

# hit-test по точке
user32 = ctypes.windll.user32
GA_ROOT = 2
GetAncestor = user32.GetAncestor
GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
GetAncestor.restype = wintypes.HWND

def hwnd_from_point(x, y):
    hwnd = win32gui.WindowFromPoint((x, y))
    if hwnd:
        root = GetAncestor(hwnd, GA_ROOT)
        if root:
            return int(root)
    return int(hwnd) if hwnd else 0

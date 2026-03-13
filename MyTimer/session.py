import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
wtsapi32 = ctypes.WinDLL("wtsapi32", use_last_error=True)

WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
NOTIFY_FOR_THIS_SESSION = 0

LRESULT = ctypes.c_long

WNDPROCTYPE = ctypes.WINFUNCTYPE(
    LRESULT,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)

class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROCTYPE),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]

def on_lock():
    print("Session locked")

def on_unlock():
    print("Session unlocked")

LRESULT = ctypes.c_long
@WNDPROCTYPE
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_WTSSESSION_CHANGE:
        if wparam == WTS_SESSION_LOCK:
            on_lock()
        elif wparam == WTS_SESSION_UNLOCK:
            on_unlock()

    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def main():
    h_instance = ctypes.windll.kernel32.GetModuleHandleW(None)
    class_name = "SessionListenerWindow"

    wnd_class = WNDCLASS()
    wnd_class.lpfnWndProc = wnd_proc
    wnd_class.hInstance = h_instance
    wnd_class.lpszClassName = class_name

    atom = user32.RegisterClassW(ctypes.byref(wnd_class))
    if not atom:
        raise ctypes.WinError(ctypes.get_last_error())

    hwnd = user32.CreateWindowExW(
        0,
        class_name,
        "Session Listener",
        0,
        0, 0, 0, 0,
        None, None, h_instance, None
    )
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())

    if not wtsapi32.WTSRegisterSessionNotification(hwnd, NOTIFY_FOR_THIS_SESSION):
        raise ctypes.WinError(ctypes.get_last_error())

    print("Lyssnar på session lock/unlock. Tryck Ctrl+C för att avsluta.")

    msg = MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    finally:
        wtsapi32.WTSUnRegisterSessionNotification(hwnd)

if __name__ == "__main__":
    main()
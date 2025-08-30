# src/overlay.py

import win32gui
import win32con
import win32api

class Overlay:
    """Creates a transparent, top-most window to draw the FOV box."""
    def __init__(self, x, y, width, height):
        self.window_name = "AimbotFOVOverlay"
        self.wc = win32gui.WNDCLASS()
        self.wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        self.wc.lpfnWndProc = self._wnd_proc
        self.wc.lpszClassName = self.window_name
        self.hwnd = None
        self.pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 0, 0))
        self.brush = win32gui.GetStockObject(win32con.BLACK_BRUSH)

        try:
            win32gui.RegisterClass(self.wc)
            self.hwnd = win32gui.CreateWindowEx(
                win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED,
                self.wc.lpszClassName, self.window_name, win32con.WS_POPUP,
                x, y, width, height, None, None, None, None
            )
            win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        except Exception as e:
            print(f"[!] Overlay Error: {e}")

    def _wnd_proc(self, hwnd, msg, w_param, l_param):
        if msg == win32con.WM_PAINT:
            hdc, paint_struct = win32gui.BeginPaint(hwnd)
            rect = win32gui.GetClientRect(hwnd)
            win32gui.FillRect(hdc, rect, self.brush)
            h_brush_hollow = win32gui.GetStockObject(win32con.NULL_BRUSH)
            win32gui.SelectObject(hdc, h_brush_hollow)
            win32gui.SelectObject(hdc, self.pen)
            win32gui.Rectangle(hdc, rect[0], rect[1], rect[2], rect[3])
            win32gui.EndPaint(hwnd, paint_struct)
            return 0
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, w_param, l_param)

    def update(self):
        """Process window messages to keep the overlay responsive."""
        if self.hwnd:
            win32gui.PumpWaitingMessages()

    def destroy(self):
        """Destroy the overlay window and unregister its class."""
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
        win32gui.UnregisterClass(self.wc.lpszClassName, None)
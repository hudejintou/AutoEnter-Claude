import ctypes
from ctypes import wintypes
import threading
import time
import tkinter as tk

# ── Windows API: 键盘模拟 ───────────────────────────────────
KEYEVENTF_KEYUP = 0x0002
VK_RETURN = 0x0D
INPUT_KEYBOARD = 1

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16),
        ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32), ("ki", KEYBDINPUT),
        ("padding", ctypes.c_ubyte * 8),
    ]

def press_enter():
    d = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_RETURN, dwFlags=0))
    u = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_RETURN, dwFlags=KEYEVENTF_KEYUP))
    sz = ctypes.sizeof(INPUT)
    ctypes.windll.user32.SendInput(1, ctypes.byref(d), sz)
    ctypes.windll.user32.SendInput(1, ctypes.byref(u), sz)

# ── Windows API: 全局热键 ───────────────────────────────────
MOD_ALT     = 0x0001
MOD_CONTROL = 0x0002
WM_HOTKEY   = 0x0312

HOTKEY_START = 1
HOTKEY_STOP  = 2

user32 = ctypes.windll.user32

def register_hotkeys(hwnd):
    """注册 Ctrl+Alt+1 和 Ctrl+Alt+2"""
    r1 = user32.RegisterHotKey(hwnd, HOTKEY_START, MOD_CONTROL | MOD_ALT, 0x31)  # 1
    r2 = user32.RegisterHotKey(hwnd, HOTKEY_STOP,  MOD_CONTROL | MOD_ALT, 0x32)  # 2
    return r1 != 0 and r2 != 0

def unregister_hotkeys(hwnd):
    user32.UnregisterHotKey(hwnd, HOTKEY_START)
    user32.UnregisterHotKey(hwnd, HOTKEY_STOP)

# PeekMessage 结构
class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
    ]

PM_REMOVE = 0x0001

# ── 色彩 ─────────────────────────────────────────────────────
BG       = "#0d1117"
CARD     = "#161b22"
BORDER   = "#30363d"
ACCENT   = "#58a6ff"
GREEN    = "#3fb950"
RED      = "#f85149"
GREY_BTN = "#21262d"
GREY_TXT = "#484f58"
TEXT     = "#c9d1d9"
TEXT2    = "#8b949e"
INPUT_BG = "#0d1117"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoEnter")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.running = False
        self.count = 0

        w, h = 340, 320
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x, y = (ws - w) // 2, (hs - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)

        # ── 注册全局热键 ──
        self.hwnd = int(root.frame(), 16)  # tkinter 窗口句柄
        if not register_hotkeys(self.hwnd):
            print("热键注册失败（可能已被占用）")

        # ── 自绘标题栏 ──
        self.title_bar = tk.Frame(root, bg="#0d1117", height=36)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)

        title_lbl = tk.Label(self.title_bar, text="  AutoEnter", bg="#0d1117", fg=TEXT2,
                             font=("Segoe UI", 10))
        title_lbl.pack(side=tk.LEFT)

        close_btn = tk.Label(self.title_bar, text="✕", bg="#0d1117", fg=TEXT2,
                             font=("Segoe UI", 12), padx=14, pady=2)
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg=RED, fg="#fff"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#0d1117", fg=TEXT2))

        # 拖拽窗口
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        title_lbl.bind("<Button-1>", self.start_drag)
        title_lbl.bind("<B1-Motion>", self.do_drag)

        # ── 主体 ──
        self.body = tk.Frame(root, bg=BG, padx=20, pady=12)
        self.body.pack(fill=tk.BOTH, expand=True)

        # 图标 + 标题
        self.header = tk.Frame(self.body, bg=BG)
        self.header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(self.header, text="⏎", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 28)).pack(side=tk.LEFT, padx=(0, 10))
        header_text = tk.Frame(self.header, bg=BG)
        header_text.pack(side=tk.LEFT)
        tk.Label(header_text, text="Auto Enter", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)
        tk.Label(header_text, text="自动按键 · 后台运行", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(anchor=tk.W)

        # ── 间隔设置卡片 ──
        card = tk.Frame(self.body, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill=tk.X, pady=(0, 12))

        card_inner = tk.Frame(card, bg=CARD, padx=14, pady=12)
        card_inner.pack(fill=tk.X)

        tk.Label(card_inner, text="回车间隔", bg=CARD, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(anchor=tk.W)

        input_row = tk.Frame(card_inner, bg=CARD)
        input_row.pack(fill=tk.X, pady=(6, 0))

        self.interval_var = tk.DoubleVar(value=10)
        self.interval_entry = tk.Entry(input_row, textvariable=self.interval_var,
                                       bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                                       font=("Segoe UI", 20, "bold"), width=5,
                                       bd=0, highlightthickness=1,
                                       highlightbackground=BORDER,
                                       highlightcolor=ACCENT,
                                       justify=tk.CENTER)
        self.interval_entry.pack(side=tk.LEFT)

        tk.Label(input_row, text="  秒/次", bg=CARD, fg=TEXT2,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT)

        preset_frame = tk.Frame(input_row, bg=CARD)
        preset_frame.pack(side=tk.RIGHT)
        for val, label in [(5, "5s"), (10, "10s"), (30, "30s")]:
            btn = tk.Label(preset_frame, text=label, bg="#21262d", fg=TEXT2,
                          font=("Segoe UI", 8), padx=8, pady=3)
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, v=val: self.set_interval(v))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#30363d", fg=TEXT))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#21262d", fg=TEXT2))

        # ── 控制按钮 ──
        btn_frame = tk.Frame(self.body, bg=BG)
        btn_frame.pack(fill=tk.X, pady=(0, 12))

        # 开始按钮 - 初始绿色
        self.start_btn = tk.Frame(btn_frame, bg=GREEN)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.start_lbl = tk.Label(self.start_btn, text="▶  开始运行", bg=GREEN, fg="#fff",
                                  font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        self.start_lbl.pack()
        self.start_lbl.bind("<Button-1>", lambda e: self.start())

        # 停止按钮 - 初始灰色
        self.stop_btn = tk.Frame(btn_frame, bg=GREY_BTN)
        self.stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        self.stop_lbl = tk.Label(self.stop_btn, text="■  停止", bg=GREY_BTN, fg=GREY_TXT,
                                 font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        self.stop_lbl.pack()
        self.stop_lbl.bind("<Button-1>", lambda e: self.stop())

        # ── 快捷键提示 ──
        hint_frame = tk.Frame(self.body, bg=BG)
        hint_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(hint_frame, text="Ctrl+Alt+1 开始    Ctrl+Alt+2 停止", bg=BG, fg="#30363d",
                 font=("Segoe UI", 8)).pack()

        # ── 状态栏 ──
        status_frame = tk.Frame(self.body, bg=CARD, highlightthickness=1,
                                highlightbackground=BORDER)
        status_frame.pack(fill=tk.X)

        status_inner = tk.Frame(status_frame, bg=CARD, padx=14, pady=10)
        status_inner.pack(fill=tk.X)

        self.status_dot = tk.Canvas(status_inner, width=8, height=8, bg=CARD,
                                    highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8))
        self._draw_dot("#30363d")

        self.status_var = tk.StringVar(value="等待启动")
        tk.Label(status_inner, textvariable=self.status_var, bg=CARD, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.count_var = tk.StringVar(value="")
        tk.Label(status_inner, textvariable=self.count_var, bg=CARD, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # ── 启动热键消息轮询 ──
        self._poll_hotkeys()

    def _poll_hotkeys(self):
        """轮询 WM_HOTKEY 消息"""
        msg = MSG()
        while user32.PeekMessageW(ctypes.byref(msg), self.hwnd, WM_HOTKEY, WM_HOTKEY, PM_REMOVE):
            if msg.message == WM_HOTKEY:
                if msg.wParam == HOTKEY_START:
                    self.start()
                elif msg.wParam == HOTKEY_STOP:
                    self.stop()
        self.root.after(50, self._poll_hotkeys)

    def _draw_dot(self, color):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill=color, outline="")

    def set_interval(self, val):
        self.interval_var.set(val)

    def loop(self, interval):
        while self.running:
            time.sleep(interval)
            if not self.running:
                break
            press_enter()
            self.count += 1
            self.root.after(0, self._update_count)

    def _update_count(self):
        self.count_var.set(f"已按 {self.count} 次")

    def start(self):
        if self.running:
            return
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            self.status_var.set("请输入有效正数")
            return
        self.running = True
        self.count = 0
        self.interval_entry.configure(state=tk.DISABLED)

        # 开始按钮(含Frame) -> 灰色  停止按钮(含Frame) -> 红色
        self.start_btn.configure(bg=GREY_BTN)
        self.start_lbl.configure(bg=GREY_BTN, fg=GREY_TXT, text="▶  开始运行")
        self.stop_btn.configure(bg=RED)
        self.stop_lbl.configure(bg=RED, fg="#fff", text="■  停止")

        self.status_var.set("运行中 · 可切换窗口")
        self._draw_dot(GREEN)
        self.count_var.set("")
        self.thread = threading.Thread(target=self.loop, args=(interval,), daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.interval_entry.configure(state=tk.NORMAL)

        # 开始按钮(含Frame) -> 绿色  停止按钮(含Frame) -> 灰色
        self.start_btn.configure(bg=GREEN)
        self.start_lbl.configure(bg=GREEN, fg="#fff", text="▶  开始运行")
        self.stop_btn.configure(bg=GREY_BTN)
        self.stop_lbl.configure(bg=GREY_BTN, fg=GREY_TXT, text="■  停止")

        self.status_var.set("已停止")
        self._draw_dot("#30363d")
        self.count_var.set(f"共按 {self.count} 次")

    def on_close(self):
        self.running = False
        unregister_hotkeys(self.hwnd)
        self.root.destroy()

    def start_drag(self, event):
        self._x = event.x
        self._y = event.y

    def do_drag(self, event):
        dx = event.x - self._x
        dy = event.y - self._y
        self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

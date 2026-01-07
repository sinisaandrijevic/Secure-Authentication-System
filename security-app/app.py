import tkinter as tk
from tkinter import messagebox
import re
import auth
from download_utils import download_db

THEME = {
    "bg": "#070b1e",
    "panel": "#0e1435",
    "panel2": "#11184a",
    "text": "#e6f0ff",
    "muted": "#aab3e6",
    "border": "#1f2a66",
    "accent": "#00d4ff",
    "accent2": "#b34cff",
    "success": "#2cffb0",
    "danger": "#ff4a4a",
    "warn": "#ff4fd8",
    "btn_text": "#001018",
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "h2": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_b": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 9),
}

APP_W, APP_H = 560, 740
CARD_W, CARD_H = 520, 700

def center_window(win: tk.Tk, w: int, h: int):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def is_blank(s: str) -> bool:
    return not s or not s.strip()

def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))

def safe_msg(kind: str, title: str, text: str):
    if kind == "info":
        messagebox.showinfo(title, text)
    elif kind == "warn":
        messagebox.showwarning(title, text)
    else:
        messagebox.showerror(title, text)

def bind_enter(widget: tk.Widget, fn):
    widget.bind("<Return>", lambda _e: fn())

def bind_escape(widget: tk.Widget, fn):
    widget.bind("<Escape>", lambda _e: fn())

def set_focus(widget: tk.Widget):
    try:
        widget.focus_set()
    except Exception:
        pass

def password_strength(pw: str):
    score = 0
    suggestions = []

    if len(pw) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters.")

    if any(c.islower() for c in pw) and any(c.isupper() for c in pw):
        score += 1
    else:
        suggestions.append("Mix uppercase and lowercase letters.")

    if any(c.isdigit() for c in pw):
        score += 1
    else:
        suggestions.append("Add at least one number.")

    if any(c in "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|" for c in pw):
        score += 1
    else:
        suggestions.append("Add at least one symbol.")

    labels = ["Very weak", "Weak", "Okay", "Good", "Strong"]
    return labels[score], score, suggestions

def strength_color(score: int) -> str:
    if score <= 1:
        return THEME["danger"]
    if score == 2:
        return THEME["warn"]
    if score == 3:
        return THEME["accent2"]
    return THEME["success"]

def username_is_reasonable(u: str) -> bool:
    # 3..32 chars, letters numbers underscore dot hyphen
    if len(u) < 3 or len(u) > 32:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", u))

def normalize_mode_value(v: str) -> str:
    return "demo" if v == "demo" else "secure"


# ==================================================================================================
# WIDGETS
# ==================================================================================================

class Divider(tk.Frame):
    def __init__(self, parent, pady=12):
        super().__init__(parent, bg=THEME["panel"])
        self.pack(fill="x", pady=pady)
        tk.Frame(self, height=1, bg=THEME["border"]).pack(fill="x")

class NeonEntry(tk.Entry):
    def __init__(self, parent, show=None):
        super().__init__(
            parent,
            bg=THEME["panel2"],
            fg=THEME["text"],
            insertbackground=THEME["accent"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
            font=FONTS["body"],
        )
        if show is not None:
            self.configure(show=show)

class NeonButton(tk.Button):
    def __init__(self, parent, text, command, accent):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=accent,
            fg=THEME["btn_text"],
            activebackground=accent,
            activeforeground=THEME["btn_text"],
            font=FONTS["body_b"],
            bd=0,
            padx=16,
            pady=10,
            cursor="hand2",
        )

class GhostButton(tk.Button):
    def __init__(self, parent, text, command, fg):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=THEME["panel"],
            fg=fg,
            activebackground=THEME["panel"],
            activeforeground=fg,
            font=FONTS["body"],
            bd=0,
            cursor="hand2",
        )

class PillTabs(tk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent, bg=THEME["panel"])
        self.on_select = on_select
        self.active = tk.StringVar(value="login")

        self.btn_login = tk.Button(
            self, text="LOGIN", bd=0, cursor="hand2",
            font=FONTS["body_b"], padx=14, pady=8,
            command=lambda: self.select("login")
        )
        self.btn_register = tk.Button(
            self, text="REGISTER", bd=0, cursor="hand2",
            font=FONTS["body_b"], padx=14, pady=8,
            command=lambda: self.select("register")
        )

        self.btn_login.pack(side="left")
        self.btn_register.pack(side="left", padx=(10, 0))
        self._apply_styles()

    def select(self, tab: str):
        tab = "register" if tab == "register" else "login"
        self.active.set(tab)
        self._apply_styles()
        self.on_select(tab)

    def _apply_styles(self):
        # Active looks like filled chip; inactive blends into panel
        if self.active.get() == "login":
            self.btn_login.configure(bg=THEME["panel2"], fg=THEME["accent"])
            self.btn_register.configure(bg=THEME["panel"], fg=THEME["muted"])
        else:
            self.btn_register.configure(bg=THEME["panel2"], fg=THEME["accent2"])
            self.btn_login.configure(bg=THEME["panel"], fg=THEME["muted"])

class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["panel"])
        self.msg = tk.StringVar(value="")
        self.label = tk.Label(self, textvariable=self.msg, bg=THEME["panel"], fg=THEME["muted"], font=FONTS["small"])
        self.label.pack(side="left")

    def set(self, text: str):
        self.msg.set(text)

class Toast(tk.Toplevel):
    def __init__(self, parent, text, kind="info"):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=THEME["panel"])

        fg = THEME["text"]
        if kind == "success":
            fg = THEME["success"]
        elif kind == "danger":
            fg = THEME["danger"]
        elif kind == "warn":
            fg = THEME["warn"]

        frame = tk.Frame(self, bg=THEME["panel"], highlightthickness=1, highlightbackground=THEME["border"])
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=text, bg=THEME["panel"], fg=fg, font=FONTS["body_b"], padx=12, pady=10).pack()

        self.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() - self.winfo_width() - 25
        y = parent.winfo_rooty() + parent.winfo_height() - self.winfo_height() - 25
        self.geometry(f"+{x}+{y}")
        self.after(2200, self.destroy)


# ==================================================================================================
# SCREENS
# ==================================================================================================

class ScreenBase(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["panel"])
        self.app = app

    def on_show(self):
        pass


class LoginScreen(ScreenBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        tk.Label(self, text="Login", bg=THEME["panel"], fg=THEME["text"], font=FONTS["h2"]).pack(anchor="w")

        Divider(self, pady=10)

        tk.Label(self, text="Username", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body"]).pack(anchor="w")
        self.username = NeonEntry(self)
        self.username.pack(fill="x", pady=(6, 12))

        tk.Label(self, text="Password", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body"]).pack(anchor="w")
        self.password = NeonEntry(self, show="*")
        self.password.pack(fill="x", pady=(6, 8))

        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self,
            text="Show password",
            variable=self.show_pw_var,
            command=self._toggle_pw,
            bg=THEME["panel"],
            fg=THEME["muted"],
            activebackground=THEME["panel"],
            activeforeground=THEME["text"],
            selectcolor=THEME["panel"],
            font=FONTS["body"],
        ).pack(anchor="w", pady=(0, 10))

        Divider(self, pady=10)

        tk.Label(self, text="Authentication mode", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body_b"]).pack(anchor="w")

        self.mode = tk.StringVar(value="secure")
        self._radio("Secure (parameterized queries)", "secure")
        self._radio("Demo (SQL Injection enabled)", "demo")

        Divider(self, pady=14)

        NeonButton(self, "LOGIN", self._login, accent=THEME["accent"]).pack(fill="x")

        row = tk.Frame(self, bg=THEME["panel"])
        row.pack(fill="x", pady=(12, 0))
        # GhostButton(row, "Create account →", self.app.show_register, fg=THEME["accent2"]).pack(side="right")

        bind_enter(self.username, self._login)
        bind_enter(self.password, self._login)
        bind_escape(self, self._clear)

    def _radio(self, text, value):
        tk.Radiobutton(
            self,
            text=text,
            variable=self.mode,
            value=value,
            bg=THEME["panel"],
            fg=THEME["text"],
            selectcolor=THEME["panel"],
            activebackground=THEME["panel"],
            activeforeground=THEME["text"],
            font=FONTS["body"],
        ).pack(anchor="w", pady=2)

    def _toggle_pw(self):
        self.password.configure(show="" if self.show_pw_var.get() else "*")

    def _clear(self):
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.caps_hint.configure(text="")
        set_focus(self.username)
        self.app.status.set("Login cleared. Ready.")

    def _login(self):
        u = self.username.get().strip()
        p = self.password.get()

        if is_blank(u) or is_blank(p):
            Toast(self.app, "Username and password are required.", kind="danger")
            self.app.status.set("Login error: missing fields.")
            return

        mode = normalize_mode_value(self.mode.get())
        auth.VULNERABLE_MODE = (mode == "demo")

        status, extra = auth.login_user(u, p)

        if status == "ok":
            Toast(self.app, "Login successful.", kind="success")
            self.app.status.set(f"Login success. Mode: {mode.upper()}.")
            self.password.delete(0, tk.END)
            set_focus(self.username)
            # Ponudi korisniku da preuzme bazu
            if download_db():
                Toast(self.app, "Database downloaded!", kind="success")
            else:
                Toast(self.app, "Database download canceled.", kind="warn")
        elif status == "locked":
            Toast(self.app, "Account locked.", kind="danger")
            self.app.status.set("Login failed: account locked.")
        elif status == "not_found":
            Toast(self.app, "User not found.", kind="danger")
            self.app.status.set("Login failed: user not found.")
        elif status == "invalid":
            if extra is not None:
                Toast(self.app, f"Invalid password. Remaining attempts: {extra}", kind="warn")
                self.app.status.set("Login failed: invalid password (lockout counting).")
            else:
                Toast(self.app, "Invalid credentials.", kind="danger")
                self.app.status.set("Login failed: invalid credentials.")
        else:
            Toast(self.app, "Login failed.", kind="danger")
            self.app.status.set("Login failed: unknown status returned.")


class RegisterScreen(ScreenBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        tk.Label(self, text="Register", bg=THEME["panel"], fg=THEME["text"], font=FONTS["h2"]).pack(anchor="w")

        Divider(self, pady=10)

        tk.Label(self, text="Username", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body"]).pack(anchor="w")
        self.username = NeonEntry(self)
        self.username.pack(fill="x", pady=(6, 12))

        self.username_hint = tk.Label(
            self,
            text="3–32 chars: letters, numbers, underscore, dot, hyphen.",
            bg=THEME["panel"],
            fg=THEME["muted"],
            font=FONTS["small"],
        )
        self.username_hint.pack(anchor="w", pady=(0, 10))

        tk.Label(self, text="Password", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body"]).pack(anchor="w")
        self.password = NeonEntry(self, show="*")
        self.password.pack(fill="x", pady=(6, 10))

        tk.Label(self, text="Confirm Password", bg=THEME["panel"], fg=THEME["text"], font=FONTS["body"]).pack(anchor="w")
        self.confirm = NeonEntry(self, show="*")
        self.confirm.pack(fill="x", pady=(6, 8))

        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self,
            text="Show passwords",
            variable=self.show_pw_var,
            command=self._toggle_pw,
            bg=THEME["panel"],
            fg=THEME["muted"],
            activebackground=THEME["panel"],
            activeforeground=THEME["text"],
            selectcolor=THEME["panel"],
            font=FONTS["body"],
        ).pack(anchor="w", pady=(0, 10))

        # Strength meter
        self.str_row = tk.Frame(self, bg=THEME["panel"])
        self.str_row.pack(fill="x", pady=(2, 8))

        tk.Label(self.str_row, text="Strength:", bg=THEME["panel"], fg=THEME["muted"], font=FONTS["body"]).pack(side="left")
        self.str_label = tk.Label(self.str_row, text="-", bg=THEME["panel"], fg=THEME["muted"], font=FONTS["body_b"])
        self.str_label.pack(side="left", padx=(8, 0))

        self.meter = tk.Canvas(self, height=10, bg=THEME["panel"], highlightthickness=0)
        self.meter.pack(fill="x", pady=(0, 10))
        self._draw_meter(0)

        self.str_hint = tk.Label(self, text="", bg=THEME["panel"], fg=THEME["muted"], font=FONTS["small"], wraplength=460, justify="left")
        self.str_hint.pack(anchor="w", pady=(0, 8))

        Divider(self, pady=12)

        NeonButton(self, "CREATE ACCOUNT", self._handle_register, accent=THEME["accent2"]).pack(fill="x")

        row = tk.Frame(self, bg=THEME["panel"])
        row.pack(fill="x", pady=(12, 0))
        # GhostButton(row, "← Back to login", self.app.show_login, fg=THEME["accent"]).pack(side="left")

        bind_enter(self.username, self._register)
        bind_enter(self.password, self._register)
        bind_enter(self.confirm, self._register)
        bind_escape(self, self._clear)

        self.password.bind("<KeyRelease>", self._update_strength)
        self.confirm.bind("<KeyRelease>", self._update_match)

        self.match_label = tk.Label(self, text="", bg=THEME["panel"], fg=THEME["muted"], font=FONTS["small"])
        self.match_label.pack(anchor="w", pady=(0, 0))

    def _toggle_pw(self):
        show = "" if self.show_pw_var.get() else "*"
        self.password.configure(show=show)
        self.confirm.configure(show=show)

    def _clear(self):
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.confirm.delete(0, tk.END)
        self.str_label.configure(text="-", fg=THEME["muted"])
        self.str_hint.configure(text="")
        self.match_label.configure(text="", fg=THEME["muted"])
        self._draw_meter(0)
        set_focus(self.username)
        self.app.status.set("Register cleared. Ready.")

    def _draw_meter(self, score: int):
        self.meter.delete("all")
        w = max(1, self.meter.winfo_width())
        if w == 1:
            self.after(10, lambda: self._draw_meter(score))
            return

        # background track
        self.meter.create_rectangle(0, 3, w, 7, fill=THEME["border"], outline=THEME["border"])

        # filled portion
        steps = 4
        frac = score / steps if steps else 0
        fill_w = int(w * frac)
        color = strength_color(score)
        self.meter.create_rectangle(0, 3, fill_w, 7, fill=color, outline=color)

    def _update_strength(self, _e=None):
        label, score, suggestions = password_strength(self.password.get())
        self.str_label.configure(text=label, fg=strength_color(score))
        self._draw_meter(score)

        if suggestions:
            self.str_hint.configure(text=" • " + "\n • ".join(suggestions))
        else:
            self.str_hint.configure(text="Looks good.")
        self._update_match()

    def _update_match(self, _e=None):
        p = self.password.get()
        c = self.confirm.get()
        if not p and not c:
            self.match_label.configure(text="", fg=THEME["muted"])
            return
        if p == c:
            self.match_label.configure(text="Passwords match.", fg=THEME["success"])
        else:
            self.match_label.configure(text="Passwords do not match.", fg=THEME["danger"])

    def _handle_register(self):
        u = self.username.get().strip()
        p = self.password.get()
        c = self.confirm.get()

        if is_blank(u) or is_blank(p) or is_blank(c):
            Toast(self.app, "All fields are required.", kind="danger")
            self.app.status.set("Register error: missing fields.")
            return

        if not username_is_reasonable(u):
            Toast(self.app, "Username must be 3–32 chars (letters/numbers/_.-).", kind="danger")
            self.app.status.set("Register error: invalid username format.")
            return

        if p != c:
            Toast(self.app, "Passwords do not match.", kind="danger")
            self.app.status.set("Register error: passwords mismatch.")
            return

        _, score, _ = password_strength(p)
        if score < 2:
            Toast(self.app, "Password too weak. Improve strength.", kind="warn")
            self.app.status.set("Register error: weak password.")
            return

        ok = auth.register_user(u, p)
        if ok:
            Toast(self.app, "Account created. You can now log in.", kind="success")
            self.app.status.set("Register success: account created.")
            self._clear()
            self.app.show_login()
        else:
            Toast(self.app, "Username already exists.", kind="danger")
            self.app.status.set("Register failed: username exists.")


# ==================================================================================================
# APP
# ==================================================================================================

class AuthApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Secure Authentication Demo")
        self.configure(bg=THEME["bg"])
        self.resizable(False, False)
        center_window(self, APP_W, APP_H)

        self.container = tk.Frame(self, bg=THEME["panel"], highlightthickness=1, highlightbackground=THEME["border"])
        self.container.place(relx=0.5, rely=0.5, anchor="center", width=CARD_W, height=CARD_H)

        # Header
        header = tk.Frame(self.container, bg=THEME["panel"])
        header.pack(fill="x", pady=(18, 10))

        tk.Label(header, text="SECURE AUTHENTICATION", font=FONTS["title"], bg=THEME["panel"], fg=THEME["text"]).pack(anchor="w", padx=24)

        Divider(self.container, pady=10)

        # Tabs
        tabs_row = tk.Frame(self.container, bg=THEME["panel"])
        tabs_row.pack(fill="x", padx=24, pady=(0, 10))
        self.tabs = PillTabs(tabs_row, self._on_tab_select)
        self.tabs.pack(anchor="w")

        # Content area
        self.body = tk.Frame(self.container, bg=THEME["panel"])
        self.body.pack(fill="both", expand=True, padx=24, pady=(6, 0))

        self.login = LoginScreen(self.body, self)
        self.register = RegisterScreen(self.body, self)

        # Status
        self.status = StatusBar(self.container)
        self.status.pack(fill="x", padx=24, pady=(8, 14))

        self.show_login()

        # global shortcut: Ctrl+L login tab, Ctrl+R register tab
        self.bind_all("<Control-l>", lambda _e: self.show_login())
        self.bind_all("<Control-r>", lambda _e: self.show_register())

    def _on_tab_select(self, tab: str):
        if tab == "register":
            self.show_register()
        else:
            self.show_login()

    def show_login(self):
        self.register.pack_forget()
        self.login.pack(fill="both", expand=True)
        self.tabs.active.set("login")
        self.tabs._apply_styles()
        self.login.on_show()

    def show_register(self):
        self.login.pack_forget()
        self.register.pack(fill="both", expand=True)
        self.tabs.active.set("register")
        self.tabs._apply_styles()
        self.register.on_show()


# ==================================================================================================
# RUN
# ==================================================================================================

if __name__ == "__main__":
    # Optional: init db if auth.py has it
    if hasattr(auth, "init_db") and callable(getattr(auth, "init_db")):
        try:
            auth.init_db()
        except Exception:
            pass

    app = AuthApp()
    app.mainloop()

import tkinter as tk
from tkinter import messagebox
from auth import register_user, login_user

THEME = {
    "bg_top": "#050722",
    "bg_bottom": "#1a0b3d",
    "neon_blue": "#00d4ff",
    "neon_cyan": "#39f5ff",
    "neon_purple": "#b34cff",
    "neon_magenta": "#ff4fd8",
    "panel_bg": "#070a25",
    "panel_bg2": "#0b1033",
    "text": "#e6f0ff",
    "muted": "#a8b3d6",
    "danger": "#ff4a4a",
    "success": "#2cffb0",
    "border": "#1f2a66",
}

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")


def clamp(v: int) -> int:
    return max(0, min(255, int(v)))


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int):
    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(lerp(r1, r2, t), lerp(g1, g2, t), lerp(b1, b2, t))


def password_strength(pw: str) -> tuple[str, int]:
    score = 0
    if len(pw) >= 8:
        score += 1
    if any(c.islower() for c in pw) and any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|" for c in pw):
        score += 1
    labels = ["Very weak", "Weak", "Okay", "Good", "Strong"]
    return labels[score], score


# ---------------------------
# CYBER BACKGROUND CANVAS
# ---------------------------
class CyberBackground(tk.Canvas):
    """
    Draws a neon gradient + circuit lines + pixels + glowing portal
    similar to the reference image style.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        # Gradient background
        steps = 90
        for i in range(steps):
            t = i / (steps - 1)
            col = lerp_color(THEME["bg_top"], THEME["bg_bottom"], t)
            y0 = int((i / steps) * h)
            y1 = int(((i + 1) / steps) * h)
            self.create_rectangle(0, y0, w, y1, fill=col, outline=col)

        # Subtle vignette edges (fake)
        self.create_rectangle(0, 0, w, h, outline=THEME["border"], width=2)

        # Circuit lines
        self._draw_circuits(w, h)

        # Floating pixels
        self._draw_pixels(w, h)

        # Central glowing portal strip
        self._draw_portal(w, h)

    def _draw_circuits(self, w: int, h: int):
        # Left side traces
        self._trace_bundle(x0=int(w * 0.05), x1=int(w * 0.35), y0=int(h * 0.15), y1=int(h * 0.85))
        # Right side traces
        self._trace_bundle(x0=int(w * 0.65), x1=int(w * 0.95), y0=int(h * 0.10), y1=int(h * 0.90))

        # Top grid / lines
        for i in range(6):
            x = int(w * (0.15 + i * 0.12))
            self.create_line(x, 0, x, int(h * 0.18), fill=THEME["neon_purple"], width=1)
            self.create_oval(x - 2, int(h * 0.18) - 2, x + 2, int(h * 0.18) + 2, fill=THEME["neon_magenta"], outline="")

    def _trace_bundle(self, x0, x1, y0, y1):
        # Draw a set of polyline "circuit" traces with glowing nodes.
        color = THEME["neon_blue"]
        node = THEME["neon_magenta"]

        # vertical spines
        for i in range(5):
            x = x0 + int((x1 - x0) * (i / 4))
            self.create_line(x, y0, x, y1, fill=color, width=1)

        # horizontal branches
        for i in range(9):
            y = y0 + int((y1 - y0) * (i / 8))
            x_start = x0 + (i % 3) * 18
            x_end = x1 - (i % 2) * 22
            self.create_line(x_start, y, x_end, y, fill=color, width=1)
            # node at end
            self.create_rectangle(x_end - 2, y - 2, x_end + 2, y + 2, fill=node, outline="")

    def _draw_pixels(self, w: int, h: int):
        # Deterministic pseudo-random-ish placement (no random import)
        px_colors = [THEME["neon_blue"], THEME["neon_purple"], THEME["neon_magenta"], THEME["neon_cyan"]]
        count = 65
        for i in range(count):
            x = (i * 73) % w
            y = (i * 139) % h
            size = 2 + (i % 3)
            c = px_colors[i % len(px_colors)]
            # avoid center card area by skipping near mid
            if abs(x - w // 2) < 140 and abs(y - h // 2) < 140:
                continue
            self.create_rectangle(x, y, x + size, y + size, fill=c, outline="")

    def _draw_portal(self, w: int, h: int):
        cx = w // 2
        top = int(h * 0.16)
        bottom = int(h * 0.90)
        width = int(w * 0.22)

        # glow layers
        for i in range(10, 0, -1):
            pad = i * 4
            col = lerp_color(THEME["neon_purple"], THEME["neon_blue"], i / 10)
            self.create_rectangle(
                cx - width // 2 - pad,
                top - pad,
                cx + width // 2 + pad,
                bottom + pad,
                outline=col,
                width=2,
            )

        # inner portal gradient strip
        steps = 70
        for i in range(steps):
            t = i / (steps - 1)
            col = lerp_color("#001a7a", THEME["neon_blue"], t)
            y0 = top + int((i / steps) * (bottom - top))
            y1 = top + int(((i + 1) / steps) * (bottom - top))
            self.create_rectangle(cx - width // 2, y0, cx + width // 2, y1, fill=col, outline=col)


# ---------------------------
# UI COMPONENTS
# ---------------------------
class NeonButton(tk.Button):
    def __init__(self, parent, text, command, kind="primary"):
        bg = THEME["neon_blue"] if kind == "primary" else THEME["neon_purple"]
        fg = "#001018"
        super().__init__(
            parent,
            text=text,
            command=command,
            font=FONT_BTN,
            bg=bg,
            fg=fg,
            activebackground=THEME["neon_cyan"],
            activeforeground=fg,
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2",
        )


class LinkButton(tk.Label):
    def __init__(self, parent, text, command, base_color):
        super().__init__(
            parent,
            text=text,
            font=FONT_BODY,
            bg=THEME["panel_bg"],
            fg=base_color,
            cursor="hand2",
        )

        self.command = command
        self.base_color = base_color

        # Hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Click
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _):
        self.config(fg=THEME["neon_magenta"])

    def _on_leave(self, _):
        self.config(fg=self.base_color)

    def _on_click(self, _):
        # switch to opposite color on click
        click_color = (
            THEME["neon_blue"]
            if self.base_color == THEME["neon_purple"]
            else THEME["neon_purple"]
        )
        self.config(fg=click_color)

    def _on_release(self, _):
        self.config(fg=self.base_color)
        self.command()

class NeonEntry(tk.Entry):
    def __init__(self, parent, show=None):
        super().__init__(
            parent,
            font=FONT_BODY,
            bg=THEME["panel_bg2"],
            fg=THEME["text"],
            insertbackground=THEME["neon_cyan"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["neon_blue"],
        )
        if show is not None:
            self.configure(show=show)


# ---------------------------
# MAIN APP
# ---------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Authentication System")
        self.geometry("980x560")
        self.minsize(980, 560)
        self.configure(bg=THEME["bg_top"])

        # Background canvas
        self.bg = CyberBackground(self, bg=THEME["bg_top"])
        self.bg.pack(fill="both", expand=True)

        # Overlay panel (center card)
        self.panel = tk.Frame(self.bg, bg=THEME["panel_bg"], highlightthickness=1, highlightbackground=THEME["neon_blue"])
        self.panel.place(relx=0.5, rely=0.5, anchor="center", width=420, height=520)

        # inner padding container
        self.inner = tk.Frame(self.panel, bg=THEME["panel_bg"])
        self.inner.pack(fill="both", expand=True, padx=22, pady=20)

        self.title_label = tk.Label(self.inner, text="SECURE ACCESS", font=FONT_TITLE, bg=THEME["panel_bg"], fg=THEME["text"])
        self.title_label.pack(anchor="w")

        self.sub_label = tk.Label(
            self.inner,
            text=" • SQLite • bcrypt",
            font=FONT_BODY,
            bg=THEME["panel_bg"],
            fg=THEME["muted"],
        )
        self.sub_label.pack(anchor="w", pady=(6, 16))

        # screen container
        self.screen_container = tk.Frame(self.inner, bg=THEME["panel_bg"])
        self.screen_container.pack(fill="both", expand=True)

        self.login_screen = LoginScreen(self.screen_container, on_switch=self.show_register)
        self.register_screen = RegisterScreen(self.screen_container, on_switch=self.show_login)

        self.status = tk.Label(self.inner, text="", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["muted"])
        self.status.pack(anchor="w", pady=(10, 0))

        self.show_login()

    def show_login(self):
        self.register_screen.pack_forget()
        self.login_screen.pack(fill="both", expand=True)

    def show_register(self):
        self.login_screen.pack_forget()
        self.register_screen.pack(fill="both", expand=True)


class LoginScreen(tk.Frame):
    def __init__(self, parent, on_switch):
        super().__init__(parent, bg=THEME["panel_bg"])
        self.on_switch = on_switch

        tk.Label(self, text="LOGIN", font=FONT_H2, bg=THEME["panel_bg"], fg=THEME["neon_cyan"]).pack(anchor="w", pady=(0, 10))

        tk.Label(self, text="Username", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["text"]).pack(anchor="w")
        self.username = NeonEntry(self)
        self.username.pack(fill="x", pady=(6, 12))

        tk.Label(self, text="Password", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["text"]).pack(anchor="w")
        self.password = NeonEntry(self, show="*")
        self.password.pack(fill="x", pady=(6, 10))

        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self,
            text="Show password",
            variable=self.show_pw_var,
            command=self._toggle_pw,
            bg=THEME["panel_bg"],
            fg=THEME["muted"],
            activebackground=THEME["panel_bg"],
            activeforeground=THEME["text"],
            selectcolor=THEME["panel_bg"],
            font=FONT_BODY,
        ).pack(anchor="w", pady=(0, 14))

        NeonButton(self, text="LOGIN", command=self._login, kind="primary").pack(fill="x", pady=(0, 10))
        LinkButton(self, text="Create new account →", command=self.on_switch, base_color=THEME["neon_blue"]).pack(anchor="e")


    def _toggle_pw(self):
        self.password.configure(show="" if self.show_pw_var.get() else "*")

    def _login(self):
        u = self.username.get().strip()
        p = self.password.get()
        if not u or not p:
            messagebox.showerror("Error", "Username and password are required.")
            return

        status, extra = login_user(u, p)

        if status == "ok":
            messagebox.showinfo("Success", "Login successful.")
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
            return

        if status == "not_found":
            messagebox.showerror("Error", "User not found.")
            return

        if status == "locked":
            messagebox.showerror("Locked", "Account locked after too many failed attempts.")
            return

        # invalid
        if extra is not None:
            messagebox.showerror("Error", f"Invalid credentials. Attempts remaining: {extra}")
        else:
            messagebox.showerror("Error", "Invalid username or password.")


class RegisterScreen(tk.Frame):
    def __init__(self, parent, on_switch):
        super().__init__(parent, bg=THEME["panel_bg"])
        self.on_switch = on_switch

        tk.Label(self, text="REGISTER", font=FONT_H2, bg=THEME["panel_bg"], fg=THEME["neon_magenta"]).pack(anchor="w", pady=(0, 10))

        tk.Label(self, text="Username", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["text"]).pack(anchor="w")
        self.username = NeonEntry(self)
        self.username.pack(fill="x", pady=(6, 12))

        tk.Label(self, text="Password", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["text"]).pack(anchor="w")
        self.password = NeonEntry(self, show="*")
        self.password.pack(fill="x", pady=(6, 12))

        tk.Label(self, text="Confirm Password", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["text"]).pack(anchor="w")
        self.confirm = NeonEntry(self, show="*")
        self.confirm.pack(fill="x", pady=(6, 10))

        # --- Row: show passwords (left) + back to login (right)
        row = tk.Frame(self, bg=THEME["panel_bg"])
        row.pack(fill="x", pady=(0, 10))

        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            row,
            text="Show passwords",
            variable=self.show_pw_var,
            command=self._toggle_pw,
            bg=THEME["panel_bg"],
            fg=THEME["muted"],
            activebackground=THEME["panel_bg"],
            activeforeground=THEME["text"],
            selectcolor=THEME["panel_bg"],
            font=FONT_BODY,
        ).pack(side="left")

        LinkButton(row, text="← Back to login", command=self.on_switch, base_color=THEME["neon_purple"]).pack(side="right")

        self.str_label = tk.Label(self, text="Password strength: -", font=FONT_BODY, bg=THEME["panel_bg"], fg=THEME["muted"])
        self.str_label.pack(anchor="w", pady=(0, 14))
        self.password.bind("<KeyRelease>", self._update_strength)

        NeonButton(self, text="CREATE ACCOUNT", command=self._register, kind="secondary").pack(fill="x", pady=(0, 10))

    def _toggle_pw(self):
        show = "" if self.show_pw_var.get() else "*"
        self.password.configure(show=show)
        self.confirm.configure(show=show)

    def _update_strength(self, _event=None):
        label, score = password_strength(self.password.get())
        self.str_label.configure(text=f"Password strength: {label}")

    def _register(self):
        u = self.username.get().strip()
        p = self.password.get()
        c = self.confirm.get()

        if not u or not p or not c:
            messagebox.showerror("Error", "All fields are required.")
            return

        if len(u) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters.")
            return

        if p != c:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        label, score = password_strength(p)
        if score < 2:
            messagebox.showerror("Error", "Password too weak. Use 8+ chars with digits/symbols.")
            return

        if register_user(u, p):
            messagebox.showinfo("Success", "Account created. You can now login.")
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
            self.confirm.delete(0, tk.END)
            self.on_switch()
        else:
            messagebox.showerror("Error", "Username already exists.")


if __name__ == "__main__":
    app = App()
    app.mainloop()

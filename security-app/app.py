import tkinter as tk
from tkinter import messagebox
from auth import register_user, login_user

# --- Main window ---
root = tk.Tk()
root.title("Secure Authentication System")
root.geometry("400x300")
root.resizable(False, False)

# --- Title ---
title_label = tk.Label(
    root,
    text="Login / Register",
    font=("Arial", 16)
)
title_label.pack(pady=15)

# --- Username ---
username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)

# --- Password ---
password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

# --- Actions ---
def handle_register():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "All fields are required.")
        return

    if register_user(username, password):
        messagebox.showinfo("Success", "User registered successfully.")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Username already exists.")


def handle_login():
    username = username_entry.get()
    password = password_entry.get()

    if login_user(username, password):
        messagebox.showinfo("Success", "Login successful.")
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# --- Buttons ---
register_button = tk.Button(
    root,
    text="Register",
    width=20,
    command=handle_register
)
register_button.pack(pady=8)

login_button = tk.Button(
    root,
    text="Login",
    width=20,
    command=handle_login
)
login_button.pack(pady=5)

# --- Run app ---
root.mainloop()
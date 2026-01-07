import shutil
from tkinter import filedialog
import os

def download_db():
    src = os.path.join(os.path.dirname(__file__), 'users.db')
    dst = filedialog.asksaveasfilename(
        defaultextension='.db',
        filetypes=[('SQLite Database', '*.db'), ('All Files', '*.*')],
        title='Save a copy of the database'
    )
    if dst:
        shutil.copyfile(src, dst)
        return True
    return False

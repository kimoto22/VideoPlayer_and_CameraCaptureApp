import tkinter as tk
import pyautogui

def restrict_cursor(event):
    x, y = event.x, event.y
    if 0 <= x < window.winfo_width() and 0 <= y < window.winfo_height():
        window.config(cursor="")
    else:
        window.config(cursor="none")
        force_cursor_inside()

def force_cursor_inside():
    x, y = pyautogui.position()
    window_x, window_y = window.winfo_rootx(), window.winfo_rooty()
    window_width, window_height = window.winfo_width(), window.winfo_height()

    if x < window_x:
        x = window_x
    elif x >= window_x + window_width:
        x = window_x + window_width - 1
    if y < window_y:
        y = window_y
    elif y >= window_y + window_height:
        y = window_y + window_height - 1
    pyautogui.moveTo(x, y)

window = tk.Tk()
window.title("Restricted Cursor")

# ウィンドウのサイズを300x20に設定
window.geometry("300x20")

# Hide the standard mouse cursor
window.config(cursor="none")

# Bind events to restrict and force cursor movement
window.bind("<Motion>", restrict_cursor)

window.mainloop()

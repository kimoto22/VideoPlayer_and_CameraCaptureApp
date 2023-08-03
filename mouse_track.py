import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker App")
        self.root.geometry("400x350")

        self.tracking = False
        self.log_file = None
        self.block_height = 150
        self.starting_y = 100

        self.create_widgets()

    def create_widgets(self):
        self.folder_select_btn = tk.Button(self.root, text="フォルダ選択", command=self.select_folder)
        self.folder_select_btn.pack(pady=10)

        self.start_btn = tk.Button(self.root, text="トラッキング開始", command=self.start_tracking, state=tk.DISABLED)
        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(self.root, text="トラッキング停止", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        self.scale_label = tk.Label(self.root, text="マウス位置スケール:")
        self.scale_label.pack()

        self.scale_canvas = tk.Canvas(self.root, width=300, height=20, bg="white")
        self.scale_canvas.pack()

        self.tracking_window = None
        self.blocks_canvas = None

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.log_file = f"{folder_path}/mouse_log.csv"
            self.start_btn.config(state=tk.NORMAL)

    def start_tracking(self):
        if self.log_file:
            self.tracking = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.folder_select_btn.config(state=tk.DISABLED)

            self.tracking_window = tk.Toplevel(self.root)
            self.tracking_window.title("マウストラッキングウィンドウ")
            window_width = 400
            window_height = 960
            self.tracking_window.geometry(f"{window_width}x{window_height}")
            self.tracking_window.resizable(0, 0)

            self.blocks_canvas = tk.Canvas(self.tracking_window, width=300, height=900, bg="white")
            self.blocks_canvas.pack()

            self.tracking_window.bind("<Motion>", self.on_mouse_motion)

            with open(self.log_file, mode='w', newline='') as csvfile:
                fieldnames = ['timestamp', 'x', 'y', 'scale']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            self.log_mouse_position_to_csv()

    def stop_tracking(self):
        self.tracking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.folder_select_btn.config(state=tk.NORMAL)

        if self.tracking_window:
            self.tracking_window.unbind("<Motion>")
            self.tracking_window.destroy()
            self.tracking_window = None
            self.blocks_canvas = None

    def on_mouse_motion(self, event):
        if self.tracking:
            self.update_scale_display(event.y)
            scale_value = 4 - min(max((event.y - self.starting_y) // self.block_height, 0), 4)
            self.update_blocks_canvas(scale_value)
            self.log_mouse_position_to_csv(event.x, event.y, scale_value)

    def log_mouse_position_to_csv(self, x=None, y=None, scale_value=None):
        if x is not None and y is not None and scale_value is not None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_file, mode='a', newline='') as csvfile:
                fieldnames = ['timestamp', 'x', 'y', 'scale']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'timestamp': timestamp, 'x': x, 'y': y, 'scale': scale_value})

    def update_scale_display(self, y):
        scale_value = 4 - min(max((y - self.starting_y) // self.block_height, 0), 4)
        self.scale_canvas.delete("all")
        colors = ["blue", "red", "orange", "yellow", "green"]
        self.scale_canvas.create_rectangle(0, 0, 300, 20, fill=colors[scale_value], outline="")
        self.scale_canvas.create_text(150, 10, text=f"スケール: {scale_value}", fill="black")

    def update_blocks_canvas(self, scale_value):
        self.blocks_canvas.delete("all")
        colors = ["green", "yellow", "orange", "red", "blue"]
        for i in range(5):
            self.blocks_canvas.create_rectangle(0, i * self.block_height + self.starting_y, 300, (i + 1) * self.block_height + self.starting_y, fill=colors[i], outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import filedialog
from datetime import datetime

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker App")
        self.root.geometry("400x350")

        self.tracking = False
        self.log_file = None
        self.block_height = 150
        self.starting_y = 100  # 色ブロックの始まりのy軸座標

        self.create_widgets()

    def create_widgets(self):
        self.folder_select_btn = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.folder_select_btn.pack(pady=10)

        self.start_btn = tk.Button(self.root, text="Start Tracking", command=self.start_tracking, state=tk.DISABLED)
        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(self.root, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        self.scale_label = tk.Label(self.root, text="Mouse Position Scale:")
        self.scale_label.pack()

        self.scale_canvas = tk.Canvas(self.root, width=300, height=20, bg="white")
        self.scale_canvas.pack()

        self.tracking_window = None
        self.blocks_canvas = None

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.log_file = f"{folder_path}/mouse_log.txt"
            self.start_btn.config(state=tk.NORMAL)

    def start_tracking(self):
        if self.log_file:
            self.tracking = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.folder_select_btn.config(state=tk.DISABLED)

            # Create a new window for mouse tracking
            self.tracking_window = tk.Toplevel(self.root)
            self.tracking_window.title("Mouse Tracking Window")

            # 色ブロックのウィンドウサイズを縦方向に3倍に設定
            window_width = 400
            window_height = 960
            self.tracking_window.geometry(f"{window_width}x{window_height}")

            # Disable resizing of the tracking window
            self.tracking_window.resizable(0, 0)

            # Create canvas for blocks
            self.blocks_canvas = tk.Canvas(self.tracking_window, width=300, height=900, bg="white")
            self.blocks_canvas.pack()

            # Bind mouse events to the tracking window
            self.tracking_window.bind("<Motion>", self.on_mouse_motion)

    def stop_tracking(self):
        self.tracking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.folder_select_btn.config(state=tk.NORMAL)

        # Unbind mouse events when tracking stops
        if self.tracking_window:
            self.tracking_window.unbind("<Motion>")
            self.tracking_window.destroy()
            self.tracking_window = None
            self.blocks_canvas = None

    def on_mouse_motion(self, event):
        if self.tracking:
            # Update the scale display
            self.update_scale_display(event.y)

            # Update the blocks canvas
            scale_value = 4 - min(max((event.y - self.starting_y) // self.block_height, 0), 4)
            self.update_blocks_canvas(scale_value)

    def log_mouse_position(self):
        if self.tracking:
            x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
            log_data = f"{datetime.now()} - Mouse position: x={x}, y={y}\n"
            with open(self.log_file, "a") as file:
                file.write(log_data)
            
            # Update the scale display
            self.update_scale_display(y)

            self.root.after(100, self.log_mouse_position)

    def update_scale_display(self, y):
        # Map the cursor position to a 5-level scale (0 to 4)
        scale_value = 4 - min(max((y - self.starting_y) // self.block_height, 0), 4)

        # Clear the scale canvas and draw the colored scale bar
        self.scale_canvas.delete("all")
        colors = ["white", "red", "orange", "yellow", "green"]
        self.scale_canvas.create_rectangle(0, 0, 300, 20, fill=colors[scale_value], outline="")
        self.scale_canvas.create_text(150, 10, text=f"Scale: {scale_value}", fill="black")

    def update_blocks_canvas(self, scale_value):
        # Clear the blocks canvas and draw the blocks based on the scale
        self.blocks_canvas.delete("all")
        colors = ["green", "yellow", "orange", "red", "white"]
        for i in range(5):
            self.blocks_canvas.create_rectangle(0, i * self.block_height + self.starting_y, 300, (i + 1) * self.block_height + self.starting_y, fill=colors[i], outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()

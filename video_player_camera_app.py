import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
import threading
import time
import numpy as np

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player App")

        self.video_path = ""
        self.output_folder = ""
        self.human_video_path = ""

        self.video_label = tk.Label(root, text="Select a video to play (mp4 only):")
        self.video_label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Video", command=self.select_video)
        self.select_button.pack(pady=5)

        self.play_button = tk.Button(root, text="Play Video", command=self.play_and_capture)
        self.play_button.pack(pady=5)

        self.name_entry_label = tk.Label(root, text="Enter your name:")
        self.name_entry_label.pack(pady=5)

        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        self.video_player = None
        self.camera_thread = None
        self.is_capturing = False
        self.is_playing = False
        self.stop_camera = False

        self.start_time_label = tk.Label(root, text="Video Start Time:")
        self.start_time_label.pack(pady=5)

        self.camera_start_time_label = tk.Label(root, text="Camera Start Time:")
        self.camera_start_time_label.pack(pady=5)

        self.end_time_label = tk.Label(root, text="End Time:")
        self.end_time_label.pack(pady=5)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4")])

        if self.video_path:
            self.video_label.config(text=f"Selected Video: {os.path.basename(self.video_path)}")

        base_name = os.path.basename(str(self.video_path))
        self.video_name = os.path.splitext(base_name)[0]

    def modify_video_path(self, name):
        directory, filename = os.path.split(self.video_path)
        new_directory = os.path.join(directory, name).replace("\\", "/")

        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        return new_directory

    def play_and_capture(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video to play.")
            return

        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

        self.is_capturing = True
        self.camera_thread = threading.Thread(target=self.capture_frames, args=(name,))
        self.camera_thread.start()

        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_label.config(text="Video Start Time: " + start_time)
        self.camera_start_time_label.config(text="Camera Start Time: " + start_time)

        self.play_video()

        self.is_capturing = False
        self.camera_thread.join()

        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time_label.config(text="End Time: " + end_time)

        self.save_times_to_file(name, start_time, end_time)

    def save_times_to_file(self, name, start_time, end_time):
        video_folder = os.path.dirname(self.video_path)
        output_filename = os.path.join(video_folder, f"{name}_video_times.txt")

        with open(output_filename, "w") as file:
            file.write(f"Video Start Time: {start_time}\n")
            file.write(f"Camera Start Time: {start_time}\n")
            file.write(f"End Time: {end_time}")

    def play_video(self):
        cap = cv2.VideoCapture(self.video_path)
        delay_seconds = 5
        icon_size = 40
        icon_display_duration = 1  # アイコンを表示する秒数
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        icon_display_count = total_frames // int(video_fps)  # 動画時間の1秒ごとにアイコンを表示

        def countdown():
            for i in range(delay_seconds, 0, -1):
                self.play_button.config(text=f"Play Video ({i})")
                time.sleep(1)
            self.play_button.config(text="Play Video")
            self.is_playing = True

        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()

        for i in range(delay_seconds * int(video_fps)):
            ret, _ = cap.read()
            if not ret:
                break

        icon_displayed = 0
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % int(video_fps) == 0 and icon_displayed < icon_display_count:
                self.draw_icon(frame, icon_size, int(video_fps) * icon_display_duration)
                icon_displayed += 1

            frame_count += 1
            time.sleep(1 / video_fps)
            cv2.imshow("Video Player", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.stop_camera = True

    def capture_frames(self, name):
        camera_w = 1280
        camera_h = 720

        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_w)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_h)

        camera_fps = capture.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.human_video_path = self.modify_video_path(name)
        output_filename = os.path.join(self.human_video_path, f"{name}_{self.video_name}.avi").replace("\\", "/")
        out = cv2.VideoWriter(output_filename, fourcc, camera_fps, (camera_w, camera_h))

        while self.is_capturing and not self.stop_camera:
            ret, frame = capture.read()
            if not ret:
                break

            out.write(frame)

        capture.release()
        out.release()

    def draw_icon(self, frame, icon_size, display_frames):
        icon = np.zeros((icon_size, icon_size, 3), dtype=np.uint8)
        cv2.rectangle(icon, (0, 0), (icon_size - 1, icon_size - 1), (255, 255, 255), -1)

        # 画面の4つの角からランダムに1つを選ぶ
        corner = np.random.randint(4)
        if corner == 0:  # 左上
            x = 0
            y = 0
        elif corner == 1:  # 右上
            x = frame.shape[1] - icon_size
            y = 0
        elif corner == 2:  # 左下
            x = 0
            y = frame.shape[0] - icon_size
        else:  # 右下
            x = frame.shape[1] - icon_size
            y = frame.shape[0] - icon_size

        roi = frame[y:y+icon_size, x:x+icon_size]
        alpha_icon = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(alpha_icon, 50, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        frame_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        icon_fg = cv2.bitwise_and(icon, icon, mask=mask)
        dst = cv2.add(frame_bg, icon_fg)
        frame[y:y+icon_size, x:x+icon_size] = dst

        # アイコンの表示フレーム数に達したらアイコンを消す
        if display_frames > 0:
            display_frames -= 1
            if display_frames == 0:
                frame[y:y+icon_size, x:x+icon_size] = roi

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()

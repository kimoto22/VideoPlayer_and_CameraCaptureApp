import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
import threading
import time
import datetime
import pandas as pd
import numpy as np

# クラス: VideoPlayerApp
class VideoPlayerApp:
    def __init__(self, root):
        # ウィンドウの設定
        self.root = root
        self.root.title("Video Player App")

        # 変数初期化
        self.video_path = ""
        self.output_folder = ""
        self.human_video_path = ""

        # ウィジェットの配置
        # 動画選択ラベル
        self.video_label = tk.Label(root, text="再生する動画を選択してください（mp4形式のみ）:")
        self.video_label.pack(pady=10)

        # 動画選択ボタン
        self.select_button = tk.Button(root, text="動画を選択", command=self.select_video)
        self.select_button.pack(pady=5)

        # 動画再生ボタン
        self.play_button = tk.Button(root, text="動画再生", command=self.play_and_capture)
        self.play_button.pack(pady=5)

        # お名前入力ラベル
        self.name_entry_label = tk.Label(root, text="お名前を入力してください:")
        self.name_entry_label.pack(pady=5)

        # お名前入力エントリ
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        # 変数初期化
        self.video_player = None
        self.camera_thread = None
        self.is_capturing = False
        self.is_playing = False
        self.stop_camera = False

        # 時刻表示ラベル
        self.start_time_label = tk.Label(root, text="動画開始時刻:")
        self.start_time_label.pack(pady=5)

        self.camera_start_time_label = tk.Label(root, text="カメラ開始時刻:")
        self.camera_start_time_label.pack(pady=5)

        self.end_time_label = tk.Label(root, text="終了時刻:")
        self.end_time_label.pack(pady=5)
        
        # スペースキーが押されたタイミングを保存するためのリスト
        self.space_key_press_times = []

    # 動画選択関数
    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="動画ファイルを選択", filetypes=[("Video files", "*.mp4")])

        if self.video_path:
            self.video_label.config(text=f"選択した動画: {os.path.basename(self.video_path)}")

        base_name = os.path.basename(str(self.video_path))
        self.video_name = os.path.splitext(base_name)[0]

    # 動画保存用のディレクトリを作成する関数
    def modify_video_path(self, name):
        directory, filename = os.path.split(self.video_path)
        new_directory = os.path.join(directory, name).replace("\\", "/")

        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        return new_directory

    # 動画再生とキャプチャを行う関数
    def play_and_capture(self):
        # 動画ファイルが選択されているか確認
        if not self.video_path:
            messagebox.showerror("エラー", "再生する動画を選択してください。")
            return

        # お名前が入力されているか確認
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("エラー", "お名前を入力してください。")
            return

        # カメラキャプチャを開始
        self.is_capturing = True
        self.camera_thread = threading.Thread(target=self.capture_frames, args=(name,))
        self.camera_thread.start()

        # 時刻表示の更新
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_label.config(text="動画開始時刻: " + start_time)
        self.camera_start_time_label.config(text="カメラ開始時刻: " + start_time)

        # ボタンテキストを変更して再生を通知
        self.set_play_button_text("再生中")

        # 動画再生を実行
        self.play_video()

        # キャプチャ終了と時刻表示の更新
        self.is_capturing = False
        self.camera_thread.join()

        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time_label.config(text="終了時刻: " + end_time)

        # 時刻情報をファイルに保存
        self.save_times_to_file(name, start_time, end_time)

    # 再生ボタンのテキストを設定する関数
    def set_play_button_text(self, text):
        self.play_button.config(text=text)
    
    # スペースキーが押されたタイミングを測定する関数
    def record_space_key_press_time(self):
        current_time = datetime.datetime.now()
        self.space_key_press_times.append(current_time)


    # 時刻情報をファイルに保存する関数
    def save_times_to_file(self, name, start_time, end_time):
        video_folder = os.path.dirname(self.video_path)
        output_filename = os.path.join(video_folder, f"{name}_video_times.txt")

        with open(output_filename, "w") as file:
            file.write(f"動画開始時刻: {start_time}\n")
            file.write(f"カメラ開始時刻: {start_time}\n")
            file.write(f"終了時刻: {end_time}")

    # 動画再生を行う関数
    def play_video(self):
        # 動画ファイルを開く
        cap = cv2.VideoCapture(self.video_path)
        delay_seconds = 5
        icon_size = 40
        icon_display_duration = 1
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        icon_display_count = total_frames // int(video_fps)

        # カウントダウンを表示するスレッド
        def countdown():
            for i in range(delay_seconds, 0, -1):
                self.set_play_button_text(f"動画再生中 ({i})")
                time.sleep(1)
            self.set_play_button_text("動画再生中")
            self.is_playing = True

        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()

        # カウントダウン後に一定フレーム数だけスキップ
        for _ in range(delay_seconds * int(video_fps)):
            ret, _ = cap.read()
            if not ret:
                break

        # アイコン表示と明るさ計算を行いながら動画再生
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
            cv2.imshow("ビデオプレーヤー", frame)
            
            # スペースキーを押したタイミングを図る
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            elif key == 32:  # スペースキーのASCIIコード
                print("スペースキーが押されました")
                self.record_space_key_press_time()



            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.stop_camera = True

    # 周囲の色を計算する関数
    def calculate_surrounding_color(self, frame, icon_size, x, y):
        roi = frame[y:y+icon_size, x:x+icon_size]
        r, g, b = np.mean(roi, axis=(0, 1)).astype(int)
        return int(r), int(g), int(b)

    # アイコンの位置を取得する関数
    def get_icon_position(self, frame, icon_size):
        corner = np.random.randint(4)
        if corner == 0:
            x = 0
            y = 0
        elif corner == 1:
            x = frame.shape[1] - icon_size
            y = 0
        elif corner == 2:
            x = 0
            y = frame.shape[0] - icon_size
        else:
            x = frame.shape[1] - icon_size
            y = frame.shape[0] - icon_size
        
        print(f"アイコンの座標: x={x}, y={y}")
        
        return x, y

    # アイコンを描画する関数
    def draw_icon(self, frame, icon_size, display_frames):
        x, y = self.get_icon_position(frame, icon_size)
        sub_img = frame[y:y+icon_size, x:x+icon_size]
        white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255
        
        res = cv2.addWeighted(sub_img, 0.5, white_rect, 0.5, 1.0)
        # Putting the image back to its position
        frame[y:y+icon_size, x:x+icon_size] = res


    # カメラキャプチャを行う関数
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

# メインの実行部分
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()

    # アプリケーションが終了したら、スペースキーの押下タイミングをCSVファイルに保存
    if app.space_key_press_times:
        data = {"SpaceKeyPressTime": app.space_key_press_times}
        df = pd.DataFrame(data)
        df["SpaceKeyPressTime"] = df["SpaceKeyPressTime"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")  # 形式を変更
        csv_filename = os.path.join(app.human_video_path, f"{app.video_name}_space_key_press_times.csv")
        df.to_csv(csv_filename, index=False)
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
import threading
import time

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player App")

        self.video_path = ""
        self.output_folder = ""
        self.human_video_path = ""  # 追加：カメラで撮影した動画の保存パス

        # ウィジェットの作成
        self.video_label = tk.Label(root, text="Select a video to play (mp4 only):")
        self.video_label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Video", command=self.select_video)
        self.select_button.pack(pady=5)

        self.play_button = tk.Button(root, text="Play Video", command=self.play_and_capture)
        self.play_button.pack(pady=5)

        # 名前を入力するEntryウィジェットの作成
        self.name_entry_label = tk.Label(root, text="Enter your name:")
        self.name_entry_label.pack(pady=5)

        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        self.video_player = None
        self.camera_thread = None
        self.is_capturing = False

        # 開始時刻と終了時刻を表示するためのラベルを作成
        self.start_time_label = tk.Label(root, text="Video Start Time:")
        self.start_time_label.pack(pady=5)

        self.camera_start_time_label = tk.Label(root, text="Camera Start Time:")
        self.camera_start_time_label.pack(pady=5)

        self.end_time_label = tk.Label(root, text="End Time:")
        self.end_time_label.pack(pady=5)

    def select_video(self):
        # ファイル選択ダイアログを表示して動画ファイルを選択する
        self.video_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4")])
        
        print("取得したビデオパス：", self.video_path)
        if self.video_path:
            self.video_label.config(text=f"Selected Video: {os.path.basename(self.video_path)}")
        
        # パスの最後の要素を取得
        base_name = os.path.basename(str(self.video_path))

        # 動画名を取得(拡張子を除いた部分を取得)
        self.video_name = os.path.splitext(base_name)[0]
        
    def modify_video_path(self, name):
        # パスのディレクトリ部分とファイル名を分割
        directory, filename = os.path.split(self.video_path)

        # 新しいフォルダ名を追加して新しいパスを作成
        new_directory = os.path.join(directory, name).replace("\\", "/")

        # フォルダが存在しない場合は作成
        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        print("カメラ映像のpath：", new_directory)
        return new_directory

    def play_and_capture(self):
        # 動画再生とカメラ撮影を行うためのメソッド
        if not self.video_path:
            # 動画が選択されていない場合はエラーメッセージを表示して処理を終了する
            messagebox.showerror("Error", "Please select a video to play.")
            return

        # 名前を入力するEntryウィジェットから名前を取得
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

        # 動画再生とカメラ撮影を同時に開始するためのスレッドを作成
        self.is_capturing = True
        self.camera_thread = threading.Thread(target=self.capture_frames, args=(name,))
        self.camera_thread.start()

        # 開始時刻を記録
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_label.config(text="Video Start Time: " + start_time)
        self.camera_start_time_label.config(text="Camera Start Time: " + start_time)

        # 動画ファイルを再生
        self.play_video()

        # カメラ撮影スレッドが終了するまで待機
        self.is_capturing = False
        self.camera_thread.join()

        # 終了時刻を記録
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time_label.config(text="End Time: " + end_time)

        # 開始時刻と終了時刻をテキストファイルに保存
        self.save_times_to_file(name, start_time, end_time)

    def save_times_to_file(self, name, start_time, end_time):
        # ビデオファイルと同じ場所にテキストファイルを保存
        video_folder = os.path.dirname(self.video_path)
        output_filename = os.path.join(video_folder, f"{name}_video_times.txt")

        with open(output_filename, "w") as file:
            file.write(f"Video Start Time: {start_time}\n")
            file.write(f"Camera Start Time: {start_time}\n")
            file.write(f"End Time: {end_time}")
    


    def play_video(self):
        # 動画ファイルをオープンして再生するためのVideoCaptureを作成
        self.video_player = cv2.VideoCapture(self.video_path)

        # カメラ撮影のフレームレートを取得
        camera_fps = 30  # 例としてカメラ撮影のフレームレートを30fpsと仮定

        while self.video_player.isOpened():
            ret, frame = self.video_player.read()
            if not ret:
                break

            # 動画フレームを表示
            cv2.imshow("Video Player", frame)

            if cv2.waitKey(int(1000/camera_fps)) & 0xFF == 27:  # 'Esc'キーを押すと動画再生を中止
                break

        self.video_player.release()
        cv2.destroyAllWindows()

    def capture_frames(self, name):
        # カメラの縦横比
        camera_w = 1280
        camera_h = 720
        
        # カメラ解像度とフレームレートの設定
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_w)  # カメラの横解像度を設定
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_h)  # カメラの縦解像度を設定

        # カメラ撮影のフレームレートを取得
        camera_fps = capture.get(cv2.CAP_PROP_FPS)

        # 動画ファイルの保存準備
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.human_video_path = self.modify_video_path(name)
        print("動画保存path:", self.human_video_path)
        output_filename = os.path.join(self.human_video_path, f"{name}_{self.video_name}.avi").replace("\\", "/")
        print("動画保存path:", output_filename)
        out = cv2.VideoWriter(output_filename, fourcc, camera_fps, (camera_w, camera_h))

        while self.is_capturing:
            ret, frame = capture.read()
            if not ret:
                break

            # 動画フレームを保存
            out.write(frame)

        capture.release()
        out.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
import sys
import subprocess
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QMessageBox, QFileDialog
)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Stream video Youtube")
        self.setGeometry(100, 100, 500, 250)
        self.ffmpeg_process = None

        layout = QVBoxLayout()

        self.input_label = QLabel("File video:")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Chọn file video...")

        self.select_file_button = QPushButton("Chọn File")
        self.select_file_button.clicked.connect(self.select_file)

        self.stream_label = QLabel("Stream Key:")
        self.stream_field = QLineEdit()
        self.stream_field.setPlaceholderText("Nhập Stream Key...")

        self.start_button = QPushButton("Bắt đầu Live Stream")
        self.start_button.clicked.connect(self.start_stream)

        self.stop_button = QPushButton("Dừng Live Stream")
        self.stop_button.clicked.connect(self.stop_stream)
        self.stop_button.setEnabled(False)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.stream_label)
        layout.addWidget(self.stream_field)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, "ffmpeg.exe")
        else:
            return r"D:\Programs-ytdlp\ffmpeg.exe"

    def select_file(self):
        """ Mở hộp thoại chọn file """
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file video", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_path:
            self.input_field.setText(file_path)

    def run_ffmpeg(self, input_file, stream_key):
        """ Chạy FFmpeg trong luồng riêng """
        ffmpeg_path = self.get_ffmpeg_path()
        command = [
            ffmpeg_path, "-stream_loop", "-1", "-re", "-i", input_file,
            "-b:v", "6800k", "-b:a", "128k", "-bufsize", "6800k", "-maxrate", "6800k",
            "-preset", "fast", "-c:v", "libx264", "-c:a", "aac", "-f", "flv",
            f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        ]


        # Chạy FFmpeg mà không hiện cửa sổ CMD
        self.ffmpeg_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def start_stream(self):
        """ Bắt đầu live stream trong luồng riêng """
        input_file = self.input_field.text().strip()
        stream_key = self.stream_field.text().strip()

        if not input_file or not stream_key:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn file và nhập Stream Key!")
            return

        QMessageBox.information(self, "Thông báo", f"Live stream bắt đầu...\nFile: {input_file}\nStream Key: {stream_key}")

        # Chạy FFmpeg trong luồng riêng
        self.stream_thread = threading.Thread(target=self.run_ffmpeg, args=(input_file, stream_key))
        self.stream_thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_stream(self):
        """ Dừng live stream bằng cách kết thúc tiến trình FFmpeg """
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()  # Dừng tiến trình FFmpeg
            self.ffmpeg_process = None
            QMessageBox.information(self, "Thông báo", "Live stream đã dừng.")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec())

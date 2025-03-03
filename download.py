import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tqdm import tqdm
import base64
import certifi
import threading

# Chỉ định file cacert.pem
os.environ["SSL_CERT_FILE"] = os.path.join(os.path.dirname(__file__), "cacert.pem")
os.environ["REQUESTS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]
API_URL = "https://snapvideo.io/wp-json/aio-dl/video-data/"

# Hàm tính toán hash
def calculate_hash(url: str, salt: str) -> str:
    url_b64 = base64.b64encode(url.encode()).decode()
    salt_b64 = base64.b64encode(salt.encode()).decode()
    return f"{url_b64}L{len(url) + 1000}L{salt_b64}"

# Cập nhật log vào giao diện
def update_log(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)  # Tự động cuộn xuống dòng mới nhất
    root.update_idletasks()

# Hàm tải video
def download_video(video_url, save_path):
    """Tải video từ URL và hiển thị tiến trình"""
    response = requests.get(video_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    
    # if total_size == 0:
    #     update_log(f"❌ Không thể tải: {video_url} (Dung lượng không xác định)")
    #     return

    update_log(f"📥 Đang tải: {save_path} ({total_size / 1024:.2f} KB)")

    with open(save_path, "wb") as file, tqdm(
        desc=save_path,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))
    
    update_log(f"✅ Hoàn thành: {save_path}")

# Hàm lấy link tải video và tải xuống
def fetch_download_links():
    """Lấy link từ API và tải xuống"""
    urls = text_input.get("1.0", tk.END).strip().split("\n")
    save_folder = filedialog.askdirectory(title="Chọn thư mục lưu video")

    if not save_folder:
        return

    for url in urls:
        url = url.strip()
        if not url:
            continue

        hash_value = calculate_hash(url, 'aio-dl')
        update_log(f"🔍 Đang xử lý: {url}")

        try:
            response = requests.post(API_URL, data={"url": url, "token": "your_token", "hash": hash_value}, verify=True)
            data = response.json()
            videos = data.get("medias", [])

            if not videos:
                update_log(f"⚠️ Không tìm thấy video cho {url}")
                continue

            for video in videos:
                if video["extension"] == "mp4":
                    file_name = f"{video['quality']}.mp4"
                    save_path = os.path.join(save_folder, file_name)
                    
                    # Chạy tải video trên một luồng riêng
                    threading.Thread(target=download_video, args=(video["url"], save_path), daemon=True).start()

        except Exception as e:
            update_log(f"❌ Lỗi khi lấy dữ liệu: {e}")

    messagebox.showinfo("Đã đọc url", "Đang bắt đầu tải xuống!")

# Giao diện Tkinter
root = tk.Tk()
root.title("Tải Video")

tk.Label(root, text="Nhập danh sách URL (mỗi dòng một link):").pack()
text_input = tk.Text(root, height=10, width=50)
text_input.pack()

btn_download = tk.Button(root, text="Tải Video", command=lambda: threading.Thread(target=fetch_download_links, daemon=True).start())
btn_download.pack()

# Thêm vùng hiển thị log
log_text = scrolledtext.ScrolledText(root, height=10, width=60, state="normal")
log_text.pack()

root.mainloop()

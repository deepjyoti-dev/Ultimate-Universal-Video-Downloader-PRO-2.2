# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 18:05:48 2025

@author: deepj
"""

# -*- coding: utf-8 -*-
"""
Ultimate Universal Video Downloader PRO+ 2.1
Fixed and enhanced by ChatGPT (GPT-5)
Author: Deepjyoti Das
"""

# Requires:
# pip install yt-dlp instaloader requests Pillow

import os
import threading
from datetime import datetime
from queue import Queue
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import instaloader
import yt_dlp

# ------------------------- Setup -------------------------
BASE_PATH = "downloads"
PLATFORMS = ["YouTube", "Instagram", "Facebook"]
for p in PLATFORMS:
    os.makedirs(os.path.join(BASE_PATH, p), exist_ok=True)

L = instaloader.Instaloader(dirname_pattern=os.path.join(BASE_PATH, "Instagram"),
                            download_videos=True)

download_queue = Queue()
active_threads = []

# ------------------------- Utility Functions -------------------------
def timestamped_filename(name, ext):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
    return f"{now}_{safe_name}.{ext}"

def save_thumbnail(img_url, platform, name):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            folder = os.path.join(BASE_PATH, platform)
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, timestamped_filename(name, "jpg"))
            with open(filename, "wb") as f:
                f.write(response.content)
    except:
        pass

def show_thumbnail(img_url):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            from io import BytesIO
            img = Image.open(BytesIO(response.content))
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)
            thumbnail_label.configure(image=img_tk)
            thumbnail_label.image = img_tk
    except:
        pass

# ------------------------- YouTube (yt-dlp) -------------------------
def download_youtube(url, resolution="best"):
    try:
        status.set("Fetching YouTube info...")

        # Prepare output path
        output_path = os.path.join(BASE_PATH, "YouTube")

        # yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'progress_hooks': [on_yt_progress],
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'unknown')
            thumbnail = info_dict.get('thumbnail')
            duration = info_dict.get('duration', 0)
            uploader = info_dict.get('uploader', 'unknown')

            minutes, seconds = divmod(duration, 60)
            info.set(f"Title: {title}\nUploader: {uploader}\nDuration: {int(minutes)}m {int(seconds)}s")
            if thumbnail:
                show_thumbnail(thumbnail)
                save_thumbnail(thumbnail, "YouTube", title.replace(" ", "_"))

            status.set(f"Downloading in {resolution}p...")
            ydl.download([url])

        progress_bar['value'] = 0
        status.set("YouTube download completed!")

    except Exception as e:
        status.set(f"Error: {e}")

def on_yt_progress(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 1)
        downloaded = d.get('downloaded_bytes', 0)
        percent = int(downloaded / total * 100)
        progress_bar['value'] = percent
        status.set(f"Downloading: {percent}%")
    elif d['status'] == 'finished':
        status.set("Download finished, processing...")

# ------------------------- Instagram -------------------------
def download_instagram(url, username=None, password=None):
    try:
        if username and password:
            L.login(username, password)
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        info.set(f"Instagram Post by: {post.owner_username}\nLikes: {post.likes}\nComments: {post.comments}")
        show_thumbnail(post.url)
        save_thumbnail(post.url, "Instagram", post.owner_username)
        status.set("Downloading Instagram media...")
        L.download_post(post, target=os.path.join(BASE_PATH, "Instagram"))
        status.set("Instagram download completed!")
    except Exception as e:
        status.set(f"Error: {e}")

# ------------------------- Facebook -------------------------
def download_facebook(url, cookies=None):
    try:
        status.set("Downloading Facebook video...")
        headers = {'cookie': cookies} if cookies else {}
        response = requests.get(url, headers=headers, stream=True)
        filename = os.path.join(BASE_PATH, "Facebook", timestamped_filename("facebook_video", "mp4"))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        status.set("Facebook download completed!")
    except Exception as e:
        status.set(f"Error: {e}")

# ------------------------- Thread Worker -------------------------
def worker(url, ig_user=None, ig_pass=None, fb_cookie=None, resolution="best"):
    if "youtube.com" in url or "youtu.be" in url:
        download_youtube(url, resolution)
    elif "instagram.com" in url:
        download_instagram(url, ig_user, ig_pass)
    elif "facebook.com" in url:
        download_facebook(url, fb_cookie)
    else:
        status.set(f"Unsupported URL: {url}")
    download_queue.task_done()

def start_downloads():
    urls = url_text.get("1.0", END).strip().splitlines()
    ig_user = ig_username_entry.get().strip() or None
    ig_pass = ig_password_entry.get().strip() or None
    fb_cookie = fb_cookies_entry.get().strip() or None
    resolution = resolution_var.get()

    if not urls:
        messagebox.showwarning("Warning", "Please enter at least one URL!")
        return

    for url in urls:
        download_queue.put((url.strip(), ig_user, ig_pass, fb_cookie, resolution))

    for _ in range(min(5, download_queue.qsize())):
        t = threading.Thread(target=queue_worker_thread)
        t.daemon = True
        t.start()
        active_threads.append(t)

def queue_worker_thread():
    while not download_queue.empty():
        url, ig_user, ig_pass, fb_cookie, resolution = download_queue.get()
        worker(url, ig_user, ig_pass, fb_cookie, resolution)

# ------------------------- GUI -------------------------
root = Tk()
root.title("Ultimate Universal Video Downloader PRO+ 2.1")
root.geometry("750x720")

Label(root, text="Paste URLs (one per line):", font=("Arial", 12)).pack(pady=5)
url_text = Text(root, width=80, height=8)
url_text.pack(pady=5)

# Resolution Selector
Label(root, text="Select YouTube Resolution:").pack(pady=2)
resolution_var = StringVar(value="1080")
resolution_menu = ttk.Combobox(root, textvariable=resolution_var, values=["144", "240", "360", "480", "720", "1080", "2160", "best"], width=10, state="readonly")
resolution_menu.pack(pady=3)

# Instagram Login
Label(root, text="Instagram Username (optional):").pack(pady=2)
ig_username_entry = Entry(root, width=30)
ig_username_entry.pack()
Label(root, text="Instagram Password (optional):").pack(pady=2)
ig_password_entry = Entry(root, width=30, show="*")
ig_password_entry.pack()

# Facebook cookies
Label(root, text="Facebook Cookies (optional):").pack(pady=2)
fb_cookies_entry = Entry(root, width=50)
fb_cookies_entry.pack()

Button(root, text="Start Downloads", command=start_downloads, font=("Arial", 12), bg="green", fg="white").pack(pady=10)

# Info & Thumbnail
info = StringVar(value="Video info will appear here")
Label(root, textvariable=info, font=("Arial", 10), fg="blue").pack(pady=5)

thumbnail_label = Label(root)
thumbnail_label.pack(pady=5)

status = StringVar(value="Status: Idle")
Label(root, textvariable=status, font=("Arial", 10), fg="red").pack(pady=5)

progress_bar = ttk.Progressbar(root, length=700, mode='determinate')
progress_bar.pack(pady=5)

root.mainloop()

# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 10:51:39 2025

@author: deepj
"""

# Ultimate Universal Video Downloader PRO+ 2.2
# Requires: pip install pytube instaloader requests Pillow

import os
import requests
import threading
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pytube import YouTube
import instaloader
from io import BytesIO

# ------------------------- Setup -------------------------
BASE_PATH = "downloads"
PLATFORMS = ["YouTube", "Instagram", "Facebook"]
for p in PLATFORMS:
    os.makedirs(os.path.join(BASE_PATH, p), exist_ok=True)

L = instaloader.Instaloader(dirname_pattern=os.path.join(BASE_PATH, "Instagram"),
                            download_videos=True)

download_threads = {}
pause_flags = {}
cancel_flags = {}
progress_vars = {}

# ------------------------- Utility Functions -------------------------
def timestamped_filename(name, ext):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{now}_{name}.{ext}"

def save_thumbnail(img_url, platform, name):
    try:
        response = requests.get(img_url)
        img_data = response.content
        folder = os.path.join(BASE_PATH, platform)
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, timestamped_filename(name, "jpg"))
        with open(filename, "wb") as f:
            f.write(img_data)
    except:
        pass

def show_thumbnail(img_url):
    try:
        response = requests.get(img_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        thumbnail_label.configure(image=img_tk)
        thumbnail_label.image = img_tk
    except:
        pass

def update_progress_bar(stream_or_url, chunk, bytes_remaining):
    total = getattr(stream_or_url, "filesize", 1)
    percent = int((total - bytes_remaining) / total * 100)
    if stream_or_url in progress_vars:
        progress_vars[stream_or_url].set(percent)

# ------------------------- Download Functions -------------------------
def download_youtube(url):
    try:
        yt = YouTube(url, on_progress_callback=update_progress_bar)
        show_thumbnail(yt.thumbnail_url)
        save_thumbnail(yt.thumbnail_url, "YouTube", yt.title.replace(" ", "_"))
        status_label[url].config(text="Downloading", fg="green")
        stream = yt.streams.get_highest_resolution()
        download_threads[url] = stream
        progress_vars[stream] = progress_bars[url]
        filename = os.path.join(BASE_PATH, "YouTube", timestamped_filename(yt.title.replace(" ", "_"), "mp4"))
        stream.download(output_path=os.path.dirname(filename), filename=os.path.basename(filename))
        status_label[url].config(text="Completed", fg="blue")
        progress_vars[stream].set(100)
    except Exception as e:
        status_label[url].config(text="Error", fg="red")

def download_instagram(url, username=None, password=None):
    try:
        if username and password:
            L.login(username, password)
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        show_thumbnail(post.url)
        save_thumbnail(post.url, "Instagram", post.owner_username)
        status_label[url].config(text="Downloading", fg="green")
        L.download_post(post, target=os.path.join(BASE_PATH, "Instagram"))
        status_label[url].config(text="Completed", fg="blue")
    except Exception as e:
        status_label[url].config(text="Error", fg="red")

def download_facebook(url, cookies=None):
    try:
        status_label[url].config(text="Downloading", fg="green")
        headers = {'cookie': cookies} if cookies else {}
        response = requests.get(url, headers=headers, stream=True)
        filename = os.path.join(BASE_PATH, "Facebook", timestamped_filename("facebook_video", "mp4"))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                if pause_flags.get(url, False):
                    while pause_flags.get(url, False):
                        threading.Event().wait(0.5)
                if cancel_flags.get(url, False):
                    status_label[url].config(text="Cancelled", fg="orange")
                    return
        status_label[url].config(text="Completed", fg="blue")
    except Exception as e:
        status_label[url].config(text="Error", fg="red")

# ------------------------- GUI Functions -------------------------
def add_url():
    url = url_entry.get().strip()
    if url:
        queue_list.insert(END, url)
        progress_var = IntVar()
        progress_vars[url] = progress_var
        bar = ttk.Progressbar(queue_frame, length=300, mode='determinate', variable=progress_var)
        bar.pack()
        progress_bars[url] = progress_var
        lbl = Label(queue_frame, text="Queued", fg="gray")
        lbl.pack()
        status_label[url] = lbl

def start_download(url):
    if "youtube.com" in url or "youtu.be" in url:
        threading.Thread(target=download_youtube, args=(url,)).start()
    elif "instagram.com" in url:
        threading.Thread(target=download_instagram, args=(url, ig_user.get(), ig_pass.get())).start()
    elif "facebook.com" in url:
        threading.Thread(target=download_facebook, args=(url, fb_cookie.get())).start()
    else:
        status_label[url].config(text="Unsupported", fg="red")

def start_all_downloads():
    for url in queue_list.get(0, END):
        start_download(url)

def pause_download(url):
    pause_flags[url] = True
    status_label[url].config(text="Paused", fg="orange")

def resume_download(url):
    pause_flags[url] = False
    status_label[url].config(text="Downloading", fg="green")

def cancel_download(url):
    cancel_flags[url] = True
    status_label[url].config(text="Cancelled", fg="red")

# ------------------------- GUI -------------------------
root = Tk()
root.title("Ultimate Video Downloader PRO+ 2.2")
root.geometry("800x750")

Label(root, text="Paste URL:", font=("Arial", 12)).pack()
url_entry = Entry(root, width=80)
url_entry.pack(pady=5)
Button(root, text="Add to Queue", command=add_url, bg="blue", fg="white").pack(pady=5)

# Queue frame
queue_frame = Frame(root)
queue_frame.pack(pady=5)

# Instagram & Facebook login
Label(root, text="Instagram Username (optional):").pack()
ig_user = Entry(root, width=30)
ig_user.pack()
Label(root, text="Instagram Password (optional):").pack()
ig_pass = Entry(root, width=30, show="*")
ig_pass.pack()
Label(root, text="Facebook Cookies (optional):").pack()
fb_cookie = Entry(root, width=50)
fb_cookie.pack()

Button(root, text="Start All Downloads", command=start_all_downloads, bg="green", fg="white").pack(pady=10)

# Video info & thumbnail
thumbnail_label = Label(root)
thumbnail_label.pack(pady=5)

progress_bars = {}
status_label = {}

root.mainloop()

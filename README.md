🎬 Ultimate Universal Video Downloader PRO+ 2.2

A Python-based, multi-platform video downloader with a professional GUI.
Supports YouTube, Instagram, and Facebook, including public and private content (login or cookies required).

✨ Features

📥 Drag-and-Drop URL Queue — Add multiple video URLs easily

⏱️ Individual Progress Bars — Track downloads per video

⏸️ Pause, Resume & Cancel — Control downloads individually

🖼️ Thumbnail Preview — Automatically displayed on download start

📝 Metadata Display — Shows title, author, duration, likes/comments when available

🗂️ Organized Folders — Separate folders per platform with date-time prefixed filenames

⚡ Concurrent Downloads — Efficiently download multiple videos simultaneously

🧩 Requirements

Python 3.8+ recommended

Install required packages:

pip install pytube instaloader requests Pillow

📂 Folder Structure
downloads/
├── YouTube/
├── Instagram/
├── Facebook/


Videos saved into platform-specific folders

Filenames prefixed with date-time to avoid overwriting

Thumbnails saved automatically in the same folder

⚙️ Usage
Launch the Application
python video_downloader_PRO_plus_2_2.py

Add URLs

Paste video URL into input box

Click Add to Queue

Repeat for multiple URLs

Configure Credentials (Optional)

Instagram: Username/password for private videos

Facebook: Cookies for private videos

Start Downloads

Click Start All Downloads

Each video has its own progress bar and status

Pause, Resume, Cancel per video

Thumbnail Preview

Automatically displays when download starts

📝 Notes

Instagram private videos require login credentials

Facebook private videos require cookies

YouTube videos download at highest resolution by default

Downloads are threaded, allowing concurrent processing

Progress bars update in real-time

🔮 Future Improvements

Right-click context menu for individual video control

Real-time metadata display (views, likes, comments) in queue

Drag-and-drop URLs directly from browser

System tray integration with notifications

Commercial-grade GUI polish with separate panels for queue, info, and controls

⚠️ Troubleshooting

Download fails: Check URL, credentials/cookies, and internet connection

Python errors: Ensure packages installed and Python 3.8+ used

Video not playing: Use supported media players (MP4 recommended)

🏷️ Tags

#python #gui #video-downloader #youtube #instagram #facebook #pytube #instaloader #desktopapp

🧑‍💻 Author

Deepjyoti Das
🔗 https://www.linkedin.com/in/deepjyotidas1

💻 GitHub

# Nexus DL - Universal Media Downloader

Nexus DL is a high-performance, aesthetically pleasing media downloader built with FastAPI and `yt-dlp`. It supports downloading videos from **YouTube**, **TikTok**, and **Instagram** with ease, featuring automated cleanup and optional cloud storage.

## ✨ Features

- **Multi-Platform Support**: Download from 1000+ sites including YouTube, TikTok, and Instagram.
- **FastAPI Backend**: Efficient, asynchronous processing with background task handling.
- **Modern UI**: Dark-mode, glassmorphic interface with real-time progress bars.
- **Auto-Cleanup**: Automatically purges downloaded files after a configurable time to save storage.
- **S3 Integration**: Optional automatic upload to AWS S3 or S3-compatible storage (Cloudflare R2, etc.).
- **Smart Fallback**: Automatically detects if FFmpeg is missing and falls back to best-available single format.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, yt-dlp, APScheduler
- **Frontend**: Vanilla JS, CSS3 (Glassmorphism), HTML5
- **Storage**: Local Filesystem / AWS S3

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.8+**
- **FFmpeg**: Required for merging high-quality video and audio (1080p+).
  - *Windows*: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html).

### 2. Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd downloader
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

Create a `.env` file in the root directory (you can copy from `.env.example`):

```env
DOWNLOAD_DIR=downloads
S3_ENABLED=false

# Cleanup (in seconds)
CLEANUP_INTERVAL_SECONDS=3600
FILE_RETENTION_SECONDS=3600

# FFmpeg Path (if not in system PATH)
FFMPEG_PATH=C:/path/to/ffmpeg.exe
```

### 4. Running the App

```bash
python main.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## 📁 Project Structure

- `main.py`: FastAPI entry point and background task management.
- `downloader.py`: `yt-dlp` wrapper for media extraction.
- `storage.py`: Handles local file management and S3 uploads.
- `config.py`: Centralized configuration using Pydantic.
- `static/`: Frontend assets (UI).
- `downloads/`: Temporary local media storage.

## ⚖️ License

MIT License. See [LICENSE](LICENSE) for more information.

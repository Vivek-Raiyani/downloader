import yt_dlp
import os
import logging
from typing import Callable, Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self, download_path: str = settings.DOWNLOAD_DIR):
        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def download(self, url: str, progress_hook: Callable[[Dict[str, Any]], None] = None) -> Dict[str, Any]:
        """
        Downloads media from the given URL.
        """
        # Check if ffmpeg is available
        import subprocess
        ffmpeg_cmd = settings.FFMPEG_PATH or 'ffmpeg'
        ffmpeg_available = False
        try:
            subprocess.run([ffmpeg_cmd, '-version'], capture_output=True, check=True)
            ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"FFmpeg not found at '{ffmpeg_cmd}'. Falling back to single format download (might be lower quality).")

        ydl_opts = {
            'ffmpeg_location': settings.FFMPEG_PATH if settings.FFMPEG_PATH else None,
            'format': 'bestvideo+bestaudio/best' if ffmpeg_available else 'best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4' if ffmpeg_available else None,
            'progress_hooks': [progress_hook] if progress_hook else [],
            'quiet': True,
            'no_warnings': True,
            # TikTok/Instagram specific options can be added here
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
        }

        # For Instagram/TikTok, cookies might be needed for private/restricted content
        # ydl_opts['cookiesfrombrowser'] = ('chrome',) 

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # If merged, the extension might change to mp4 as per merge_output_format
                base, _ = os.path.splitext(filename)
                final_filename = f"{base}.mp4"
                
                return {
                    "success": True,
                    "title": info.get('title'),
                    "filepath": final_filename,
                    "filename": os.path.basename(final_filename),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "platform": info.get('extractor_key')
                }
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {"success": False, "error": str(e)}

def get_downloader():
    return MediaDownloader()

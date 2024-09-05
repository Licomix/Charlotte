import logging
import os
import asyncio

import yt_dlp
from yt_dlp.utils import sanitize_filename

from utils import update_metadata
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

class YouTubeDownloader:
    """
    A class for downloading videos and audio from YouTube using yt-dlp.

    Attributes:
    ----------
    output_path : str
        Directory where the downloaded files will be saved.

    Methods:
    -------
    download(url: str, format: str)
        Download a media file (either video or audio) from a given YouTube URL.

    download_video(url: str)
        Download a video from a given YouTube URL.

    download_music(url: str)
        Download audio from a given YouTube URL.
    """

    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the YouTubeDownloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

    async def download(self, url: str, format: str):
        """
        Download a media file (video or audio) based on the format.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio).

        Returns:
        -------
        Any
            Returns the result of the `download_video` or `download_music` methods or None if an error occurs.
        """
        try:
            if format == "media":
                return await self.download_video(url)
            elif format == "audio":
                return await self.download_music(url)
            else:
                logging.error(f"Unsupported format: {format}")
                return None
        except yt_dlp.DownloadError as e:
            logging.error(f"Download error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return None

    async def download_video(self, url: str):
        """
        Download a video from YouTube.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.

        Returns:
        -------
        tuple or None
            Returns a tuple containing the MediaGroup object, video title, and list of filenames if successful,
            or None if an error occurs.
        """
        try:
            options = {
                "format": "bv*[filesize < 50M][ext=mp4] + ba[ext=m4a] / w*[filesize < 50M]",
                "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "video")
                filename = ydl.prepare_filename(info_dict)

                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder(caption=title)
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                if os.path.exists(filename):
                    return media_group, title, [filename]
        except Exception as e:
            logging.error(f"Error downloading YouTube video: {str(e)}")
            return None

    async def download_music(self, url: str):
        """
        Download audio from YouTube.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.

        Returns:
        -------
        tuple or None
            Returns a tuple containing the audio filename and thumbnail filename if successful,
            or None if an error occurs.
        """
        try:
            options = {
                "format": "m4a/bestaudio/best",
                "writethumbnail": True,
                "outtmpl": f"{self.output_path}/{sanitize_filename('%(title)s')}",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                    }
                ],
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "audio")
                author = info_dict.get("uploader", "unknown")

                audio_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.mp3")
                thumbnail_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.webp")

                await asyncio.to_thread(ydl.download, [url])

                update_metadata(audio_filename, title=title, artist=author)

                if os.path.exists(audio_filename):
                    return audio_filename, thumbnail_filename
        except Exception as e:
            logging.error(f"Error downloading YouTube Audio: {str(e)}")
            return None

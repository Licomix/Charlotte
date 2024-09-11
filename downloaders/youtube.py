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
        Choose which function use to download.

    _download_video(url: str)
        Download a video from a given YouTube URL.

    _download_music(url: str)
        Download an audio from a given YouTube URL.
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
        self.yt_dlp_video_options = {
                "format": "bv*[filesize < 50M][ext=mp4] + ba[ext=m4a] / w*[filesize < 50M]",
                "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
            }
        self.yt_dlp_audio_options = {
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

    async def download(self, url: str, format: str):
        """
        Download a media file (video or audio) based on the format.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio).

        Yields:
        -------
        AsyncGenerator
            Returns an async generator yielding video, audio and cover filenames or None if an error occurs.
        """
        try:
            if format == "media":
                async for result in self._download_video(url):
                    yield result
            elif format == "audio":
                async for result in self._download_music(url):
                    yield result
            else:
                logging.error(f"Unsupported format: {format}")
                yield None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None

    async def _download_video(self, url: str):
        """
        Download a video from YouTube.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.

        Yields:
        -------
        tuple
            Yields a tuple containing the MediaGroup object, video title, and list of filenames
        """
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_video_options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "video")
                filename = ydl.prepare_filename(info_dict)

                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder(caption=title)
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                if os.path.exists(filename):
                    yield media_group, title, [filename]
        except Exception as e:
            logging.error(f"Error downloading YouTube video: {str(e)}")
            yield None

    async def _download_music(self, url: str):
        """
        Download audio from YouTube.

        Parameters:
        ----------
        url : str
            The YouTube video URL to download.

        Yields:
        -------
        tuple
            Yields a tuple containing the audio filename and thumbnail filename
        """
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_audio_options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "audio")
                author = info_dict.get("uploader", "unknown")

                audio_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.mp3")
                thumbnail_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.webp")

                await asyncio.to_thread(ydl.download, [url])

                update_metadata(audio_filename, title=title, artist=author)

                if os.path.exists(audio_filename):
                    yield audio_filename, thumbnail_filename
        except Exception as e:
            logging.error(f"Error downloading YouTube Audio: {str(e)}")
            yield None

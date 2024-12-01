import asyncio
import logging
import os

import yt_dlp
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder


class TikTokDownloader:
    """
    A class for downloading videos and audio from TikTok using yt-dlp.

    Attributes:
    ----------
    output_path : str
        Directory where the downloaded files will be saved.

    Methods:
    -------
    download(url: str, format: str)
        Choose which function use to download.

    _download_video(url: str)
        Download a video from a given TikTok URL.

    _download_music(url: str)
        Download an audio from a given TikTok URL.
    """

    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the TikTokDownloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.yt_dlp_video_options = {
            "format": "mp4",
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        }
        # self.yt_dlp_audio_options = {
        #         "format": "m4a/bestaudio/best",
        #         "writethumbnail": True,
        #         "outtmpl": f"{self.output_path}/{sanitize_filename('%(title)s')}",
        #         "postprocessors": [
        #             {
        #                 "key": "FFmpegExtractAudio",
        #                 "preferredcodec": "mp3",
        #             }
        #         ],
        #     }

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
            # elif format == "audio":
            #     async for result in self._download_music(url):
            #         yield result
            else:
                logging.error(f"Unsupported format: {format}")
                yield None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None

    async def _download_video(self, url):
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_video_options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                filename = ydl.prepare_filename(info_dict)
                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder()
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                if os.path.exists(filename):
                    yield media_group, filename
        except Exception as e:
            logging.error(f"Error downloading Tiktok video: {str(e)}")
            yield None, None
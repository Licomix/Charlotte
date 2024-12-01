import logging
import os
import asyncio

import yt_dlp

from utils import truncate_string
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder


class BilibiliDownloader:
    """
        A class for downloading videos and audio from BiliBili using yt-dlp.

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
        Initialize the BiliBili downloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.yt_dlp_video_options = {
                "format": "bv*[filesize < 50M][ext=mp4] + ba/w",
                "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
            }

    async def download(self, url: str, format: str):
        """
        Download a media file (video or audio) based on the format.

        Parameters:
        ----------
        url : str
            The BiliBili video URL to download.
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

    async def _download_video(self, url: str):
        """
        Downloads a video from Bilibili using yt-dlp and saves it to the specified output path.

        Parameters:
        ----------
        url : str
            The URL of the Bilibili video to download.
        output_path : str, optional
            The directory where the downloaded video will be saved (default is "other/downloadsTemp").
        format : str, optional
            The format of the download, default is "media". Not used in this implementation.

        Returns:
        -------
        tuple or int
            Returns a tuple containing the title of the video and the file path of the downloaded video if successful.
            Returns None if an error occurs.
        """
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_video_options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "video")
                filename = ydl.prepare_filename(info_dict)

                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder(caption=truncate_string(title))
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                if os.path.exists(filename):
                    yield media_group, [filename]
        except yt_dlp.DownloadError as e:
            logging.error(f"Error downloading YouTube video: {str(e)}")
            yield None, None
        except Exception as e:
            logging.error(f"Error downloading YouTube video: {str(e)}")
            yield None, None

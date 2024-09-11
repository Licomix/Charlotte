import asyncio
import logging
import os
import urllib.request
import re

import aiohttp
import yt_dlp
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import BeautifulSoup


class PinterestDownloader:
    """
    A class for downloading media from Pinterest using parser.

    Attributes:
    ----------
    output_path : str
        Directory where the downloaded files will be saved.

    Methods:
    -------
    download(url: str, format: str)
        Choose which function use to download.

    _download_media(url: str)
        Download a video from a given Instagram URL.

    """

    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the Pinterest downloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

    async def download(self, url: str, format: str):
        """
        Download a media file based on the format.

        Parameters:
        ----------
        url : str
            The Instagram media URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio). Media only.

        Yields:
        -------
        AsyncGenerator
            Returns an async generator yielding media_group or None if an error occurs.
        """
        try:
            if format == "media":
                async for result in self._download_media(url):
                    yield result
            else:
                logging.error(f"Unsupported format: {format}")
                yield None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None

    async def _download_media(self, url: str, output_path: str = "other/downloadsTemp", format: str = "media"):
        """
        Downloads media (photos or videos) from a Pinterest post and saves them to the specified output path.
        Attempts to download the media first using yt-dlp, and if unsuccessful, falls back to scraping the media from the page.

        Parameters:
        ----------
        url : str
            The URL of the Pinterest post to download.
        output_path : str, optional
            The directory where the downloaded media will be saved (default is "other/downloadsTemp").
        format : str, optional
            The format of the media to download, default is "media". Currently not used for logic branching.

        Yields:
        -------
        tuple
            Yields a tuple containing:
            - media_group: A media group object containing all the downloaded media (photos or videos).
            - caption: An empty string, as Pinterest posts don't have captions by default.
            - file_path: The path to the downloaded file.
        """
        async with aiohttp.ClientSession() as sesion:
            async with sesion.get(url) as link:
                url = str(link.url)

        try:
            parts = url.split("/")
            filename = parts[-3]
            options = {
                "outtmpl": f"{output_path}/{filename}.%(ext)s",
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                file_path = ydl.prepare_filename(info_dict)
                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder()
                media_group.add_video(media=FSInputFile(file_path), type=InputMediaType.VIDEO)

                yield media_group, " ", file_path

        except Exception:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    status_code = response.status

                if status_code == 200:
                    soup = BeautifulSoup(html, "html.parser")
                    link = soup.find("img")

                    if link:
                        content_url = link["src"]

                        parts = content_url.split("/")
                        filename = parts[-1]
                        file_path = os.path.join(output_path, filename)
                        content_url = re.sub(r'/\d+x', '/originals', content_url)

                        try:
                            urllib.request.urlretrieve(content_url, file_path)
                        except Exception:
                            content_url = re.sub(r'\.jpg$', '.png', content_url)
                            urllib.request.urlretrieve(content_url, file_path)

                        media_group = MediaGroupBuilder()
                        media_group.add_photo(media=FSInputFile(file_path), type=InputMediaType.PHOTO)

                        yield media_group, " ", file_path

                    else:
                        logging.error('Class "img" not found')
                        yield None
                else:
                    logging.error(f"Error response status code {status_code}")
                    yield None

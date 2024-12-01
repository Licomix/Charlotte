import json
import logging
import os

import aiofiles
import aiohttp
import yarl
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from instagrapi import Client

from config.secrets import INSTA_PASSWORD, INSTA_USERNAME

from utils import truncate_string


class InstagramDownloader:
    """
        A class for downloading media from Instagram using instagrapi.

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
        Initialize the Instagram downloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.client = Client()
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
            # elif format == "audio":
            #     async for result in self._download_music(url):
            #         yield result
            else:
                logging.error(f"Unsupported format: {format}")
                yield None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None

    async def _download_media(self, url: str):
        """
        Downloads media (photos or videos) from an Instagram post and saves them to the specified output path.
        Supports both individual photos/videos and carousel posts.

        Parameters:
        ----------
        url : str
            The URL of the Instagram post to download.
        output_path : str, optional
            The directory where the downloaded media will be saved (default is "other/downloadsTemp").
        format : str, optional
            The format of the media to download, default is "media". Not used in this implementation.

        Returns:
        -------
        tuple
            Returns a tuple containing:
            - media_group: A media group object containing all the downloaded media (photos or videos).
            - caption: The caption of the Instagram post.
            - temp_medias: A list of file paths to the downloaded media.
        """
        try:
            # Check user login
            try:
                user_info = self.client.user_info(str(self.client.user_id))
            except Exception as e:
                self._instagram_login()

            media_urls = []
            media_types = []
            temp_medias = []

            media_pk = self.client.media_pk_from_url(url)
            media = self.client.media_info(media_pk)

            media_group = MediaGroupBuilder(caption=truncate_string(media.caption_text))

            if media.media_type == 8:  # GraphSidecar (multiple photos or videos)
                for i, resource in enumerate(media.resources):
                    media_urls.append(resource.thumbnail_url if resource.media_type == 1 else resource.video_url)
                    media_types.append("photo" if resource.media_type == 1 else "video")
            elif media.media_type == 1:  # GraphImage (single image)
                media_urls.append(media.thumbnail_url)
                media_types.append("photo")
            elif media.media_type == 2:  # GraphVideo (single video)
                media_urls.append(media.video_url)
                media_types.append("video")

            for i, (media_url, media_type) in enumerate(zip(media_urls, media_types)):
                filename_ext = ".jpg" if media_type == "photo" else ".mp4"
                media_filename = os.path.join(self.output_path, f"{media_pk}_{i}{filename_ext}")

                async with aiohttp.ClientSession() as session:
                    async with session.request("GET", url=yarl.URL(str(media_url), encoded=True)) as response:
                        if response.status == 200:
                            async with aiofiles.open(media_filename, "wb") as file:
                                await file.write(await response.read())
                                temp_medias.append(media_filename)
                            if media_type == "photo":
                                media_group.add_photo(media=FSInputFile(media_filename), type=InputMediaType.PHOTO)
                            else:
                                media_group.add_video(media=FSInputFile(media_filename), type=InputMediaType.VIDEO)
                        else:
                            print(f"Failed to download media: {media_url}")

            yield media_group, temp_medias

        except Exception as e:
            logging.error(f"Error downloading Instagram media: {str(e)}")
            yield None, None

    def _instagram_login(self):
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
            self.client.set_settings(cookies)
        else:
            self.client.login(INSTA_USERNAME, INSTA_PASSWORD)
            with open("cookies.json", "w") as f:
                json.dump(self.client.get_settings(), f)
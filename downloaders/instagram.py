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


async def download_instagram(url: str, output_path: str = "other/downloadsTemp", format: str = "media"):
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

    int
        Returns 1 if an error occurs during the download process.

    Exceptions:
    -----------
    Exception
        Logs and returns an error if any exception occurs during the downloading process.
    """
    try:
        client = Client()

        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
            client.set_settings(cookies)
        else:
            client.login(INSTA_USERNAME, INSTA_PASSWORD)
            with open("cookies.json", "w") as f:
                json.dump(client.get_settings(), f)

        media_urls = []
        media_types = []
        temp_medias = []

        media_pk = client.media_pk_from_url(url)
        media = client.media_info(media_pk)

        media_group = MediaGroupBuilder(caption=media.caption_text)

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
            media_filename = os.path.join(output_path, f"{media_pk}_{i}{filename_ext}")

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

        return media_group, media.caption_text, temp_medias

    except Exception as e:
        print(e)
        logging.error(f"Error downloading Instagram media: {str(e)}")
        return 1

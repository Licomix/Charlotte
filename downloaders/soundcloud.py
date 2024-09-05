import logging
import os
import asyncio

import yt_dlp
from yt_dlp.utils import sanitize_filename

from utils.get_soundcloud_author import get_soundcloud_author
from utils import update_metadata


async def download_soundcloud(url: str, output_path: str = "other/downloadsTemp", format: str = "audio"):
    """
    Downloads a SoundCloud track from the given URL and saves it to the specified output path.

    Args:
        url (str): The URL of the SoundCloud track to download.
        output_path (str, optional): The directory where the downloaded file and thumbnail will be saved.
            Defaults to "other/downloadsTemp".
        format (str, optional): The format in which to save the audio. Defaults to "audio".

    Returns:
        tuple or None: A tuple containing the file paths of the downloaded audio and thumbnail images if
            the download is successful. Returns None if there is an error during the download process.

    Raises:
        Exception: If there is an error during the download process, it will be logged, and the function
            will return None.
    """
    options = {
        "format": "m4a/bestaudio/best",
        "writethumbnail": True,
        "outtmpl": f"{output_path}/{sanitize_filename('%(title)s')}",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            },
            {
                "key": "FFmpegThumbnailsConvertor",
                "format": "jpg",
            },
        ],
    }

    try:
        ydl = yt_dlp.YoutubeDL(options)
        info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
        ydl_title = info_dict.get("title")
        await asyncio.to_thread(ydl.download, [url])

        artist, title = await get_soundcloud_author(url)
        audio_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.mp3")
        thumbnail_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.jpg")

        update_metadata(audio_filename, title, artist)

        if os.path.exists(audio_filename) and os.path.exists(thumbnail_filename):
            return audio_filename, thumbnail_filename

    except Exception as e:
        logging.error(f"Error downloading : {str(e)}")
        return None

import json
import logging
import os
import asyncio
import urllib.request

import yt_dlp
from yt_dlp.utils import sanitize_filename

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
    """
    options = {
        "format": "bestaudio",
        "writethumbnail": True,
        "outtmpl": f"{output_path}/{sanitize_filename('%(title)s')}",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            },
        ],
    }

    try:
        ydl = yt_dlp.YoutubeDL(options)
        info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
        title = info_dict.get("title")
        artist = info_dict.get("uploader")
        thumbnails = info_dict.get("thumbnails", [])
        cover_url = next((thumbnail["url"] for thumbnail in thumbnails if thumbnail.get("width") == 500), None)

        with open("temp.json", "w") as f:
            json.dump(info_dict, f)

        await asyncio.to_thread(ydl.download, [url])

        audio_filename = os.path.join(output_path, f"{sanitize_filename(title)}.mp3")
        cover_filename = os.path.join(output_path, f"{sanitize_filename(title)}.jpg")

        urllib.request.urlretrieve(cover_url, cover_filename)

        update_metadata(audio_filename, title, artist)

        if os.path.exists(audio_filename) and os.path.exists(cover_filename):
            return audio_filename, cover_filename

    except Exception as e:
        logging.error(f"Error downloading : {str(e)}")
        return None

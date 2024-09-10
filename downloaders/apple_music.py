import asyncio
import logging
import os
import urllib.request

import yt_dlp
from yt_dlp.utils import sanitize_filename

from utils import get_applemusic_author, update_metadata, search_music


async def download_apple_music(url: str, output_path: str = "other/downloadsTemp", format: str = "audio"):
    """
    Downloads audio from YouTube based on a Apple Music track's artist and title.

    Given a Apple Music URL, the function retrieves the artist and title, searches for a corresponding YouTube video,
    and downloads the audio if the duration is 10 minutes or less. After the download, it updates the metadata and
    adds the cover image from the Spotify track.

    Parameters:
    ----------
    url : str
        The Apple Music URL to retrieve artist and track information.
    output_path : str, optional
        The directory where the downloaded files will be saved (default is "other/downloadsTemp").
    format : str, optional
        The format of the download, default is "audio".

    Returns:
    -------
    tuple or None
        Returns a tuple containing the audio filename and cover image filename if successful,
        or None if an error occurs.
    """
    try:
        artist, title, cover_url = await get_applemusic_author(url)

        video_link = await search_music(artist, title)

        options = {
            "format": "m4a/bestaudio/best",
            "outtmpl": f"{output_path}/{sanitize_filename('%(title)s')}",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                },
            ],
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, video_link, download=False)
            ydl_title = info_dict.get("title", "unknown_title")
            logging.info(f"Downloading: {ydl_title}")

            await asyncio.to_thread(ydl.download, [video_link])

        audio_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.mp3")
        cover_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.jpg")

        urllib.request.urlretrieve(cover_url, cover_filename)

        update_metadata(audio_filename, artist, title, cover_filename)

        if audio_filename and cover_filename:
            return audio_filename, cover_filename

    except Exception as e:
        logging.error(f"Error downloading YouTube Audio: {e}", exc_info=True)

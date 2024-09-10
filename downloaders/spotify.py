import logging
import os
import asyncio

import yt_dlp
from yt_dlp.utils import sanitize_filename
import urllib.request

from utils import update_metadata, get_spotify_author, search_music


async def download_spotify(url: str, output_path: str = "other/downloadsTemp", format: str = "audio"):
    """
    Downloads audio from YouTube based on a Spotify track's artist and title.

    Given a Spotify URL, the function retrieves the artist and title, searches for a corresponding YouTube video,
    and downloads the audio if the duration is 10 minutes or less. After the download, it updates the metadata and
    adds the cover image from the Spotify track.

    Parameters:
    -----------
    url : str
        The Spotify track URL.
    output_path : str, optional
        Directory where the downloaded audio and cover image will be saved (default is "other/downloadsTemp").
    format : str, optional
        Format of the media to download. For this function, only "audio" is supported (default is "audio").

    Returns:
    --------
    tuple
        Returns a tuple containing:
        - audio_filename (str): The path to the downloaded audio file.
        - cover_filename (str): The path to the downloaded cover image.
    """
    artist, title, cover_url = await get_spotify_author(url)

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

    try:
        ydl = yt_dlp.YoutubeDL(options)

        info_dict = await asyncio.to_thread(ydl.extract_info, video_link, download=False)
        ydl_title = info_dict.get("title")

        await asyncio.to_thread(ydl.download, [video_link])

        audio_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.mp3")
        cover_filename = os.path.join(output_path, f"{sanitize_filename(ydl_title)}.jpg")

        urllib.request.urlretrieve(cover_url, cover_filename)

        update_metadata(audio_filename, artist, title, cover_filename)

        if os.path.exists(audio_filename) and os.path.exists(cover_filename):
            return audio_filename, cover_filename

    except Exception as e:
        logging.error(f"Error downloading YouTube Audio: {str(e)}")
        return None
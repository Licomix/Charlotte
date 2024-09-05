import logging
import os
import asyncio

import yt_dlp
from yt_dlp.utils import sanitize_filename
import urllib.request
from youtubesearchpython import VideosSearch

from utils import update_metadata
from utils import get_spotify_author


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

    None
        Returns None if the audio or cover file cannot be downloaded or if there's an error during the process.

    Exceptions:
    -----------
    Exception
        Logs the error message if an error occurs during the YouTube video search, download, or metadata update.

    """
    artist, title, cover_url = await get_spotify_author(url)

    videos_search = VideosSearch(f"{artist} - {title}", limit=10)
    video_results = await asyncio.to_thread(videos_search.result)

    for video_result in video_results["result"]:
        video_link = video_result["link"]
        duration_str = video_result["duration"]

        duration_parts = duration_str.split(":")
        if len(duration_parts) == 3:
            duration = (
                int(duration_parts[0]) * 3600
                + int(duration_parts[1]) * 60
                + int(duration_parts[2])
            )
        elif len(duration_parts) == 2:
            duration = int(duration_parts[0]) * 60 + int(duration_parts[1])
        else:
            duration = int(duration_parts[0])

        if int(duration) <= 600:
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

                update_metadata(audio_file=audio_filename, artist=artist, title=title, cover_file=cover_filename)

                if os.path.exists(audio_filename) and os.path.exists(cover_filename):
                    return audio_filename, cover_filename

            except Exception as e:
                logging.error(f"Error downloading YouTube Audio: {str(e)}")
                return None

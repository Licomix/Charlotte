import asyncio
import logging
import os
import urllib

import yt_dlp
from youtubesearchpython import VideosSearch
from yt_dlp.utils import sanitize_filename

from utils import get_applemusic_author, update_metadata


def parse_duration(duration_str: str) -> int:
    """
    Parses a duration string in the format of HH:MM:SS, MM:SS, or SS and converts it into total seconds.

    Parameters:
    ----------
    duration_str : str
        The duration string to parse.

    Returns:
    -------
    int
        The total duration in seconds.
    """
    duration_parts = duration_str.split(":")
    if len(duration_parts) == 3:
        return int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
    elif len(duration_parts) == 2:
        return int(duration_parts[0]) * 60 + int(duration_parts[1])
    return int(duration_parts[0])


async def download_apple_music(url: str, output_path: str = "other/downloadsTemp", format: str = "audio"):
    """
    Downloads audio from Apple Music and searches for the corresponding YouTube video,
    then extracts and processes the audio from the video.

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

    Raises:
    -------
    Exception
        Catches and logs any exceptions that occur during the process.
    """
    try:
        artist, title, cover_url = await get_applemusic_author(url)
        logging.info(f"Artist: {artist}, Title: {title}, Cover URL: {cover_url}")

        videos_search = VideosSearch(f"{artist} - {title}", limit=10)
        video_results = await asyncio.to_thread(videos_search.result)

        for video_result in video_results.get("result", []):
            video_link = video_result["link"]
            duration_str = video_result.get("duration", "0")

            duration = parse_duration(duration_str)

            if duration <= 600:
                logging.info(f"Found suitable video: {video_link} with duration {duration} seconds")

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

                update_metadata(audio_filename, artist, title)

                if audio_filename and cover_filename:
                    return audio_filename, cover_filename

    except Exception as e:
        logging.error(f"Error downloading YouTube Audio: {e}", exc_info=True)

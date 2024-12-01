import asyncio
import logging
import os
import re
import urllib.request

import yt_dlp
from yt_dlp.utils import sanitize_filename

from utils import get_applemusic_author, update_metadata, search_music


class AppleMusicDownloader:
    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the Apple Music downloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.yt_dlp_options = {
            "format": "m4a/bestaudio/best",
            "outtmpl": f"{output_path}/{sanitize_filename('%(title)s')}",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                },
            ],
        }

    async def download(self, url: str, format: str = "audio"):
        """
        Download an audio (track or playlist) based on the format.

        Parameters:
        ----------
        url : str
            The SoundCloud video URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio) audio only.

        Returns:
        -------
        AsyncGenerator
            Returns an async generator yielding audio and cover filenames or None if an error occurs.
        """
        try:
            if re.match(r"https?://music\.apple\.com/.*/album/.+/\d+(\?.*)?$", url):
                # Single track
                async for result in self._download_single_track(url):
                    yield result
            # elif re.match(r"", url):
            #     # Playlist
            #     async for result in self._download_playlist(url):
            #         yield result
            else:
                logging.error(f"Unsupported URL: {url}")
                yield None, None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None, None

    async def _download_single_track(self, url: str):
        """
        Downloads a single Apple Music track.

        Parameters:
        ----------
        url : str
            The URL of the Apple Music track to download.

        Yields:
        -------
        tuple
            Yields the file paths of the downloaded audio and cover image, or None if an error occurs.
        """
        yield await self._download_track(url)

    # async def _download_playlist(self, url: str):
    #     """
    #     Downloads a SoundCloud playlist by iterating over each track in the playlist.
    #
    #     Parameters:
    #     ----------
    #     url : str
    #         The URL of the SoundCloud playlist to download.
    #
    #     Yields:
    #     -------
    #     tuple
    #         Yields the file paths of the downloaded audio and cover image for each track, or None if an error occurs.
    #     """
    #     tracks = get_all_tracks_from_playlist_soundcloud(url)
    #     for track in tracks:
    #         yield await self._download_track(track)

    async def _download_track(self, url: str, output_path: str = "other/downloadsTemp", format: str = "audio"):
        """
        Downloads audio from YouTube based on an Apple Music track's artist and title.

        Given an Apple Music URL, the function retrieves the artist and title, searches for a corresponding YouTube video,
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

            with yt_dlp.YoutubeDL(self.yt_dlp_options) as ydl:
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
            return None, None

import logging
import os
import asyncio
import re
import urllib.request
import yt_dlp
from yt_dlp.utils import sanitize_filename
from utils import update_metadata, get_all_tracks_from_playlist_soundcloud


class SoundCloudDownloader:
    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the SoundCloud downloader with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.yt_dlp_options = {
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

    async def download(self, url: str, format: str = "audio"):
        """
        Download a media file (video or audio) based on the format.

        Parameters:
        ----------
        url : str
            The SoundCloud video URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio).

        Returns:
        -------
        AsyncGenerator
            Returns an async generator yielding audio and cover filenames or None if an error occurs.
        """
        try:
            if re.match(r"https://soundcloud\.com/[\w-]+/(?!sets/)[\w-]+", url):
                # Single track
                async for result in self._download_single_track(url):
                    yield result
            elif re.match(r"https?://soundcloud\.com/[a-zA-Z0-9_-]+/sets/[a-zA-Z0-9_-]+", url):
                # Playlist
                async for result in self._download_playlist(url):
                    yield result
            else:
                logging.error(f"Unsupported URL: {url}")
                yield None, None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None, None

    async def _download_single_track(self, url: str):
        """
        Downloads a single SoundCloud track.

        Parameters:
        ----------
        url : str
            The URL of the SoundCloud track to download.

        Yields:
        -------
        tuple
            Yields the file paths of the downloaded audio and cover image, or None if an error occurs.
        """
        yield await self._download_track(url)

    async def _download_playlist(self, url: str):
        """
        Downloads a SoundCloud playlist by iterating over each track in the playlist.

        Parameters:
        ----------
        url : str
            The URL of the SoundCloud playlist to download.

        Yields:
        -------
        tuple
            Yields the file paths of the downloaded audio and cover image for each track, or None if an error occurs.
        """
        tracks = get_all_tracks_from_playlist_soundcloud(url)
        for track in tracks:
            yield await self._download_track(track)

    async def _download_track(self, url: str):
        """
        Core method to download a single SoundCloud track and its metadata.

        Parameters:
        ----------
        url : str
            The URL of the SoundCloud track to download.

        Returns:
        -------
        tuple
            Returns a tuple containing the audio filename and cover filename, or (None, None) if an error occurs.
        """
        try:
            # Download track info
            ydl = yt_dlp.YoutubeDL(self.yt_dlp_options)
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
            title = info_dict.get("title")
            artist = info_dict.get("uploader")
            cover_url = self._get_cover_url(info_dict)

            # Download the track
            await asyncio.to_thread(ydl.download, [url])

            # Filenames for audio and cover
            audio_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.mp3")
            cover_filename = os.path.join(self.output_path, f"{sanitize_filename(title)}.jpg")

            # Download the cover image
            if cover_url:
                urllib.request.urlretrieve(cover_url, cover_filename)

            # Update metadata
            update_metadata(audio_file=audio_filename, title=title, artist=artist, cover_file=cover_filename)

            # Return file paths if files exist
            if os.path.exists(audio_filename) and os.path.exists(cover_filename):
                return audio_filename, cover_filename
            else:
                return None, None

        except Exception as e:
            logging.error(f"Error downloading track: {str(e)}")
            return None, None

    def _get_cover_url(self, info_dict: dict):
        """
        Extracts the cover URL from the track's information.

        Parameters:
        ----------
        info_dict : dict
            The information dictionary for the SoundCloud track.

        Returns:
        -------
        str or None
            The URL of the cover image, or None if no appropriate image is found.
        """
        thumbnails = info_dict.get("thumbnails", [])
        return next((thumbnail["url"] for thumbnail in thumbnails if thumbnail.get("width") == 500), None)

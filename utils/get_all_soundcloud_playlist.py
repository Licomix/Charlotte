import logging
import yt_dlp


def get_all_tracks_from_playlist_soundcloud(url: str) -> list[str]:
    """
    Extracts all track URLs from a SoundCloud playlist.

    Args:
        url (str): The URL of the SoundCloud playlist.

    Returns:
        list[str]: A list of track URLs. Returns None if there is an error.
    """
    try:
        options = {
            "noplaylist": False,
            "extract_flat": True
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            playlist_info = ydl.extract_info(url, download=False)


        track_urls = [entry.get('url') for entry in playlist_info.get('entries', []) if entry.get('url')]

        return track_urls if track_urls else None

    except Exception as e:
        logging.error(f"Error extracting track URLs from playlist: {e}")
        return None
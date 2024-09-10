import logging
import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from config.secrets import SPOTIFY_CLIENT_ID, SPOTIFY_SECRET


auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_SECRET
)
spotify = spotipy.Spotify(auth_manager=auth_manager)


def get_all_tracks_from_playlist_spotify(url: str) -> list[str]:
    """
    Retrieves all track URLs from a Spotify playlist.

    :param url: URL of the Spotify playlist.
    :return: A list of track URLs.
    """
    match = re.search(r"playlist/([^/?]+)", url)
    if not match:
        logging.error(f"Invalid playlist URL: {url}")
        return []

    playlist_id = match.group(1)
    all_tracks = []
    offset = 0
    limit = 100

    while True:
        try:
            results = spotify.playlist_tracks(playlist_id, limit=limit, offset=offset)
            tracks = results["items"]
            all_tracks.extend(tracks)
            if len(tracks) < limit:
                break
            offset += limit
        except Exception as e:
            logging.error(f"Error fetching tracks: {e}")
            break

    track_urls = []

    for item in all_tracks:
        track = item.get("track")
        if track:
            track_url = track.get("external_urls", {}).get("spotify")
            if track_url:
                track_urls.append(track_url)

    return track_urls

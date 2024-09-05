import aiohttp
from bs4 import BeautifulSoup
import logging


async def get_soundcloud_author(url: str) -> tuple[str, str] | None:
    """
    Asynchronously retrieves the artist name and track title from a SoundCloud URL.

    :param url: SoundCloud URL of the track.
    :return: Tuple containing artist name and track title, or None if an error occurs.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch data from SoundCloud, status code: {response.status}")
                    return None

                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        artist_div = soup.find("div", itemprop="byArtist")
        track_meta = soup.find("meta", property="og:title")

        if artist_div and track_meta:
            artist_name = artist_div.meta["content"] if artist_div.meta else None
            track_title = track_meta["content"]

            if artist_name and track_title:
                logging.info(f"Successfully retrieved artist: {artist_name}, track: {track_title}")
                return artist_name, track_title
            else:
                logging.error("Missing artist name or track title in the HTML content.")
                return None

        logging.error("Required HTML elements not found.")
        return None

    except aiohttp.ClientError as e:
        logging.error(f"Network error occurred: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error parsing SoundCloud author information: {str(e)}")
        return None

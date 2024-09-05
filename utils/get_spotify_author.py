import logging
import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config.secrets import SPOTIFY_CLIENT_ID, SPOTIFY_SECRET

auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_SECRET
)
spotify = spotipy.Spotify(auth_manager=auth_manager)

def extract_track_id(url: str) -> str:
    match = re.search(r'track/(\w+)', url)
    return match.group(1) if match else None

async def get_spotify_author(url: str):
    track_id = extract_track_id(url)
    if not track_id:
        logging.error("Invalid Spotify URL")
        return None, None, None

    try:
        result = spotify.track(track_id)
        artist = ", ".join([artist["name"] for artist in result["artists"]])
        title = result["name"]
        cover_url = result['album']['images'][0]['url']

        if artist and title:
            return artist, title, cover_url
        else:
            return None, None, None
    except Exception as e:
        logging.error(f"Error fetching track: {e}")
        return None, None, None



# import aiohttp
# import asyncio
# import logging

# # Убедитесь, что токен обновляется при необходимости
# ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'

# async def get_spotify_author(url: str) -> tuple[str, str, str] | None:
#     """
#     Асинхронно получает имя исполнителя, название трека и URL обложки из URL трека Spotify.

#     :param url: URL трека Spotify.
#     :return: Кортеж, содержащий имя исполнителя, название трека и URL обложки, или None в случае ошибки.
#     """
#     try:
#         # Извлечение идентификатора трека из URL
#         track_id = url.split('/')[-1].split('?')[0]
#         api_url = f"https://api.spotify.com/v1/tracks/{track_id}"

#         headers = {
#             "Authorization": f"Bearer {ACCESS_TOKEN}",  # Используйте ваш токен доступа
#         }

#         async with aiohttp.ClientSession() as session:
#             async with session.get(api_url, headers=headers) as response:
#                 if response.status != 200:
#                     logging.error(f"Failed to fetch data from Spotify API, status code: {response.status}")
#                     return None

#                 data = await response.json()

#                 artist = ", ".join([artist["name"] for artist in data["artists"]])
#                 title = data.get("name", "Unknown Title")
#                 cover_url = data['album']['images'][0]['url']

#                 if artist and title:
#                     return artist, title, cover_url
#                 else:
#                     logging.error("Artist or title information is missing.")
#                     return None

#     except aiohttp.ClientError as e:
#         logging.error(f"Network error occurred: {str(e)}")
#         return None
#     except KeyError as e:
#         logging.error(f"Missing expected data in Spotify response: {str(e)}")
#         return None
#     except Exception as e:
#         logging.error(f"Unexpected error occurred: {str(e)}")
#         return None

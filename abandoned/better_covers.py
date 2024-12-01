# Not used, because telegram limitation, that breaks covers on some clients
# But maybe you need it

import deezer
import logging
from difflib import SequenceMatcher

def get_similarity(str1, str2):
    matcher = SequenceMatcher(None, str1.lower(), str2.lower())
    return matcher.ratio()

async def get_better_covers(artist: str, title: str) -> str | None:
    with deezer.Client() as client:
        try:
            find: deezer.Track = client.search(query=f'{artist} {title}', strict=False)[0]

            result_artist: str = find.as_dict()["artist"]["name"]
            result_title: str = find.as_dict()["title"]

            artist_similarity = get_similarity(artist, result_artist)
            title_similarity = get_similarity(title, result_title)

            if artist_similarity > 0.6 and title_similarity > 0.8:
                return find.as_dict()["album"]["cover_xl"]
            else:
                return None

        except Exception as e:
            logging.error(e)
            return None

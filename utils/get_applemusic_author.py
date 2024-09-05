import aiohttp
import logging
from bs4 import BeautifulSoup


async def get_applemusic_author(url: str):
    """Getting artist and title of music from Apple Music

    Args:
        url (str): Music url on apple music

    Returns:
        artist_name: Artist name
        track_title: Track title
        best_image_url: Cover url
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_content = await response.text()

                soup = BeautifulSoup(html_content, 'html.parser')

                title_span = soup.find('h1', class_='headings__title svelte-1fpig7d')
                track_title = title_span.find('span', dir='auto').text.strip() if title_span else None

                artist_a = soup.find('div', class_='headings__subtitles svelte-1fpig7d')
                artist_name = artist_a.find('a').text.strip() if artist_a else None

                picture_tag = soup.find('picture', class_='svelte-3e3mdo')
                if picture_tag:
                    source_tag = picture_tag.find('source', type="image/webp")
                    if source_tag:
                        srcset = source_tag.get('srcset')
                        image_urls = srcset.split(',')

                        best_image_url = max(image_urls, key=lambda url: int(url.split(' ')[1][:-1])).split(' ')[0]

                if track_title and artist_name and best_image_url:
                    return artist_name, track_title, best_image_url
                else:
                    logging.error("Could not find the track title or artist name on the page.")
                    return None, None

    except Exception as e:
        logging.error(f"Error getting Apple Music author: {str(e)}")
        return None, None

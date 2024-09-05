import re
from aiogram import types
from aiogram.filters import BaseFilter

class UrlFilter(BaseFilter):
    """
    A filter for detecting URLs in a message from various popular platforms.

    This filter checks if the message contains a URL that matches any of the following patterns:
        - YouTube (shorts, standard watch URL)
        - TikTok (short URLs and regular URLs)
        - SoundCloud (track URLs)
        - Spotify (track URLs)
        - Apple Music (album URLs)
        - Pinterest (pins and board URLs)
        - Bilibili (video URLs)
        - Twitter/X (status URLs)
        - Instagram (posts, reels, TV shows, and stories)

    Methods:
        __call__(message: types.Message) -> bool:
            Asynchronously checks if the message contains a URL matching any of the patterns.
    """
    async def __call__(self, message: types.Message) -> bool:
        return any([
            re.match(r'https?://(?:www\.)?(?:youtu\.be\/|youtube\.com/(?:shorts/|watch\?v=))([\w-]+)', message.text),
            re.match(r'https?://vm.tiktok.com/', message.text),
            re.match(r'https?://(?:www\.)?tiktok\.com/.*', message.text),
            re.match(r'https?://soundcloud\.com/([\w-]+)/([\w-]+)', message.text),
            re.match(r'https?://open\.spotify\.com/track/([\w-]+)', message.text),
            re.match(r'https?://music\.apple\.com/.*/album/.+/\d+(\?.*)?$', message.text),
            re.match(r'https?://(?:\w{2,3}\.)?pinterest\.com/[\w/\-]+|https://pin\.it/[A-Za-z0-9]+', message.text),
            re.match(r'https?://(?:www\.)?bilibili\.(?:com|tv)/[\w/?=&]+', message.text),
            re.match(r'https://(?:twitter|x)\.com/\w+/status/\d+', message.text),
            re.match(r'https://www\.instagram\.com/(?:p|reel|tv|stories)/([A-Za-z0-9_-]+)/', message.text),
        ])

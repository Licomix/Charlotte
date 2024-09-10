import re
from aiogram import types
from aiogram.filters import BaseFilter

class PlaylistFilter(BaseFilter):
    """
    A filter for detecting services playlist URLs in a message.

    Methods:
        __call__(message: types.Message) -> bool:
            Asynchronously checks if the message contains a URL pointing to playlist.
    """
    async def __call__(self, message: types.Message) -> bool:
        return any([
            re.match(r'https:\/\/soundcloud\.com\/[a-zA-Z0-9_-]+\/sets\/[a-zA-Z0-9_-]+', message.text),
            re.match(r'https?://open\.spotify\.com/playlist/([\w-]+)', message.text),
        ])

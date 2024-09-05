from aiogram.filters import BaseFilter
from aiogram.types import Message


class EmojiTextFilter(BaseFilter):
    """
    A filter for checking if the message text matches a specified text.

    This filter performs a case-insensitive comparison between the text of the message and
    a predefined text.

    Attributes:
        text (str): The text to compare against the message text.

    Methods:
        __call__(message: types.Message) -> bool:
            Asynchronously checks if the message text matches the predefined text.
    """
    def __init__(self, text: str):
        self.text = text

    async def __call__(self, message: Message) -> bool:
        return message.text.casefold() == self.text.casefold()

from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import FSMI18nMiddleware, I18n, I18nMiddleware

from database.database_manager import SQLiteDatabaseManager

i18n = I18n(path="locales", default_locale="en", domain="messages")
i18n_middleware = FSMI18nMiddleware(i18n)


class CustomMiddleware(I18nMiddleware):
    def __init__(self, i18n: I18n):
        self.i18n = i18n

    async def set_local(self, state: FSMContext, locale: str) -> None:
        """Set localisation for user state

        Args:
            state (FSMContext): Message State Object
            locale (str): Localisation, such as: en, ru, etc.
        """
        await i18n_middleware.set_locale(state=state, locale=locale)

    async def get_locale(self, chat_id: int):
        """Get localisation from database

        Args:
            chat_id (int): Chat ID

        Returns:
            str: Localisation, such as: en, ru, etc.
        """
        language = await get_chat_language(chat_id)
        return language

    def setup_dp(self, dp):
        """Setup i18n middleware for dispatcher

        Args:
            dp (Dispatcher): Dispatcher Object

        Returns:
            i18n: i18n Object
        """
        i18n_middleware.setup(dp)
        return i18n_middleware


async def get_chat_language(chat_id: int):
    """Get chat language from database

    Args:
        chat_id (int): Chat ID

    Returns:
        str: Localisation, such as: en, ru, etc. Default is 'en'
    """
    async with SQLiteDatabaseManager() as cursor:
        await cursor.execute(
            "SELECT lang FROM chat_settings WHERE chat_id = ?", (chat_id,)
        )
        result = await cursor.fetchone()

        if result:
            return result[0]
        else:
            return "en"

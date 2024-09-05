from database.database_manager import SQLiteDatabaseManager

async def db_add_chat(chat_id: int, locale: str, anonime_statistic: int) -> None:
    """Add chat info into database

    Args:
        chat_id (int): Chat ID
        locale (str): Localisation, such as: en, ru, etc.
        anonime_statistic (int): Anonime statistic bool
    """
    async with SQLiteDatabaseManager() as cursor:
        await cursor.execute(
            """
            INSERT INTO chat_settings (chat_id, lang, anonime_statistic)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM chat_settings WHERE chat_id = ?
            )
            """,
            (chat_id, locale, anonime_statistic, chat_id),
        )

async def db_change_lang(chat_id: int, lang: str) -> None:
    """Change localisation in database

    Args:
        chat_id (int): User Chat ID
        lang (str): Localisation, such as: en, ru, etc.
    """

    async with SQLiteDatabaseManager() as cursor:
        await cursor.execute("SELECT lang FROM chat_settings WHERE chat_id = ?", [chat_id])
        row = await cursor.fetchone()

        if row:
            await cursor.execute("UPDATE chat_settings SET lang = ? WHERE chat_id = ?", (lang, chat_id))
        else:
            await cursor.execute(
                """
                INSERT INTO chat_settings (chat_id, lang, anonime_statistic)
                SELECT ?, ?, ?
                """,
                (chat_id, lang, 0),
            )

async def db_get_lang(chat_id: int) -> str:
    """Get localisation from database

    Args:
        chat_id (int): User Chat ID

    Returns:
        str: Localisation
    """
    async with SQLiteDatabaseManager() as cursor:
        await cursor.execute("SELECT lang FROM chat_settings WHERE chat_id = ?", [chat_id])
        row = await cursor.fetchone()

        if row:
            return row[0]
        else:
            return "en"

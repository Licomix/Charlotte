import aiosqlite
import logging


class SQLiteDatabaseManager:
    """
    A context manager for managing SQLite database connections and cursors using async/await.

    Attributes:
        mode (str): The mode in which the database is operating (e.g., "production").
        conn (aiosqlite.Connection): The SQLite database connection object.
        cursor (aiosqlite.Cursor): The SQLite database cursor object.

    Methods:
        __aenter__: Asynchronously opens a connection to the database and returns a cursor.
        __aexit__: Asynchronously closes the cursor and the connection, commits any pending transactions,
                    and handles any exceptions that occurred.
    """
    def __init__(self, mode: str = "production"):
        """
        Initializes the SQLiteDatabaseManager instance.

        Args:
            mode (str): The mode in which the database is operating (e.g., "production"). Defaults to "production".
        """
        self.mode = mode
        self.conn = None
        self.cursor = None

    async def __aenter__(self):
        """
        Asynchronously opens a connection to the SQLite database and returns a cursor.

        Returns:
            aiosqlite.Cursor: The cursor for interacting with the database.

        Raises:
            aiosqlite.Error: If an error occurs while connecting to the database.
        """
        try:
            self.conn = await aiosqlite.connect("./database/database.sql")

            self.cursor = await self.conn.cursor()
            logging.info(f"Connected to the database: {self.mode}")
            return self.cursor

        except aiosqlite.Error as e:
            logging.error(f"Error connecting to the database: {e}")
            raise

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Asynchronously closes the cursor and the database connection, commits any pending transactions,
        and logs any exceptions that occurred.

        Args:
            exc_type (type): The type of the exception that was raised, if any.
            exc_value (Exception): The exception instance, if any.
            traceback (traceback): The traceback object, if any.

        Returns:
            bool: False, to propagate the exception if one occurred.
        """
        if self.cursor:
            await self.cursor.close()
            logging.info("Cursor closed")
        if self.conn:
            await self.conn.commit()
            await self.conn.close()
            logging.info("Connection closed")

        if exc_type is not None:
            logging.error(f"An error occurred: {exc_type}, {exc_value}")

        return False


async def create_table_settings():
    """
    Creates the 'chat_settings' table in the SQLite database if it does not already exist.

    The table includes:
        - chat_id (INTEGER PRIMARY KEY): Unique identifier for the chat.
        - lang (TEXT): Language setting for the chat, defaulting to 'en'.
        - anonime_statistic (BOOLEAN): Indicates if anonymous statistics are enabled, defaulting to 0 (False).
    """
    async with SQLiteDatabaseManager() as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT en,
                anonime_statistic BOOLEAN DEFAULT 0
            );
        """
        )

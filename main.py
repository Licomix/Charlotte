import asyncio
import logging
import os
from logging.handlers import TimedRotatingFileHandler

import handlers
from database.database_manager import create_table_settings
from loader import bot, dp
from utils.language_middleware import CustomMiddleware, i18n
from utils.set_bot_commands import set_default_commands

# Initialize CustomMiddleware and connect it to dispatcher
CustomMiddleware(i18n=i18n).setup_dp(dp)


@dp.startup()
async def on_ready():
    """
    This function is called when the bot is ready.
    """
    logging.info("Bot is ready")


async def main():
    """
    The main asynchronous function to start the bot and perform initial setup.
    """
    await create_table_settings()
    await set_default_commands()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, on_startup=on_ready)
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}")


if __name__ == "__main__":
    log_dir = 'other/logs'
    os.makedirs(log_dir, exist_ok=True)

    log_format = '%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'

    log_file = os.path.join(log_dir, 'logging.log')
    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(log_format))

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    asyncio.run(main())

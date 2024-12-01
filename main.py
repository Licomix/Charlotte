import asyncio
import importlib
import logging
import os
import pkgutil
from logging.handlers import TimedRotatingFileHandler

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

    load_modules(["handlers.user", "handlers.admin"], ignore_files=["__init__.py", "help.py"])

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, on_startup=on_ready)
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}")

def load_modules(plugin_packages, ignore_files=[]):
    ignore_files.append("__init__")
    for plugin_package in plugin_packages:
        package = importlib.import_module(plugin_package)
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg and name not in ignore_files:
                logging.info(f"Loading module: {plugin_package}.{name}")
                importlib.import_module(f"{plugin_package}.{name}")

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

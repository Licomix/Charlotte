from aiogram import types
from loader import bot


async def set_default_commands():
    """
    Sets default commands for the Telegram bot.

    This asynchronous function configures the default commands that the bot will recognize.
    The commands are set using the `bot.set_my_commands` method from the Aiogram library.

    The function uses the `types.BotCommand` to specify the command '/start' and its description
    'Start work with me'. When users send the '/start' command to the bot, they will see the description
    associated with it.

    Parameters:
    - None

    Returns:
    - None

    This function does not take any parameters and does not return any value. It only performs
    an action by setting the default commands for the bot.
    """
    await bot.set_my_commands(
        [
            types.BotCommand(command='start', description='🌸 Start work with me'),
            types.BotCommand(command='help', description='🐾 My commands'),
            types.BotCommand(command='settings', description='🎀 Settings'),
            types.BotCommand(command='cancel', description='🔮 Cancel task'),
            types.BotCommand(command='support', description='💖 Support Charlotte'),
        ]
    )

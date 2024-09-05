import logging

from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from functions.db import db_add_chat
from loader import dp
from utils.language_middleware import CustomMiddleware, i18n


@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    try:
        await db_add_chat(chat_id=message.chat.id, locale="en", anonime_statistic=0)

        locale = await CustomMiddleware(i18n=i18n).get_locale(chat_id=message.chat.id)
        await CustomMiddleware(i18n=i18n).set_local(state=state, locale=locale)

        await message.answer(
            _(
                "Henlooooooooooooooooooooooooooooooooooooooooooooooo\n\n"
                "Nice to meet you, {name}!\n\n"
                "I'm Charlotte - my hobby is pirating content from various resources.\n\n"
                "Use _/help_ for more info on me, commands and everything!\n\n"
                "If something doesn't work, email @jellyfrogirl, or better yet if you send a link to what didn't download🧡"
            ).format(name=message.from_user.first_name),
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as err:
        logging.error(f"Error handling /start command: {err}")

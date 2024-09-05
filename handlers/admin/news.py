import asyncio
import datetime

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.i18n import gettext as _

from config.secrets import ADMIN_ID
from database.database_manager import SQLiteDatabaseManager
from loader import dp


class News_Spam(StatesGroup):
    news_spam = State()
    accept_news_spam = State()

@dp.message(Command("news_spam"))
async def news_spam_command(message: Message, state: FSMContext) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(News_Spam.news_spam)
    await message.answer(_("Send a message with the news"))


@dp.message(News_Spam.news_spam)
async def proccess_spam_news(message: Message, state: FSMContext) -> None:
    escaped_text = escape_markdown(message.text)
    text = "Are you sure you want to send such a message?\n" f"> {escaped_text}"

    button_yes = KeyboardButton(text="yes")
    button_no = KeyboardButton(text="cancel")

    language_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_yes, button_no],
        ],
        resize_keyboard=True,
    )

    await state.update_data(message_text=escaped_text)
    await state.set_state(News_Spam.accept_news_spam)
    await message.answer(
        text, reply_markup=language_keyboard, parse_mode=ParseMode.MARKDOWN_V2
    )


@dp.message(News_Spam.accept_news_spam, F.text.casefold() == "yes")
async def process_spam_news_to_chats(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    bot = message.bot
    chat_id = message.chat.id
    message_text = data.get("message_text", "")

    await message.answer(_("Mailing list started"), reply_markup=ReplyKeyboardRemove())
    await state.clear()

    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_chat = 0
    sucсess_send = 0
    error_send = 0

    async with SQLiteDatabaseManager() as cursor:
        await cursor.execute("SELECT DISTINCT chat_id FROM chat_settings")
        rows = await cursor.fetchall()
        total_chat = len(rows)

        for row in rows:
            try:
                if row[0] == chat_id:
                    continue
                await asyncio.sleep(5)
                await message.bot.send_message(row[0], message_text, parse_mode=ParseMode.MARKDOWN_V2)
                sucсess_send += 1
            except Exception as e:
                error_send += 1
                print(e)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        _("The mailing has been completed\n"
        "Beginning at {start_time}\n"
        "Ended at {end_time}\n"
        "Number of chats: {total_chat}\n"
        "Successfully sent: {sucсess_send}\n"
        "erros: {error_send}").format(start_time=start_time, end_time=end_time, total_chat=total_chat, sucсess_send=sucсess_send, error_send=error_send)
    )

    await bot.send_message(chat_id=chat_id, text=message)


def escape_markdown(text: str) -> str:
    special_chars = [
        "*",
        "_",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

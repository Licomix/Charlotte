from aiogram import Bot, F
from aiogram.enums.chat_member_status import ChatMemberStatus
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

from filters.settings_filter import EmojiTextFilter
from functions.db import db_change_lang
from utils.language_middleware import CustomMiddleware, i18n
from loader import dp

class Settings(StatesGroup):
    language = State()

@dp.message(Command("settings"))
async def settings_command(message: Message, state: FSMContext) -> None:
    chat = message.chat

    if chat.type == "group" or chat.type == "supergroup":
        is_admin_or_owner = await check_if_admin_or_owner(message.bot, chat.id, message.from_user.id)
        if not is_admin_or_owner:
            await message.answer(_("You have no rights to edit these settings!"))
            return

    button_lang_eng = KeyboardButton(text="English 🇺🇲")
    button_lang_rus = KeyboardButton(text="Russian 🇷🇺")
    button_lang_ukr = KeyboardButton(text="Ukrainian 🇺🇦")
    button_lang_pol = KeyboardButton(text="Polish 🇵🇱")
    button_cancel = KeyboardButton(text="Cancel ❌")

    language_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_lang_eng, button_lang_ukr],
            [button_lang_rus, button_lang_pol],
            [button_cancel],
        ],
        resize_keyboard=True,
    )

    await state.set_state(Settings.language)
    await message.answer(_("Pick a language!"), reply_markup=language_keyboard)


@dp.message(Settings.language, EmojiTextFilter("English 🇺🇲"))
async def process_settings_english(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db_change_lang(message.chat.id, "en")
    await CustomMiddleware(i18n=i18n).set_local(state=state, locale="en")
    await message.answer("Your language has been changed to English", reply_markup=ReplyKeyboardRemove())


@dp.message(Settings.language, EmojiTextFilter("Russian 🇷🇺"))
async def process_settings_russian(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db_change_lang(message.chat.id, "ru")
    await CustomMiddleware(i18n=i18n).set_local(state=state, locale="ru")
    await message.answer("Ваш язык сменён на русский", reply_markup=ReplyKeyboardRemove())


@dp.message(Settings.language, EmojiTextFilter("Ukrainian 🇺🇦"))
async def process_settings_ukrainian(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db_change_lang(message.chat.id, "uk")
    await CustomMiddleware(i18n=i18n).set_local(state=state, locale="uk")
    await message.answer("Ваша мова зміннена на українську", reply_markup=ReplyKeyboardRemove())


@dp.message(Settings.language, EmojiTextFilter("Polish 🇵🇱"))
async def process_settings_polish(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db_change_lang(message.chat.id, "pl")
    await CustomMiddleware(i18n=i18n).set_local(state=state, locale="pl")
    await message.answer("Twój język został zmieniony na Polski", reply_markup=ReplyKeyboardRemove())


@dp.message(Settings.language, EmojiTextFilter("Cancel ❌"))
async def process_settings_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("Canceled!"), reply_markup=ReplyKeyboardRemove())


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(_("Canceled!"), reply_markup=ReplyKeyboardRemove())


async def check_if_admin_or_owner(bot: Bot, chat_id: int, user_id: int) -> bool:
    chat_member = await bot.get_chat_member(chat_id, user_id)
    return chat_member.is_anonymous or chat_member.status in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    ]

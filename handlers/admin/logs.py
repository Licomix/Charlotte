from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.secrets import ADMIN_ID
from loader import dp

@dp.message(Command("get_logs"))
async def get_logs_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer_document(document=types.FSInputFile("other/logs/logging.log"))

@dp.message(Command("get_database"))
async def get_database_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer_document(document=types.FSInputFile("database/database.sql"))

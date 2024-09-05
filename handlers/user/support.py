from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from loader import dp


@dp.message(Command("support"))
async def support_handler(message: types.Message, state: FSMContext):
    answer_message  = _("After some thought, I dare to leave a link to support the project. If you have a desire to improve the work of Charlotte, please follow this link. For every 3 dollars I can buy a month of hosting that is 2 times better than the current one, which means Charlotte will respond faster even when busy. You are not obligated to pay. Only if you have the desire!!!!\n https://buymeacoffee.com/jellytyan")

    await message.answer(answer_message)

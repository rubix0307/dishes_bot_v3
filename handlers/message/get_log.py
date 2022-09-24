import time
from aiogram import types

from app import dp, bot
from functions import get_home_page


@dp.message_handler(state='*', commands=['log'])
async def main_def(message: types.Message):
    await message.delete()
    await message.answer_document(open('test_log_file.txt', 'rb'))
    time.sleep(5)
    await bot.delete_message(
        chat_id=message.from_id,
        message_id=message.message_id+1,
    )


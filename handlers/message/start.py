from aiogram import types

from app import dp, bot
from db.functions import sql
from functions import get_home_page, update_last_message


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    user = message.from_user
    
    data = get_home_page(user)
    await message.delete()
    await message.answer(data['text'], reply_markup=data['markup'])

    await update_last_message(message, castom_message_id = message.message_id + 1)

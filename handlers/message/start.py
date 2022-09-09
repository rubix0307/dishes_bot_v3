from aiogram import types

from app import dp
from functions import get_home_page


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    user = message.from_user
    data = get_home_page(user)
    await message.answer(data['text'], reply_markup=data['markup'])

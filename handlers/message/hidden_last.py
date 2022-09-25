from email import message

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import bot, dp
from config import BOT_URL
from db.functions import sql
from functions import get_home_page, update_last_message

br = '\n'


@dp.message_handler(state='*')
async def main_def(message: types.Message):
    text = message.html_text

    if BOT_URL in text:
        await update_last_message(message)

    else:

        data_list = sql(f'SELECT * FROM dishes WHERE title LIKE "%{text}%" LIMIT 1,1')

        if len(data_list) and data_list:
            dish = InlineKeyboardButton(text=f'Блюдо: {message.text.lower()}', switch_inline_query_current_chat=message.text)

            markup = InlineKeyboardMarkup()
            markup.add(dish)

            data = {
                'text': 'Возможно вы искали это:',
                'markup': markup,
            }


            await message.answer(data['text'], reply_markup=data['markup'])
            await message.delete()
        else:
            await message.answer('Я вас не понял.')
        
        await update_last_message(message, castom_message_id=message.message_id + 1)

import time

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *
from app import bot, dp
from config import BOT_URL
from db.functions import sql
from functions import update_last_message
from markups import br


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
            await update_last_message(message, castom_message_id=message.message_id + 1)
        else:

            await message.reply('Я вас не понял.')
        
            for i in range(15,-1,-1):
                await bot.edit_message_text(
                    f'''Я вас не понял.{br*2}{hitalic('Удаление через:')} {i} {hitalic("сек")}''',
                    chat_id=message.from_user.id ,
                    message_id=message.message_id + 1,
                    parse_mode='html'
                )
                time.sleep(1)

            await message.delete()
            await bot.delete_message(
                    chat_id=message.from_user.id ,
                    message_id=message.message_id + 1
                )
            
        

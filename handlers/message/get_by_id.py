import time

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *
from app import bot, dp
from functions import Article, get_data_dish, get_fav_ids, update_last_message
from markups import call_filters
from aiogram.utils.exceptions import MessageToDeleteNotFound



@dp.message_handler(filters.Text(contains=['get_id:']))
async def show_dish(message: types.Message):
    try:
        await message.delete()
    except MessageToDeleteNotFound:
        pass

    
    query = message.text
    dish_id_data, query_text_data = query.split('|')
    dish_id = int(dish_id_data.split(':')[1])
    query_text = query_text_data.split(':')[1]

    data = get_data_dish(dish_id)
    
    fav_ids = get_fav_ids(message.from_user.id)
    callback_data = {
                'id': dish_id,
                'fav': int(dish_id in fav_ids),
                'query': query_text,
                'num_ph': 0,
            }

    article = Article(data, callback_data = callback_data)
    await update_last_message(message, castom_message_id=message.message_id + 1)
    await message.answer(
        reply_markup=article.get_markup(),
        text=article.get_message_text(),
        parse_mode='html'
    )

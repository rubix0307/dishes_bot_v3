from email import message

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import bot, dp
from config import BOT_URL
from db.functions import sql
from functions import get_home_page

br = '\n'


@dp.message_handler(state='*')
async def main_def(message: types.Message):
    global last_message
    user = message.from_user
    text = message.html_text
    message_id = message.message_id

    if BOT_URL in text:
        last_message = sql(f'SELECT message_id FROM users_messages WHERE user_id = {user.id}')
        if not len(last_message):
            sql(f'INSERT INTO `users_messages`(`user_id`, `message_id`) VALUES ({user.id},{message_id})', commit=True)
            last_message = [{'message_id': message_id}]

        if not message_id == last_message[0]['message_id']:
            try:
                await bot.delete_message(
                    chat_id=user.id,
                    message_id=last_message[0]['message_id']
                )
            finally:
                sql(f'UPDATE users_messages SET message_id={message_id} WHERE user_id = {user.id}', commit=True)
    else:

        data_list = sql(f'SELECT * FROM dishes WHERE title LIKE "%{text}%" LIMIT 1,1')

        if len(data_list) and data_list:
            user = message.from_user
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

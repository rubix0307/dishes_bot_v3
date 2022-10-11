from aiogram import types

from app import dp, bot
from db.functions import sql
from functions import get_home_page, update_last_message


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    
    data = get_home_page()
    data_answer = {
        'text': data['text'],
        'reply_markup': data['markup'],
    }

    try:
        start_parameter = message.text.split()[1]
        if start_parameter == 'speed':
            data_answer.update({'text':f'{data_answer["text"]}\n\n❗️ Быстрый поиск работает только в этом чате (с ботом)'})
    
    except IndexError:
        start_parameter = None



    
    await message.delete()
    await message.answer(**data_answer)
    await update_last_message(message, castom_message_id = message.message_id + 1)

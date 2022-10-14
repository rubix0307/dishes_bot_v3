from config import ADMIN_ID, GROUG_ID
from functions import get_mailing_data
from aiogram.utils.exceptions import ChatNotFound
from app import bot





async def mailing_dishe():
    try:
        article, nexts_mailing = get_mailing_data()
        data = {
            'chat_id': GROUG_ID,
            'text': article.get_message_text(),
            'reply_markup': article.get_markup(),
            'protect_content': True,
            'parse_mode': 'html',
        }

        await bot.send_message(**data, )

        if nexts_mailing < 10:
            await bot.send_message(chat_id=ADMIN_ID, text=f'Количество блюд в рассылке: {nexts_mailing}')

    except:
        pass
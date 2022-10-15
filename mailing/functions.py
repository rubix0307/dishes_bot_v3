from aiogram import types
from aiogram.utils.exceptions import ChatNotFound
from app import bot
from config import ADMIN_ID, GROUG_ID, MEDIA_URL
import requests
from functions import get_mailing_data


async def mailing_dishe():
    try:
        article, nexts_mailing = get_mailing_data()


        media = types.MediaGroup()
        photos = article.data['photos'].split('\n')[:9]
        [media.attach_photo(types.InputFile(MEDIA_URL + photo), article.title) for photo in photos]


        data = {
            'chat_id': GROUG_ID,
            'protect_content': True,
            
        }
        
        show_preview = False
        try:
            if len(photos) > 1:
                await bot.send_media_group(
                    media=media, **data,
                )
            else:
                show_preview = True
        except TypeError:
            show_preview = True

        await bot.send_message(
            text=article.get_message_text(show_preview=show_preview),
            reply_markup = article.get_markup(),
            parse_mode= 'html',
            **data,
        )

        if nexts_mailing < 10:
            await bot.send_message(chat_id=ADMIN_ID, text=f'Количество блюд в рассылке: {nexts_mailing}')

    except TypeError:
        pass


import time
from aiogram import types

from app import bot, dp
from markups import edit_photo_call_menu, set_photo_call_menu
from functions import Article, edit_preview, get_call_data, get_data_dish, get_fav_ids
from db.functions import sql
from aiogram.utils.exceptions import MessageNotModified


@dp.callback_query_handler(edit_photo_call_menu.filter())
async def edit_photo(call: types.CallbackQuery, callback_data: dict()):

    call_data = get_call_data(callback_data)

    data = sql(f'''SELECT * FROM dishes WHERE id = {call_data['id']}''')[0]
    article = Article(data, callback_data=call_data)

    article, call_data = edit_preview(article, call_data, next_photo=True)

    await bot.edit_message_text(
        reply_markup=article.get_markup(),
        inline_message_id=call.inline_message_id,
        text=article.get_message_text(),
        parse_mode='html'
    )
    await call.answer()


@dp.callback_query_handler(set_photo_call_menu.filter())
async def edit_photo(call: types.CallbackQuery, callback_data: dict()):

    call_data = get_call_data(callback_data)

    data = get_data_dish(call_data['id'])
    article = Article(data, callback_data=call_data)

    article, call_data = edit_preview(article, call_data)


    message_photo_data = {
        'reply_markup': article.get_markup(),
        'text': article.get_message_text(),
        'parse_mode': 'html',
    }

    try:

        try:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                **message_photo_data,
            )

        except:
            await bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                **message_photo_data,
            )

    except MessageNotModified:
        await call.answer('Выбрано текущее фото')

    finally:
        await call.answer()

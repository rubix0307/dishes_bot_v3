import time
from aiogram import types

from app import bot, dp
from markups import edit_photo_call_menu
from functions import Article, edit_preview, get_call_data, get_fav_ids
from db.functions import sql



@dp.callback_query_handler(edit_photo_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    
    call_data = get_call_data(callback_data)


    data = sql(f'''SELECT * FROM dishes WHERE id = {call_data['id']}''')[0]
    article = Article(data, callback_data = call_data)

    article, call_data = edit_preview(article, call_data, next_photo=True)

    await bot.edit_message_text(
            reply_markup=article.get_markup(),
            inline_message_id=call.inline_message_id,
            text=article.get_message_text(),
            parse_mode='html'
        )
    await call.answer()

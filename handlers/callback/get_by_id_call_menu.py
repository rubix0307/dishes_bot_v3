from aiogram import types

from app import bot, dp
from markups import get_by_id_call_menu
from functions import Article, edit_preview, get_call_data, get_data_dish


@dp.callback_query_handler(get_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    call_data = get_call_data(callback_data)


    data = get_data_dish(call_data['id'])

    # call_data['view'] = int(not call_data['view']) # view deleted in call_data
    article = Article(data, callback_data = call_data)

    article, call_data = edit_preview(article, call_data)

    await bot.edit_message_text(
            reply_markup=article.get_markup(),
            text=article.get_message_text(),
            inline_message_id=call.inline_message_id,
            parse_mode='html'
        )
    await call.answer()

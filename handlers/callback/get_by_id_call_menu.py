from aiogram import types
from app import bot, dp
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from functions import Article
from markups import get_by_id_call_menu


@dp.callback_query_handler(get_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    call.query = callback_data.get('query')

    user = call.from_user

    id = int(callback_data.get('id'))
    view = int(callback_data.get('view'))

    data = sql(f'SELECT * FROM dishes WHERE id = {id}')[0]

    article = Article(data, show_recipe_instructions=view)

    
    fav = get_fav_dish_by_user(user.id)
    fav = fav if fav else []
    fav_ids = [item['id'] for item in fav]


    await bot.edit_message_text(
        text=article.get_message_text(),
        inline_message_id=call.inline_message_id,
        reply_markup=article.get_markup(fav_ids, call),
        parse_mode='html')
    await call.answer()

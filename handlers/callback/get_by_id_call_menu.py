from aiogram import types
from app import bot, dp
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from functions import Article
from markups import get_by_id_call_menu


@dp.callback_query_handler(get_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    user = call.from_user

    id = int(callback_data.get('id'))
    view = int(callback_data.get('view'))

    data = sql(f'SELECT * FROM dishes WHERE id = {id}')[0]

    categories = get_categories_data_from_id(id)
    ingredients = get_ingredients_data_from_id(id)
    photos = get_photos_data_from_id(id)

    new = {
        'categories': categories,
        'ingredients': ingredients,
        'photos': photos,
        }

    data.update(new)

    article = Article(data, show_recipe_instructions=view)
    fav = get_fav_dish_by_user(call.from_user.id)

    
    await bot.edit_message_text(
        text=article.get_message_text(),
        inline_message_id=call.inline_message_id,
        reply_markup=article.get_markup(fav),
        parse_mode='html')
    await call.answer()

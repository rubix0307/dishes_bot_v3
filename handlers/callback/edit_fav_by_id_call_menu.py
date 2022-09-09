import time
from aiogram import types
from app import bot, dp
from db.functions import get_categories_data_from_id, get_fav_dish_by_user, get_ingredients_data_from_id, get_photos_data_from_id, sql
from functions import Article
from markups import edit_fav_by_id_call_menu


@dp.callback_query_handler(edit_fav_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    user = call.from_user

    id = int(callback_data.get('id'))
    is_add = int(callback_data.get('is_add'))
    data_list_item = sql(f'SELECT * FROM dishes WHERE id = {id}')[0]

    categories = get_categories_data_from_id(id)
    ingredients = get_ingredients_data_from_id(id)
    photos = get_photos_data_from_id(id)

    new = {
        'categories': categories,
        'ingredients': ingredients,
        'photos': photos,
        }

    data_list_item.update(new)


    fav = get_fav_dish_by_user(call.from_user.id)
    fav = fav if fav else []
    fav_ids = [item['id'] for item in fav]

    if is_add and not id in fav_ids:
        sql(f'INSERT INTO fav_dish_user (user_id, dish_id) VALUES ({user.id},{id})', commit=True)
    
    elif not is_add and id in fav_ids:
        sql(f'DELETE FROM fav_dish_user WHERE fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = {id}', commit=True)


    article = Article(data_list_item, show_recipe_instructions=True)
    fav = get_fav_dish_by_user(call.from_user.id)
    await bot.edit_message_text(
        text=article.get_message_text(),
        inline_message_id=call.inline_message_id,
        reply_markup=article.get_markup(fav, query_text=''),
        parse_mode='html')
    await call.answer()



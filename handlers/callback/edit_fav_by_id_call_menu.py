from aiogram import types

from app import bot, dp
from markups import edit_fav_by_id_call_menu
from functions import Article, get_call_data, get_fav_ids
from db.functions import get_fav_dish_by_user, sql




@dp.callback_query_handler(edit_fav_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    

    user = call.from_user
    call_data = get_call_data(callback_data)
    call.query = call_data['query']
    fav_ids = get_fav_ids(user.id)


    if call_data['fav'] and not call_data['id'] in fav_ids:
        answer_text = 'Добавлено в избранное'
        sql(f'''INSERT INTO fav_dish_user (user_id, dish_id) VALUES ({user.id},{call_data['id']})''', commit=True)
        fav_ids.append(call_data['id'])
        
    elif not call_data['fav'] and call_data['id'] in fav_ids:
        answer_text = 'Убрано из избранного'
        sql(f'''DELETE FROM fav_dish_user WHERE fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = {call_data['id']}''', commit=True)
        fav_ids.remove(call_data['id'])
        
    else:
        answer_text = 'Не измененно'

    data_list_item = sql(f'''SELECT * FROM dishes WHERE id = {call_data['id']}''')[0]

    article = Article(data_list_item, show_recipe_instructions = not bool(call_data['view']))


    await bot.edit_message_text(
            text = article.get_message_text(),
            inline_message_id = call.inline_message_id,
            reply_markup = article.get_markup(fav_ids, call),
            parse_mode = 'html'
        )

    await call.answer(answer_text)



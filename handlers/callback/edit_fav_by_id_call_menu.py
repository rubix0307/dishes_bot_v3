from aiogram import types

from app import bot, dp
from markups import edit_fav_by_id_call_menu
from functions import Article, edit_preview, get_call_data, get_fav_ids
from db.functions import get_fav_dish_by_user, sql




@dp.callback_query_handler(edit_fav_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    

    user = call.from_user
    call_data = get_call_data(callback_data)


    if not call_data['fav']:
        answer_text = 'Добавлено в избранное'
        sql(f'''INSERT INTO fav_dish_user (user_id, dish_id) VALUES ({user.id},{call_data['id']})''', commit=True)
    else:
        answer_text = 'Убрано из избранного'
        sql(f'''DELETE FROM fav_dish_user WHERE fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = {call_data['id']}''', commit=True)

    call_data['fav'] = int(not call_data['fav'])


    data_list_item = sql(f'''SELECT * FROM dishes WHERE id = {call_data['id']}''')[0]



    article = Article(data_list_item, show_recipe_instructions = call_data['view'])
    
    article, call_data = edit_preview(article, call_data)
    
    await bot.edit_message_text(
            text = article.get_message_text(),
            inline_message_id = call.inline_message_id,
            reply_markup = article.get_markup(),
            parse_mode = 'html'
        )

    await call.answer(answer_text)



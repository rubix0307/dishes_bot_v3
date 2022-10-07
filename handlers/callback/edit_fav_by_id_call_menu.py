from aiogram import types

from app import bot, dp
from markups import edit_fav_by_id_call_menu
from functions import Article, edit_preview, get_call_data, get_data_dish, get_fav_ids
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


    data_list_item = get_data_dish(call_data['id'])



    article = Article(data_list_item, callback_data = call_data)
    
    article, call_data = edit_preview(article, call_data)
    
    try:
        await bot.edit_message_text(
                text = article.get_message_text(),
                inline_message_id = call.inline_message_id,
                reply_markup = article.get_markup(),
                parse_mode = 'html'
            )

    except:
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            reply_markup=article.get_markup(),
            text=article.get_message_text(),
            message_id=call.message.message_id,
            parse_mode='html',
        )
    
    finally:
        await call.answer(answer_text)



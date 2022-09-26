from aiogram import types

from app import bot, dp
from markups import get_by_id_call_menu
from functions import Article, get_call_data, get_fav_ids
from db.functions import sql



@dp.callback_query_handler(get_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    
    user = call.from_user
    call_data = get_call_data(callback_data)
    call.query = call_data['query']
    fav_ids = get_fav_ids(user.id)

    data = sql(f'''SELECT * FROM dishes WHERE id = {call_data['id']}''')[0]
    article = Article(data, show_recipe_instructions = call_data['view'])


    await bot.edit_message_text(
            text=article.get_message_text(),
            inline_message_id=call.inline_message_id,
            reply_markup=article.get_markup(fav_ids, call),
            parse_mode='html'
        )
    await call.answer()

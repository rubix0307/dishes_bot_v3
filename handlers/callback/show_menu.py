from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

from app import dp, bot
from db.functions import sql
from functions import get_home_page
from markups import show_menu, filters, call_filters


@dp.callback_query_handler(show_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    menu_name = callback_data['menu_name']
    
    if call_filters['home'] in menu_name:

        text = 'Главное меню'
        data = get_home_page(user)

        try:
            await call.message.edit_text(
                    text=data['text'],
                    reply_markup=data['markup']
                )
        except:
            await bot.edit_message_text(
                    text=text,
                    inline_message_id=call.inline_message_id,
                    reply_markup=data['markup'],
                    parse_mode='html',
                )
        await call.answer()
        return

    elif call_filters['countries'] in menu_name:
        text = 'Кухни разных стран'
        categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 1 AND is_show = 1')
    
    else:
        text = 'По категориям'
        categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')

    
    keyboard_markup = InlineKeyboardMarkup()
    for category in categories[:99]:
        keyboard_markup.add(
            InlineKeyboardButton(
                text = f'{category["title"]} {category["emoji"]}',
                switch_inline_query_current_chat = f'{filters["category"]}{category["title"].lower()}')
        )

    keyboard_markup.add(
            InlineKeyboardButton(text=f'⭕️ Главная страница ⭕️', callback_data=show_menu.new(menu_name=call_filters['home']))
        )

    try:
        await call.message.edit_text(
                text = text,
                reply_markup = keyboard_markup
            )
    except:
        await bot.edit_message_text(
                text = text,
                inline_message_id = call.inline_message_id,
                reply_markup = keyboard_markup,
                parse_mode = 'html',
            )
    await call.answer()


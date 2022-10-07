from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import bot, dp
from db.functions import sql
from functions import get_home_page
from markups import call_filters, filters, show_menu


@dp.callback_query_handler(show_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    menu_name = callback_data['menu_name']
    highlight_symbol = '✨ '

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
        top_categories = sql(
            f'SELECT title, emoji FROM `categories` WHERE id IN (58,16,31,22,33,71)')
        categories = sql(
            'SELECT title, emoji FROM categories WHERE parent_id = 1 AND is_show = 1')

        for category in top_categories:
            category['title'] = f'''{highlight_symbol}{category['title']}'''
            categories.append(category)

    else:
        text = 'По категориям'
        categories = sql(
            'SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')

    keyboard_markup = InlineKeyboardMarkup()
    for category in categories[:99]:
        button_title = f'{category["title"]} {category["emoji"]}'
        hiden_text = f'''{filters['category']}{category['title'].replace(highlight_symbol, '').split(' ')[0][:12].lower()}'''

        keyboard_markup.add(
            InlineKeyboardButton(
                text=button_title,
                switch_inline_query_current_chat=hiden_text)
        )

    keyboard_markup.add(
        InlineKeyboardButton(
            text=f'⭕️ Главная страница ⭕️',
            callback_data=show_menu.new(menu_name=call_filters['home'])
        )
    )

    try:
        await call.message.edit_text(
            text=text,
            reply_markup=keyboard_markup,
        )

    except:
        await bot.edit_message_text(
            text=text,
            parse_mode='html',
            reply_markup=keyboard_markup,
            inline_message_id=call.inline_message_id,
        )
    await call.answer()

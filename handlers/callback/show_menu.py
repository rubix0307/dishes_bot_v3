from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

from app import dp, bot
from db.functions import sql
from functions import get_home_page
from markups import show_menu, filters



def get_alphabet_sort(sorting_list: list):
    for letter_number in range(min([len(i) for i in sorting_list])):

        for round in range(len(sorting_list)):
            for i in range(len(sorting_list) - 1):

                if not letter_number:
                    if ord(sorting_list[round][letter_number]) < ord(sorting_list[i][letter_number]):
                        sorting_list[round], sorting_list[i] = sorting_list[i], sorting_list[round]
                else:
                    if ord(sorting_list[round][letter_number]) < ord(sorting_list[i][letter_number]) and ord(sorting_list[round][0]) == ord(sorting_list[i][0]):
                        sorting_list[round], sorting_list[i] = sorting_list[i], sorting_list[round]
    return sorting_list


@dp.callback_query_handler(show_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    user = call.from_user
    menu_name = callback_data.get('menu_name')
    
    if 'home' in menu_name:
        data = get_home_page(user)
        try:
            await call.message.edit_text(text=data['text'], reply_markup=data['markup'])
        except:
            await bot.edit_message_text(
                text='Главное меню',
                inline_message_id=call.inline_message_id,
                reply_markup=data['markup'],
                parse_mode='html')
 

        await call.answer()
        return

    elif 'country-cuisines' in menu_name:
        text = 'Кухни разных стран'
        categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 1 AND is_show = 1')
    
    else:
        text = 'По категориям'
        categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')

    

    keyboard_markup = InlineKeyboardMarkup()
    for category in categories[:99]:
        keyboard_markup.add(
            InlineKeyboardButton(text=f'{category["title"]} {category["emoji"]}', switch_inline_query_current_chat=f'{filters["category"]}{category["title"].lower()}')
        )

    keyboard_markup.add(
            InlineKeyboardButton(text=f'⭕️ Главная страница ⭕️', callback_data=show_menu.new(menu_name='home'))
        )

    try:
        await call.message.edit_text(text=text, reply_markup=keyboard_markup)
    except:
        await bot.edit_message_text(
            text=text,
            inline_message_id=call.inline_message_id,
            reply_markup=keyboard_markup,
            parse_mode='html')
            
    await call.answer()


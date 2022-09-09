from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *
from config import BOT_URL
from db.functions import get_fav_dish_by_user

from markups import *

br = '\n'


def get_home_page(user) -> dict:

    text = 'Добро пожаловать в бот'
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton(text=f'♥️ Избранное', switch_inline_query_current_chat=filters['favourites']))
    markup.add(InlineKeyboardButton(text=f'🗂 По категориям', callback_data=show_menu.new(menu_name='categories')))
    markup.add(InlineKeyboardButton(text=f'🌍 Кухни мира 🌎', callback_data=show_menu.new(menu_name='country-cuisines')))
    markup.add(InlineKeyboardButton(text=f'🧾 Показать все рецепты', switch_inline_query_current_chat=''))

    return {
        'text': text,
        'markup': markup,
    }

def get_advertisement(id: int, offset: int) -> types.InlineQueryResultArticle:
    return types.InlineQueryResultArticle(

            id=id*-1,
            title=f'Ваша реклама',
            thumb_url=f'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQ4qwp5h7c3KcNSnOImf64Dz1_bf_6ysZ6tQ&usqp=CAU',
            description=f'Заказать рекламу можно тут',
            
            input_message_content=types.InputTextMessageContent(
                message_text=f'''Реклама №{id}{br}{f'Страница №{offset}' if offset else ''}''',
                parse_mode='html'),
        
        )

class Article:

    def __init__(self, data, show_recipe_instructions):
        self.id = data['id']
        self.title = data['title']  
        self.serving = data['serving']
        self.cooking_time = data['cooking_time']
        self.kilocalories = data['kilocalories']
        self.protein = data['protein']
        self.fats = data['fats']
        self.carbohydrates = data['carbohydrates']
        self.recipe = data['recipe'].replace(br, br*2)

        self.categories = data['categories']
        self.ingredients = data['ingredients']
        self.photo = data['photos'][0] if len(data['photos']) > 0 else 'https://upload.wikimedia.org/wikipedia/commons/9/9a/%D0%9D%D0%B5%D1%82_%D1%84%D0%BE%D1%82%D0%BE.png'
        self.photos = data['photos']

        self.show_recipe_instructions = show_recipe_instructions
    
    def get_description(self):
        return f'Порций: {self.serving} | {self.cooking_time} | {self.kilocalories} ккал{br}{self.categories}' if self.id > 0 else '😢'

    def get_message_text(self):
        message_text = f'''{hide_link(self.photo)}
            {self.title}
            {hcode(self.get_description())}

            {self.ingredients}

            {f'🧾 Как готовить:{br}{self.recipe}' if self.show_recipe_instructions else ''}

            {hlink(f'Больше рецептов ищу ТУТ', BOT_URL)}
        ''' 
        return message_text.replace(' '*12,'').replace(br*4, br*2) if self.id > 0 else 'Похоже тут ничего не найдено'

    def get_markup(self, fav, query_text: str = ''):
        
        markup = InlineKeyboardMarkup()
        other_recipes = InlineKeyboardButton(text=f'🗂 Другие блюда', switch_inline_query_current_chat=query_text if query_text else '')
        main_page = InlineKeyboardButton(text=f'🏡 На главную', callback_data=show_menu.new(menu_name='home'))


        if  not self.id == -1:

            if fav:
                fav_ids = [item['id'] for item in fav]
            else:
                fav_ids = []

            if self.id in fav_ids:
                edit_fav = InlineKeyboardButton(text=f'♥️ Убрать из избранного',
                    callback_data=edit_fav_by_id_call_menu.new(id=self.id, is_add=0)
                )
            else:
                edit_fav = InlineKeyboardButton(text=f'🤍 В избранное',
                    callback_data=edit_fav_by_id_call_menu.new(id=self.id, is_add=1)
                )
                
            if not self.show_recipe_instructions:
                show_recipe = InlineKeyboardButton(text=f'🧾 Показать рецепт', callback_data=get_by_id_call_menu.new(
                    id=self.id,
                    view=1,
                ))         
            else:
                show_recipe = InlineKeyboardButton(text=f'📃 Скрыть рецепт', callback_data=get_by_id_call_menu.new(
                    id=self.id,
                    view=0,
                ))

            other_recipes = InlineKeyboardButton(text=f'🗂 Другие блюда', switch_inline_query_current_chat=query_text if query_text else '')
            main_page = InlineKeyboardButton(text=f'🏡 На главную', callback_data=show_menu.new(menu_name='home'))


           
            markup.add(edit_fav)
            markup.add(show_recipe, other_recipes)
            markup.add(main_page)
        
        else:
            markup.add(main_page)
        
        return markup

    def get_inline_query_result(self, fav, query_text: str = '') -> types.InlineQueryResultArticle:
        return types.InlineQueryResultArticle(

            id= self.id,
            title= self.title,
            thumb_url= self.photo,
            description= self.get_description(),
            
            input_message_content=types.InputTextMessageContent(
                message_text= self.get_message_text(),
                parse_mode='html',
                ),
            reply_markup= self.get_markup(fav, query_text),
        
        )


def get_inline_reslt(query: types.InlineQuery, data_list):

    fav = get_fav_dish_by_user(query.from_user.id)
    answer = [Article(item, False).get_inline_query_result(fav, query.query) for item in data_list]
    
    
    # ad block
    for i in range(0, len(answer) + 1, 10):
        answer.insert(i, get_advertisement(i, query.offset))
    return answer

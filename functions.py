import time
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *

from config import BOT_URL
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id)
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
            description=f'№ {id}/{offset + 1} | Заказать рекламу можно тут',
            
            input_message_content=types.InputTextMessageContent(
                message_text=f'''Реклама №{id}{br}{f'Страница №{offset+1}'}''',
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
        self.preview = data['preview']

        self.show_recipe_instructions = show_recipe_instructions
    
    def get_description(self):
        return f'Порций: {self.serving} | {self.cooking_time} | {self.kilocalories} ккал{br}{self.categories}' if self.id > 0 else '😢'

    def get_message_text(self):
        message_text = f'''{hide_link(self.preview)}
            {self.title}
            {self.get_description()}
            {hcode(f'*калорийность для сырых продуктов')}

            {self.ingredients}

            {f'🧾 Как готовить:{br}{self.recipe}' if self.show_recipe_instructions else ''}

            {hlink(f'Больше рецептов ищу ТУТ', BOT_URL)}
        ''' 
        return message_text.replace(' '*12,'').replace(br*4, br*2) if self.id > 0 else 'Похоже, тут ничего не найдено'

    def get_markup(self, fav_ids, query: types.InlineQuery):
        
        callback_data = {
            'id': self.id,
            'fav': 0,
            'view': 0,
            'query': '',
            'menu': 'home',
        }



        if self.id in fav_ids:
            callback_data.update({'fav': 0,})
        else:
            callback_data.update({'fav': 1,})

        if not self.show_recipe_instructions:
            callback_data.update({'view': 1,})    
        else:
            callback_data.update({'view': 0,})


        callback_data.update({'query': query.query,})


        markup = InlineKeyboardMarkup()
        other_recipes = InlineKeyboardButton(text=f'🗂 Другие блюда', switch_inline_query_current_chat=callback_data.get('query'))
        main_page = InlineKeyboardButton(text=f'🏡 На главную', callback_data=show_menu.new(
            menu_name = 'home'
        ))

        if not self.id < 1:


            if self.id in fav_ids:
                edit_fav = InlineKeyboardButton(text=f'♥️ Убрать из избранного',
                    callback_data=edit_fav_by_id_call_menu.new(
                        id = callback_data.get('id'),
                        fav = callback_data.get('fav'),
                        view = callback_data.get('view'),
                        query = callback_data.get('query'),
                        menu = callback_data.get('menu'),
                    )
                )
            else:
                edit_fav = InlineKeyboardButton(text=f'🤍 В избранное',
                    callback_data=edit_fav_by_id_call_menu.new(
                        id = callback_data.get('id'),
                        fav = callback_data.get('fav'),
                        view = callback_data.get('view'),
                        query = callback_data.get('query'),
                        menu = callback_data.get('menu'),
                    )
                )
                
            if not self.show_recipe_instructions:
                show_recipe = InlineKeyboardButton(text=f'🧾 Показать рецепт', callback_data=get_by_id_call_menu.new(
                    id = callback_data.get('id'),
                    fav = callback_data.get('fav'),
                    view = callback_data.get('view'),
                    query = callback_data.get('query'),
                    menu = callback_data.get('menu'),
                ))         
            else:
                show_recipe = InlineKeyboardButton(text=f'📃 Скрыть рецепт', callback_data=get_by_id_call_menu.new(
                    id = callback_data.get('id'),
                    fav = callback_data.get('fav'),
                    view = callback_data.get('view'),
                    query = callback_data.get('query'),
                    menu = callback_data.get('menu'),
                ))

            markup.add(edit_fav)
            markup.add(show_recipe, other_recipes)

            markup.add(main_page)
        
        else:
            markup.add(main_page)
        
        return markup

    def get_inline_query_result(self, fav, query: types.InlineQuery) -> types.InlineQueryResultArticle:
        return types.InlineQueryResultArticle(

            id= self.id,
            title= self.title,
            thumb_url= self.preview,
            description= self.get_description(),
            
            input_message_content=types.InputTextMessageContent(
                message_text= self.get_message_text(),
                parse_mode='html',
                ),
            reply_markup= self.get_markup(fav, query),
        
        )

def get_inline_reslt(query: types.InlineQuery, data_list):

    fav = get_fav_dish_by_user(query.from_user.id)
    answer = []
    
    for item in data_list:
        try:
            answer.append(Article(item, False).get_inline_query_result(fav, query))
        except Exception as ex:
            continue
    
    # ad block
    offset = int(query.offset) if query.offset else 0
    for round, i in enumerate(range(0, len(answer) + 1, 10)):
        answer.insert(i, get_advertisement(round + 1, offset))
    return answer

def get_extra_data(data_list):

    remove_list = []
    for round, data in enumerate(data_list):
        try:
            categories = get_categories_data_from_id(data['id'])
            ingredients = get_ingredients_data_from_id(data['id'])
            photos = get_photos_data_from_id(data['id'])
            new = {
                'categories': categories,
                'ingredients': ingredients,
                'photos': photos,
                }

            data_list[round].update(new)
        except:
            remove_list.append(data)
            continue

    for i in remove_list:
        data_list.remove(i)

    return data_list




def get_blank_data(id=-1, title='К сожалению, ничего не найдено', photo='https://sitechecker.pro/wp-content/uploads/2017/12/404.png'):
    data_list = [{
            'id': id,
            'title':title,
            'link':' ',
            'photo':photo,
            'category':' ',
            'count_ingredients':' ',
            'serving':' ',
            'cooking_time':' ',
            'kilocalories':0,
            'protein':0,
            'fats':0,
            'carbohydrates':0,
            'list_ingredients':' ',
            'recipe':' ',
            'rating':0,
            'categories': [],
            'ingredients': [],
            'photos': [photo],
        }]
    return data_list


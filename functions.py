import time
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *

from config import BOT_URL
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from markups import *
from app import bot



def get_home_page(user) -> dict:

    text = 'Добро пожаловать в бот'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'♥️ Избранное', switch_inline_query_current_chat=filters['favorites']))
    markup.add(InlineKeyboardButton(text=f'🗂 По категориям', callback_data=show_menu.new(menu_name=call_filters['categories'])))
    markup.add(InlineKeyboardButton(text=f'🌍 Кухни мира 🌎', callback_data=show_menu.new(menu_name=call_filters['countries'])))
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

    def __init__(self, data, callback_data):
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

        self.callback_data = callback_data
    
    def get_description(self):
        return f'Порций: {self.serving} | {self.cooking_time} | {self.kilocalories} ккал{br}{self.categories}' if self.id > 0 else '😢'

    def get_message_text(self):
        message_text = f'''{hide_link(self.preview.replace('c88x88', '900x-'))}
            {self.title}
            {self.get_description()}
            {hcode(f'*калорийность для сырых продуктов')}

            {self.ingredients}

            {f'🧾 Как готовить:{br}{self.recipe}' if self.callback_data['view'] else ''}

            {hlink(f'Больше рецептов ищу ТУТ', BOT_URL)}
        ''' 
        return message_text.replace(' '*12,'').replace(br*4, br*2) if self.id > 0 else 'Похоже, тут ничего не найдено'

    def get_markup(self):
        

        markup = InlineKeyboardMarkup()
        
        main_page = InlineKeyboardButton(text=f'🏡 На главную', callback_data=show_menu.new(
            menu_name = call_filters['home']
        ))

        if not self.callback_data['id'] < 1:

            if self.callback_data['fav']:
                edit_fav = InlineKeyboardButton(text=f'♥️ Убрать из избранного',
                    callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
            else:
                edit_fav = InlineKeyboardButton(text=f'🤍 В избранное',
                    callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
                
            if not self.callback_data['view']:
                show_recipe = InlineKeyboardButton(text=f'🧾 Показать рецепт', callback_data=get_by_id_call_menu.new(**self.callback_data))         
            else:
                show_recipe = InlineKeyboardButton(text=f'📃 Скрыть рецепт', callback_data=get_by_id_call_menu.new(**self.callback_data))

            other_recipes = InlineKeyboardButton(text=f'🗂 Другие блюда', switch_inline_query_current_chat=self.callback_data['query'])

            markup.add(edit_fav)
            markup.add(show_recipe, other_recipes)

        
            count_photo = sql(f'''SELECT COUNT(dish_id) as count_photos FROM photos WHERE dish_id = {self.callback_data['id']}''')[0]['count_photos']
            if count_photo > 1:
                next_photo = InlineKeyboardButton(text=f'🏞', 
                    callback_data=edit_photo_call_menu.new(**self.callback_data))

                markup.add(main_page, next_photo)
            else:
                markup.add(main_page)

        else:
            markup.add(main_page)
        
        return markup


    def get_inline_query_result(self) -> types.InlineQueryResultArticle:
        return types.InlineQueryResultArticle(
            reply_markup = self.get_markup(),
            input_message_content = types.InputTextMessageContent(
                    message_text= self.get_message_text(),
                    parse_mode='html',
                ),
            

            id= self.id,
            title= self.title,
            thumb_url= self.preview,
            description= self.get_description(),
        
        )

def get_inline_reslt(query: types.InlineQuery, data_list):
    fav_ids = get_fav_ids(query.from_user.id)
    answer = []
    
    

    for item in data_list:
        try:

            callback_data = {
                'id': item['id'],
                'fav': 1 if item['id'] in fav_ids else 0,
                'view': 0,
                'query': query.query,
                'menu': call_filters['home'],
                'num_ph': 0,
            }
            answer.append(Article(item, callback_data).get_inline_query_result())
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
            'ingredients':'',
            'list_ingredients':'',
            'recipe':' ',
            'rating':0,
            'categories': [],
            'ingredients': [],
            'photos': [photo],
            'preview': photo,
            'likes': 0,
        }]
    return data_list


async def update_last_message(message: types.Message, castom_message_id = None):

    user = message.from_user


    if not castom_message_id:
        message_id = message.message_id
    else:
        message_id = castom_message_id

    last_message = sql(f'SELECT message_id FROM users_messages WHERE user_id = {user.id}')
    
    if not len(last_message):
        sql(f'INSERT INTO `users_messages`(`user_id`, `message_id`) VALUES ({user.id},{message_id})', commit=True)
        last_message = [{'message_id': message_id}]

    elif not message_id == last_message[0]['message_id']:
        try:
            await bot.delete_message(
                    chat_id=user.id,
                    message_id=last_message[0]['message_id']
                )
        finally:
            sql(f'UPDATE users_messages SET message_id={message_id} WHERE user_id = {user.id}', commit=True)


def get_call_data(callback_data: dict) -> dict:
    # use base_markup_menu
    return {
        'id': int(callback_data.get('id')),
        'fav': int(callback_data.get('fav')),
        'view': int(callback_data.get('view')),
        'query': callback_data.get('query'),
        'menu': callback_data.get('menu'),
        'num_ph': int(callback_data.get('num_ph')),
    }

def get_fav_ids(user_id: int) -> list:

    fav = get_fav_dish_by_user(user_id)
    fav = fav if fav else []
    fav_ids = [item['id'] for item in fav]

    return fav_ids













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




def edit_preview(article, call_data, next_photo=False):
    
        photos = sql(f'''SELECT DISTINCT url FROM photos WHERE dish_id = {call_data['id']}''')

        if next_photo:
            call_data['num_ph'] += 1
        
        try:
            article.preview = photos[call_data['num_ph']]['url']
        except:
            call_data['num_ph'] = 0
            article.preview = photos[call_data['num_ph']]['url']

        return article, call_data

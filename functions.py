import copy
import re
import time

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *

from app import bot
from config import BOT_URL
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from markups import *


def get_home_page() -> dict:

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

        try:
            self.preview = data['photos'].split('\n')[callback_data['num_ph']]
        except:
            self.preview = edit_preview(call_data=callback_data, next_photo=False, get_url=True)

        self.callback_data = callback_data
    


    def get_description(self):
        return f'Порций: {self.serving} | {self.cooking_time} | {self.kilocalories} ккал{br}{self.categories}' if self.id > 0 else '😢'

    def get_message_text(self):
        message_text = f'''{hide_link(self.preview.replace('c88x88', '900x-')) if self.preview else ''}
            {self.title}
            {self.get_description()}
            {hcode(f'*калорийность для сырых продуктов')}

            {self.ingredients}

            {f'🧾 Как готовить:{br}{self.recipe}'}

            {hlink(f'Больше рецептов ищу ТУТ', BOT_URL)}
        ''' 
        return message_text.replace(' '*12,'').replace(br*4, br*2) if self.id > 0 else 'Похоже, тут ничего не найдено'



        
    def get_markup(self):
        
        markup = InlineKeyboardMarkup(row_width=8)
        
        main_page = InlineKeyboardButton(text=f'🏡 На главную', callback_data=show_menu.new(
            menu_name = call_filters['home']
        ))

        if not self.callback_data['id'] < 1:

            photos = self.get_nav_photo()
            fav = self.get_fav_button()
            # view = self.get_view_button()

            other_recipes = InlineKeyboardButton(text=f'↪️ Назад', switch_inline_query_current_chat=self.callback_data['query'])



            try:
                markup.add(*photos)
            except TypeError:
                pass

            markup.add(fav)
            markup.add(main_page, other_recipes)


            

        else:
            markup.add(main_page)
        
        return markup
    
    def get_nav_photo(self):
        count_photo = sql(f'''SELECT COUNT(dish_id) as count_photos FROM photos WHERE dish_id = {self.callback_data['id']}''')[0]['count_photos']
        
        if count_photo > 1:

            buttons_ph = []
            current_num_ph = self.callback_data['num_ph']
            callback_data = copy.deepcopy(self.callback_data)

            for num_ph in range(count_photo):
                callback_data.update({'num_ph': num_ph})

                decorations = '╿' if current_num_ph == num_ph else ''

                button = InlineKeyboardButton(text=f'{decorations}{num_ph + 1}{decorations}', 
                            callback_data = set_photo_call_menu.new(**callback_data))

                if count_photo > 5:
                    if not count_photo == current_num_ph + 1:
                        max_last_btns = 2 if current_num_ph + 2 < count_photo else int(count_photo - current_num_ph +  1)
                    else:
                        max_last_btns = 4
                    max_next_btns = 2

                    if current_num_ph == num_ph:
                        buttons_ph.append(button)

                    elif num_ph >= current_num_ph - max_last_btns and num_ph <= current_num_ph + max_next_btns:
                        buttons_ph.append(button)

                    elif current_num_ph <= 2 and num_ph < 5:
                        buttons_ph.append(button)
                
                else:
                    buttons_ph.append(button)

                # if num_ph <= current_num_ph + 2 and  num_ph >= current_num_ph - 2:
                #     buttons_ph.append(InlineKeyboardButton(text=f'{decorations}{num_ph + 1}{decorations}', 
                #             callback_data= set_photo_call_menu.new(**callback_data)))
                

        
            return buttons_ph
        return

    def get_fav_button(self):
        if self.callback_data['fav']:
            edit_fav = InlineKeyboardButton(text=f'♥️ Убрать из избранного',
                callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
        else:
            edit_fav = InlineKeyboardButton(text=f'🤍 В избранное',
                callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
        
        return edit_fav

    def get_view_button(self):
        if not self.callback_data['view']:
            show_recipe = InlineKeyboardButton(text=f'🧾 Показать рецепт', callback_data=get_by_id_call_menu.new(**self.callback_data))         
        else:
            show_recipe = InlineKeyboardButton(text=f'📃 Скрыть рецепт', callback_data=get_by_id_call_menu.new(**self.callback_data))
        
        return show_recipe

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

def get_inline_result(query: types.InlineQuery, data_list):
    fav_ids = get_fav_ids(query.from_user.id)
    answer = []
    
    

    for item in data_list:
        try:

            callback_data = {
                'id': item['id'],
                'fav': 1 if item['id'] in fav_ids else 0,
                'query': query.query,
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



def get_inline_result_min_data(query, query_text, data_list):
    answer = []
    for data in data_list:

        if data['id'] > 0:
            if not data['categories']:
                data['categories'] = "-"*20

            description = f'''Порций: {data['serving']} | {data['cooking_time']} | {data['kilocalories']} ккал{br}{data['categories'].capitalize()}'''
        else:
            description = f'😢'

        try:
            thumb_url = data['photos'].split('\n')[0].replace('900x-', 'c88x88') if type(data['photos']) == str else (data['photos'][0] if data['photos'] else None)
            answer.append(
                types.InlineQueryResultArticle(
                input_message_content = types.InputTextMessageContent(
                        message_text= f"get_id:{data['id']}|query_text:{query_text}",
                        parse_mode='html',
                    ),
                

                id= data['id'],
                title= data['title'],
                thumb_url= thumb_url,
                description= description,
            
            ))
        except:
            print()

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
        'query': callback_data.get('query'),
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




def edit_preview(article=None, call_data=None, next_photo=False, get_url=False):
    
        photos = sql(f'''SELECT url FROM photos WHERE dish_id = {call_data['id']}''')

        if next_photo:
            call_data['num_ph'] += 1
        
        try:
            url = photos[call_data['num_ph']]['url']
        except:
            try:
                call_data['num_ph'] = 0
                url = photos[0]['url']
            except IndexError:
                url = None



        if not get_url:
            article.preview = url
            return article, call_data

        else:
            return url






def get_data_dish(id: int):
    sql_query = f'''
    SELECT
        dishes.*,
        GROUP_CONCAT(DISTINCT photos.url SEPARATOR "\n") as photos,
        GROUP_CONCAT(DISTINCT CONCAT(ingredients.title,": " ,dishes_ingredients.value) SEPARATOR "\n") as ingredients,
        GROUP_CONCAT(DISTINCT categories.title SEPARATOR ", ") as categories
    FROM dishes

    LEFT JOIN photos ON dishes.id = photos.dish_id
    
    LEFT JOIN dishes_categories ON dishes.id = dishes_categories.dish_id
    LEFT JOIN categories ON categories.id = dishes_categories.category_id

    LEFT JOIN dishes_ingredients ON dishes.id = dishes_ingredients.dish_id
    LEFT JOIN ingredients ON dishes_ingredients.ingredient_id = ingredients.id

    WHERE dishes.id = {id}
    '''
    return sql(sql_query)[0]




def get_data_list_by_category(query_text, start, max_dishes):

    cat_name = query_text.split(filters['category'])[1]
    filter = sql(
        f'SELECT id FROM categories WHERE title LIKE "%{cat_name}%" LIMIT 1')
    sql_query = f'''
        SELECT dishes.* FROM dishes
        LEFT JOIN dishes_categories ON dishes_categories.dish_id = dishes.id
        LEFT JOIN categories ON categories.id = dishes_categories.category_id
        WHERE dishes_categories.category_id = {filter[0]['id'] if len(filter) else 27} 
        ORDER BY likes
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list

def get_data_list_by_category_min_data(query_text, start, max_dishes):
    cat_name = query_text.split(filters['category'])[1]
    filter_id = sql(
        f'SELECT id FROM categories WHERE title LIKE "{cat_name}%" LIMIT 1')[0]['id']
    sql_query = f'''
        SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select p.url from photos as p where p.dish_id=d.id limit 1) as photos
        FROM dishes as d 
        WHERE d.id in (select dish_id from dishes_categories where category_id = {filter_id if filter_id else 27})
        ORDER BY d.likes DESC
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list




def get_data_list_by_favorites(user, start, max_dishes):

    sql_query = f'''
    SELECT dishes.* FROM dishes
    INNER JOIN fav_dish_user ON fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = dishes.id
    WHERE 1 
    LIMIT {start},{max_dishes}'''
    data_list = sql(sql_query)

    return data_list

def get_data_list_by_favorites_min_data(user, start, max_dishes):
    sql_query = f'''
    SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select p.url from photos as p where p.dish_id=d.id limit 1) as photos
    FROM dishes as d 
    WHERE d.id in (select dish_id from fav_dish_user where user_id = {user.id})
    ORDER BY d.likes DESC
    LIMIT {start},{max_dishes}
    '''
    data_list = sql(sql_query)
    return data_list

def get_data_list_by_query_text(query_text, start, max_dishes):

    data_list = sql(
        f'SELECT * FROM dishes WHERE MATCH (title) AGAINST ("{query_text}") ORDER BY `dishes`.`likes` DESC LIMIT {start},{max_dishes}')
    if not data_list:
        data_list = sql(
            f'SELECT * FROM dishes WHERE title LIKE "%{query_text}%" ORDER BY likes LIMIT {start},{max_dishes}')
    
    return data_list

def get_data_list_by_query_text_min_data(query_text, start, max_dishes):
    data_list = sql(
        f'''SELECT  d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
        FROM dishes as d 

        WHERE MATCH (d.title) AGAINST ("{query_text}") ORDER BY d.likes DESC
            LIMIT {start}, {max_dishes}'''
    )
    if not data_list:
        data_list = sql(
            f'''
            SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, d.categories,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 
            WHERE title LIKE "%{query_text}%" ORDER BY d.likes DESC
            LIMIT {start},{max_dishes}
            ''')

    return data_list

def clear_input_text(text: str):

    sumbols = '|'.join('~!@#$%*()+|:;<>,.?/^')
    answer = re.sub(f'[{sumbols}]','',text)
    return answer.strip()




def get_home_button():
    return InlineKeyboardButton(
                    text=f'⭕️ Главная страница ⭕️',
                    callback_data=show_menu.new(menu_name=call_filters['home'])
                )
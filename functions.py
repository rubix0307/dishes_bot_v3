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
    markup.add(InlineKeyboardButton(text=f'🧾 Искать рецепт', switch_inline_query_current_chat=''))

    return {
        'text': text,
        'markup': markup,
    }

def сleaning_input_text_from_sql_injection(text: str):

    sumbols = '|'.join('~!@#$%*()+:;<>,.?/^')
    key_words = '|'.join(['DELETE', 'ALTER' , 'CREATE' , 'DROP' , 'LIKE' , 'TABLE' , 'WHERE', 'SET'])
    answer = re.sub(f'[|{sumbols}|{key_words.lower()}|]','',text.capitalize()).replace('  ', ' ').strip()
    return answer


def сleaning_input_text_for_search(query_text: str):
    query_text = f' {query_text} '
    prelogs = [' без ', ' безо ', ' близ ', ' в ',  ' во ', ' вместо ', ' вне ', ' для ', ' до ', ' за ', ' из ', ' изо ', ' к ',  ' ко ', ' кроме ', ' между ', ' меж ', ' на ', ' над ', ' надо ', ' о ',  ' об ', ' обо ', ' от ', ' ото ', ' перед ', ' передо ', ' предо ', ' пo ', ' под ', ' при ', ' про ', ' ради ', ' с ',  ' со ', ' сквозь ', ' среди ', ' через ', ' чрез ']
    for prelog in prelogs:
        query_text = query_text.replace(prelog, ' ')

    return query_text.strip()

def get_advertisement(id: int, offset: int, query_text: str) -> types.InlineQueryResultArticle:

    data_ad = sql(f'SELECT * FROM ads WHERE position = {id} AND offset = {offset}')

    if data_ad:
        data_ad = data_ad[0]

        

        input_message_content=types.InputTextMessageContent(
                message_text=f'''{hide_link(data_ad['preview_photo'])}{data_ad['message_text']}'''+ f'''\n{'-'*40}\n{hlink(f'Заказать рекламу в боте', BOT_URL)}''',
                parse_mode=data_ad['parse_mode'])
        

        markup = InlineKeyboardMarkup()
        
        url_button = InlineKeyboardButton(text=data_ad['url_button_text'] , url=data_ad['url'])

       

        markup.add(url_button)
        markup.add(get_home_button(text='🏡 На главную'), get_back_to_inline(query_text=query_text))

        result_article = {
            'id': id*-1,
            'title':  data_ad['preview_title'],
            'url':  data_ad['url'],
            'thumb_url':  data_ad['preview_photo'],
            'description':  data_ad['preview_description'],
            'input_message_content': input_message_content,
            'reply_markup': markup,
        }



    else:
        input_message_content=types.InputTextMessageContent(
                message_text=f'''Реклама №{id}{br}{f'Страница №{offset+1}'}''',
                parse_mode='html')

        result_article = {
            'id': id*-1,
            'title': f'‼️ Ваша реклама ‼️',
            'thumb_url': f'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQ4qwp5h7c3KcNSnOImf64Dz1_bf_6ysZ6tQ&usqp=CAU',
            'description': f'№ {id}/{offset + 1} | Заказать рекламу можно тут',
            'input_message_content': input_message_content

        }
        

    return types.InlineQueryResultArticle(
        **result_article,   
        )

def insert_ad(offset, answer, query_text):

    for round, i in enumerate(range(0, len(answer) + 1, 10)):
        answer.insert(i, get_advertisement(round + 1, offset, query_text))
    
    return answer

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
        self.recipe = data['recipe'].replace(br, br*2) if data['recipe'] else ''

        self.categories = data['categories'].capitalize() if data['categories'] else ''
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

            {hlink(f'📖 Книга рецептов', BOT_URL)}
        ''' 
        return message_text.replace(' '*12,'').replace(br*4, br*2) if self.id > 0 else 'Похоже, тут ничего не найдено'



        
    def get_markup(self):
        
        markup = InlineKeyboardMarkup(row_width=8)
        

        if not self.callback_data['id'] < 1:

            photos = self.get_nav_photo()
            fav = self.get_fav_button()

            try:
                markup.add(*photos)
            except TypeError:
                pass

            markup.add(fav)
            markup.add(get_home_button(text='🏡 На главную'), get_back_to_inline(query_text=self.callback_data['query']))


            

        else:
            markup.add(get_home_button(text='🏡 На главную'), get_back_to_inline(query_text=self.callback_data['query']))
        
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

                

        
            return buttons_ph
        return

    def get_fav_button(self):

        if self.callback_data['fav']:
            text='♥️ Убрать из избранного'
        else:
            text = '🤍 В избранное'

        return InlineKeyboardButton(text=text,
            callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
        


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





def get_inline_result(query, data_list, offset, is_personal_chat: bool = False, **kwargs):
    answer = []

    if not is_personal_chat:
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
                                message_text= f"get_id:{data['id']}|query_text:{query.query}",
                                parse_mode='html',
                            ),
                        

                        id= data['id'],
                        title= data['title'],
                        thumb_url= thumb_url,
                        description= description,
                    
                    )
                )
            except:
                pass



    else:
        fav_ids = get_fav_ids(query.from_user.id)
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
    ad_reply = insert_ad(offset, answer, query.query)
    
    
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
            'id': int(id),
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
            try:
                await bot.delete_message(
                        chat_id=user.id,
                        message_id=last_message[0]['message_id']
                    )
            except:
                pass
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
    if id > 0:
        sql_query = f'''
        SELECT d.id, d.title, d.original_link, d.serving, d.cooking_time, d.kilocalories,d.protein, d.fats, d.carbohydrates, d.recipe, d.likes,
            GROUP_CONCAT(DISTINCT p.url SEPARATOR "\n") as photos,
            GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') as ingredients,
            GROUP_CONCAT(DISTINCT c.title SEPARATOR ", ") as categories
        FROM dishes as d

        LEFT JOIN photos as p ON d.id = p.dish_id
        
        LEFT JOIN dishes_categories as dc ON d.id = dc.dish_id
        LEFT JOIN categories as c ON c.id = dc.category_id

        LEFT JOIN dishes_ingredients as di ON d.id = di.dish_id
        LEFT JOIN ingredients as i ON di.ingredient_id = i.id

        WHERE d.id = {id}
        '''
        return sql(sql_query)[0]
    else:
        return get_blank_data(id=id)[0]









def get_by_favorites(user_id, start, max_dishes):

    sql_query = f'''
    SELECT d.*,
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
        (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
    FROM dishes as d

    INNER JOIN fav_dish_user as fdu ON fdu.user_id = {user_id} AND fdu.dish_id = d.id
    WHERE 1
    LIMIT {start},{max_dishes}'''
    data_list = sql(sql_query)

    return data_list

def get_by_favorites_min(user_id, start, max_dishes):
    sql_query = f'''
    SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select p.url from photos as p where p.dish_id=d.id limit 1) as photos
    FROM dishes as d 
    WHERE d.id in (select dish_id from fav_dish_user where user_id = {user_id})
    ORDER BY d.likes DESC
    LIMIT {start},{max_dishes}
    '''
    data_list = sql(sql_query)
    return data_list

def get_data_by_favorites(user_id, start, max_dishes, is_personal_chat: bool = False, **kwargs):
    
    if not is_personal_chat:
        data_list = get_by_favorites_min(user_id, start, max_dishes)
    else:
        data_list = get_by_favorites(user_id, start, max_dishes)
    return data_list



def get_by_category(category_id, start, max_dishes):

    sql_query = f'''
        SELECT d.*,
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
            (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
        FROM dishes as d

        LEFT JOIN dishes_categories as dc ON dc.dish_id = d.id
        LEFT JOIN categories as c ON c.id = dc.category_id
       
        WHERE dc.category_id = {category_id} 
        
        ORDER BY d.likes
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list

def get_by_category_min(category_id, start, max_dishes):

    sql_query = f'''
        SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select p.url from photos as p where p.dish_id=d.id limit 1) as photos
        FROM dishes as d 
        WHERE d.id in (select dish_id from dishes_categories where category_id = {category_id})
        ORDER BY d.likes DESC
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list

def get_data_by_category(query_text, start, max_dishes, is_personal_chat: bool = False, **kwargs):

    cat_name = query_text.split(filters['category'])[1]
    try:
        category_id = sql(
            f'SELECT id FROM categories WHERE title LIKE "{cat_name}%" LIMIT 1')[0]['id']
    except IndexError:
        category_id = 27


    if not is_personal_chat:
        data_list = get_by_category_min(category_id, start, max_dishes)
    else:
        data_list = get_by_category(category_id, start, max_dishes)
    return data_list



def get_by_query_text(query_text, start, max_dishes):

    data_list = sql(
        f'''SELECT d.*,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
        FROM dishes as d
        WHERE MATCH (title) AGAINST ("{query_text}") ORDER BY d.likes DESC LIMIT {start},{max_dishes}''')
    if not data_list:
        data_list = sql(
            f'''SELECT d.*,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select  GROUP_CONCAT(DISTINCT CONCAT(i.title,": " ,di.value)) from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients

            FROM dishes as d
            WHERE d.title LIKE "%{query_text}%" ORDER BY d.likes LIMIT {start},{max_dishes}''')
    
    return data_list

def get_by_query_text_min(query_text, start, max_dishes):
    data_list = sql(
            f'''SELECT  d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 

            WHERE MATCH (d.title) AGAINST ("{query_text}")
                LIMIT {start}, {max_dishes}'''
        )
    if not data_list:
        data_list = sql(
            f'''
            SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.url SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 
            WHERE title LIKE "%{query_text}%" ORDER BY d.likes DESC
            LIMIT {start},{max_dishes}
            ''')
    return data_list

def get_data_by_query_text(query_text, start, max_dishes, is_personal_chat: bool = False, **kwargs):
    
    if not is_personal_chat:
        data_list = get_by_query_text_min(query_text, start, max_dishes)
    else:
        data_list = get_by_query_text(query_text, start, max_dishes)
    return data_list



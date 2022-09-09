
import time

from aiogram import types
from app import dp
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from functions import get_inline_reslt
from markups import filters

br = '\n'

@dp.inline_handler()
async def main(query: types.InlineQuery):
    
    start_time = time.time()

    query_text = query.query
    user = query.from_user
    offset = int(query.offset or 0)

    print(f'{offset=} | {query.from_user.id}')
    print(f'{query_text}')
    
    cache_time = 5
    max_dishes =  8
    start = offset * max_dishes - 1 if offset else 0
    

    if filters['favourites'] in query_text:
        sql_query = f'''SELECT dishes.* FROM dishes
                    RIGHT JOIN fav_dish_user ON fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = dishes.id
                    WHERE 1'''.replace(br, '')
        data_list = sql(sql_query)

    elif filters['category'] in query_text:
        cat_name = query_text.split(filters['category'])[1]
        filter = sql(f'SELECT id FROM categories WHERE title LIKE "%{cat_name}%"')
        sql_query = f'''
            SELECT dishes.* FROM dishes
            LEFT JOIN dishes_categories ON dishes_categories.dish_id = dishes.id
            LEFT JOIN categories ON categories.id = dishes_categories.category_id
            WHERE dishes_categories.category_id = {filter[0]['id']} 
            ORDER BY likes
            LIMIT {start},{max_dishes}
        '''.replace(br,'')

        data_list = sql(sql_query)

    else:

        data_list = sql(f'SELECT * FROM dishes WHERE MATCH (title) AGAINST ("{query_text}") LIMIT {start},{max_dishes}')
        if not data_list:
            data_list = sql(f'SELECT * FROM dishes WHERE title LIKE "%{query_text}%" ORDER BY dishes.likes LIMIT {start},{max_dishes} ')


    if not data_list:
        data_list = [{
            'id': -1,
            'title':'К сожалению, ничего не найдено',
            'link':' ',
            'photo':'https://sitechecker.pro/wp-content/uploads/2017/12/404.png',
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
        }]
        query.query = ''


    get_add_data_start = time.time()
    for round, data in enumerate(data_list):
        categories = get_categories_data_from_id(data['id'])
        ingredients = get_ingredients_data_from_id(data['id'])
        photos = get_photos_data_from_id(data['id'])
        new = {
            'categories': categories,
            'ingredients': ingredients,
            'photos': photos,
            }

        data_list[round].update(new)
    print(f'end get add data = {time.time() - get_add_data_start}')

    answer = get_inline_reslt(query, data_list[:50])
    next_offset = offset + 1 if len(answer) >= max_dishes else None

    await query.answer(answer[:50],cache_time=cache_time, is_personal=True, switch_pm_text=None, switch_pm_parameter=None, next_offset=next_offset)
    
    print(f'all time = {time.time() - start_time}', end=br*2)

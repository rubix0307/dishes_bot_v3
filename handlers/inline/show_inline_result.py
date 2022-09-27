
import time

from aiogram import types
from aiogram.utils.markdown import *
from app import dp
from db.functions import sql
from functions import get_blank_data, get_inline_reslt
from markups import br, call_filters, filters


@dp.inline_handler()
async def main(query: types.InlineQuery):

    start_time = time.time()

    user = query.from_user
    query_text = query.query
    offset = int(query.offset or 0)

    cache_time = 5
    max_value_page = 45
    max_dishes = max_value_page if offset else max_value_page - 1
    start = offset * max_dishes - 1 if offset else 0

    if filters['favorites'] in query_text:
        data_list_time = time.time()

        sql_query = f'''SELECT dishes.* FROM dishes RIGHT JOIN fav_dish_user ON fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = dishes.id WHERE 1'''.replace(br, '')
        data_list = sql(sql_query)

        data_list_time_end = time.time()

    elif filters['category'] in query_text:
        data_list_time = time.time()

        cat_name = query_text.split(filters['category'])[1]
        filter = sql(
            f'SELECT id FROM categories WHERE title LIKE "%{cat_name}%"')
        sql_query = f'''
            SELECT dishes.* FROM dishes
            LEFT JOIN dishes_categories ON dishes_categories.dish_id = dishes.id
            LEFT JOIN categories ON categories.id = dishes_categories.category_id
            WHERE dishes_categories.category_id = {filter[0]['id']} 
            ORDER BY likes
            LIMIT {start},{max_dishes}
        '''.replace(br, '')

        data_list = sql(sql_query)
        data_list_time_end = time.time()

    else:
        data_list_time = time.time()

        data_list = sql(
            f'SELECT * FROM dishes WHERE MATCH (title) AGAINST ("{query_text}") LIMIT {start},{max_dishes}')
        if not data_list:
            data_list = sql(
                f'SELECT * FROM dishes WHERE title LIKE "%{query_text}%" ORDER BY likes LIMIT {start},{max_dishes} ')

        data_list_time_end = time.time()

    if not data_list:
        alticle_none = get_blank_data(id=0)
        data_list = alticle_none
        query.query = ''

    if len(data_list) >= max_dishes:
        next_offset = offset + 1
    else:
        next_offset = None

        if not get_blank_data(id=0)[0] in data_list and (len(data_list) > 8 or offset):
            data_list.append(get_blank_data(
                id=-100,
                title='Ты долистал до конца',
                photo='https://regnum.ru/uploads/pictures/news/2021/10/22/regnum_picture_1634889920126510_big.png')[0],
            )

    inline_reslt_time = time.time()


    c_data = {

    }
    answer = get_inline_reslt(query, data_list[:50])
    inline_reslt_time_end = time.time()

    query_answer_time = time.time()
    await query.answer(
            answer[:50],
            is_personal=True,
            cache_time=cache_time,
            next_offset=next_offset,
        )
    query_answer_time_end = time.time()

    print(f'| query | "{query_text}"')
    print(f'| TIME  | data list = {data_list_time_end - data_list_time}')
    print(f'| TIME  | inline reslt = {inline_reslt_time_end - inline_reslt_time}')
    print(f'| TIME  | query answer = {query_answer_time_end - query_answer_time}')
    print(f'| TIME  | all = {query_answer_time_end - start_time}', end=br*2)

    with open('test_log_file.txt', 'a', encoding='utf-8') as f:
        f.write(
            f'"{query_text}" | {query.from_user.id} | {query.from_user.mention} | {query.from_user.url}\n')

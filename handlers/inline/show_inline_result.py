
import time

from aiogram import types
from aiogram.utils.markdown import *
from app import dp
from db.functions import sql
from functions import (clear_input_text, get_blank_data,
                       get_data_list_by_category, get_data_list_by_category_min_data, get_data_list_by_favorites, get_data_list_by_favorites_min_data,
                       get_data_list_by_query_text, get_data_list_by_query_text_min_data, get_inline_result, get_inline_result_min_data)
from markups import br, call_filters, filters


@dp.inline_handler()
async def main(query: types.InlineQuery):

    start_time = time.time()

    user = query.from_user
    
    query.query = clear_input_text(query.query)
    query_text = query.query


    offset = int(query.offset or 0)

    cache_time = 5
    max_value_page = 45
    max_dishes = max_value_page if offset else max_value_page - 1
    start = (offset * max_dishes - 1) if offset else 0

    if filters['favorites'] in query_text:
        data_list_time = time.time()
        # data_list = get_data_list_by_favorites(user, start, max_dishes)
        data_list = get_data_list_by_favorites_min_data(user, start, max_dishes)
        data_list_time_end = time.time()

    elif filters['category'] in query_text:
        data_list_time = time.time()
        # data_list = get_data_list_by_category(query_text, start, max_dishes)
        data_list = get_data_list_by_category_min_data(query_text, start, max_dishes)
        data_list_time_end = time.time()

    else:
        data_list_time = time.time()
        # data_list = get_data_list_by_query_text(query_text, start, max_dishes)
        data_list = get_data_list_by_query_text_min_data(query_text, start, max_dishes)
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

    # answer = get_inline_result(query, data_list[:50])
    answer = get_inline_result_min_data(query, query_text, data_list[:50])
    inline_reslt_time_end = time.time()

    query_answer_time = time.time()
    
    await query.answer(
            answer[:50],
            is_personal=True,
            cache_time=1,
            next_offset=next_offset,
        )

    query_answer_time_end = time.time()

    print(f'| query | "{query_text}"')
    print(f'| TIME  | data list = {data_list_time_end - data_list_time}')
    print(f'| TIME  | inline reslt = {inline_reslt_time_end - inline_reslt_time}')
    print(f'| TIME  | query answer = {query_answer_time_end - query_answer_time}')
    print(f'| TIME  | all = {query_answer_time_end - start_time}', end=br*2)


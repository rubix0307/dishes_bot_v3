from db.functions import (get_categories_data_from_id,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)



all_dish = sql('SELECT * FROM dishes WHERE preview = ""')
for data in all_dish:
    categories = get_categories_data_from_id(data['id'])
    ingredients = get_ingredients_data_from_id(data['id'])
    photos = get_photos_data_from_id(data['id'])

    if not len(photos):
        photos = ['https://upload.wikimedia.org/wikipedia/commons/9/9a/%D0%9D%D0%B5%D1%82_%D1%84%D0%BE%D1%82%D0%BE.png']

    sql(f'UPDATE `dishes` SET `preview`="{photos[0]}",`categories`="{categories}",`ingredients`="{ingredients}" WHERE id = {data["id"]}',
        commit=True)
    print(data["id"])
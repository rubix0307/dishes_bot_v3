

from db.functions import sql


all_photos = sql(f'''SELECT * FROM photos''')

for photo_data in all_photos:

    new_ph_path = photo_data['local_photo'].replace('images/','')
    sql(f'''UPDATE `photos` SET local_photo="{new_ph_path}" WHERE dish_id = {photo_data['dish_id']} AND local_photo = "{photo_data['local_photo']}"''', commit=True)

    if not photo_data['dish_id'] % 100:
        print(photo_data['dish_id']) 
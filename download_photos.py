
import os
import time
import requests
from db.functions import sql
from threading import Thread

def transliterate(name):
   """
   Автор: LarsKort
   Дата: 16/07/2011; 1:05 GMT-4;
   Не претендую на "хорошесть" словарика. В моем случае и такой пойдет,
   вы всегда сможете добавить свои символы и даже слова. Только
   это нужно делать в обоих списках, иначе будет ошибка.
   """
   # Слоаврь с заменами
   slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
      'ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'u','я':'ya', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'YO',
      'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
      'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
      'Ц':'C','Ч':'CH','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
      'Ю':'U','Я':'YA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'',
      '$':'','%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',
      ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
      '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
      'Є':'e', '—':''}
        
   # Циклически заменяем все буквы в строке
   for key in slovar:
      name = name.replace(key, slovar[key])
   return name



def download_photo(url, folder_path, filename) -> bool:

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


    p = requests.get(url.replace("c88x88", "900x-").replace("c620x415", "900x-"))
    out = open(f'{folder_path}{filename}', "wb")
    out.write(p.content)
    out.close()

    if os.path.exists(f'{folder_path}/{filename}'):
        return True
    return False




folder_num = 100
for id in range(1,10000):
    try:
        photos = sql(f'SELECT url FROM photos WHERE dish_id = {id}')
        
        for round, url in enumerate(photos):
            url = url['url']
            name = sql(f'SELECT title FROM dishes WHERE id = {id}')[0]['title']
            transl_name = f'{transliterate(name)}-{round+1}.{url.split(".")[-1]}'

            folder_path = f'images/{folder_num}/'
            
            if not os.path.exists(f'{folder_path}/{transl_name}'):
                is_download = download_photo(url, folder_path, transl_name)

                if is_download:
                    local_photo_path = f'{folder_path}{transl_name}'
                    sql(f'''UPDATE `photos` SET `local_photo`="{local_photo_path}" WHERE `url` = "{url}"''', commit=True)
                    print(f'{id}-{round}')
            else:
                if not id % 50 and not round:
                    print(f'{id}-{round} exists')

    except Exception as ex:
        pass

    finally:
        if not id % 100:
            folder_num += 100
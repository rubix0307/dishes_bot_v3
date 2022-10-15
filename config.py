import os
import dotenv
DEBUG = False
if DEBUG:
    print(f'⭕️ {DEBUG=}')

dotenv.load_dotenv('.env')
BOT_TOKEN = os.environ['BOT_TOKEN']
db_user = os.environ['db_user']
db_password = os.environ['db_password']

GROUG_ID = -1001624492781
ADMIN_ID = 887832606
BUY_AD_URL = 'https://t.me/xx_rubix_xx'

MEDIA_URL = 'https://obertivanie.com/tg_images/' if not DEBUG else 'C:/Users/artem/programming/aiogram/dishes_bot_v3/images/'
BOT_URL = 'https://t.me/best_recipe_bot'


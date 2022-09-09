import os
import dotenv
dotenv.load_dotenv('.env')

BOT_TOKEN = os.environ['BOT_TOKEN']
db_user = os.environ['db_user']
db_password = os.environ['db_password']
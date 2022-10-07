import time
from aiogram import Bot
from config import BOT_TOKEN
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import NetworkError

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    print('✅ bot is run')
    
    while 1:
        try:
            executor.start_polling(dp)
        except NetworkError:
            time.sleep(1)
    
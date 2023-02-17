from dotenv import load_dotenv
from bot.bot import MyChatBot
import os
from config import Config
from bot.telegram_api import TelegramAPI

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение переменных окружения
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')

if __name__ == '__main__':
    # Инициализация экземпляра чат-бота
    my_chat_bot = MyChatBot(
        telegram_bot_token=telegram_bot_token, 
        openai_api_key=openai_api_key
    )
    
    # Запуск чат-бота
    my_chat_bot.run()


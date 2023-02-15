import os

class Config:
    # Токен Telegram Bot API
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # API-ключ OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
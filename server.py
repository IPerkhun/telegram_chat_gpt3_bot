from bot.tg_bot import MyChatBot
from config import ConfigManager
from bot.openai_api import OpenAIManager

if __name__ == '__main__':
    my_chat_bot = MyChatBot(
        telegram_bot_token=ConfigManager().get_tg_bot_token(), 
        openai_api_key=OpenAIManager().openai_api_key
    )
    
    my_chat_bot.start()
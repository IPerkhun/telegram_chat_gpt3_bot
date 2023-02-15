from telegram import Bot
from telegram.error import TelegramError
import telegram

class TelegramAPI:
    def __init__(self, telegram_bot_token):
        self.telegram_bot_token = telegram_bot_token
        self.bot = Bot(token=telegram_bot_token, request=telegram.request.BaseRequest())

    def send_message(self, chat_id, message):
        try:
            response = self.bot.send_message(chat_id=chat_id, text=message)
            return response
        except TelegramError as error:
            print(f"An error occurred: {error}")
            return None

from dataclasses import dataclass
from typing import List

from bot.openai_api import OpenAIAPI
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters



@dataclass
class ConversationContext:
    user_id: int
    bot_name: str
    dialog_state: str = "idle"
    message_history: List[str] = None

class MyChatBot:
    def __init__(self, telegram_bot_token, openai_api_key):
        self.telegram_bot_token = telegram_bot_token
        self.openai_api = OpenAIAPI(openai_api_key)
        self.conversations = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(user_id, "MyBot")
        context = self.conversations[user_id]
        context.message_history = []
        context.dialog_state = "greeting"
        # Send greeting message to user here
        await update.message.reply_html(
            rf"Hi!",
            reply_markup=ForceReply(selective=True),
        )
        
    async def stop_dialog(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id in self.conversations:
            context = self.conversations[user_id]
            context.dialog_state = "idle"
            # Send goodbye message to user here
            await update.message.reply_html(
                rf"Bye!",
                reply_markup=ForceReply(selective=True),
            )
        else:
            # Send message to user saying there is no active dialog
            await update.message.reply_html(
                rf"There is no active dialog",
                reply_markup=ForceReply(selective=True),
            )
        
    async def new_dialog(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        self.conversations[user_id] = ConversationContext(user_id, "MyBot")
        context = self.conversations[user_id]
        context.message_history = ""
        context.dialog_state = "greeting"
        # Send greeting message to user here
        await update.message.reply_html(
            rf"Hi!",
            reply_markup=ForceReply(selective=True),
        )
        
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message.text
        user_id = update.effective_user.id
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(user_id, "MyBot")
        context = self.conversations[user_id]
        context_message_history = context.message_history

        if context_message_history is None:
            message = f"Human: {message}\m Bot:"
        else:
            message = f"{context_message_history}\nHuman: {message}\nBot:"

        response = self.openai_api.send_message(message)
        context.message_history += f"\nHuman: {update.message.text}\nBot: {response}"

        await update.message.reply_text(response)


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")


    def run(self) -> None:
        """Запуск чат-бота"""
        application = Application.builder().token(self.telegram_bot_token).build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stop", self.stop_dialog))
        application.add_handler(CommandHandler("new", self.new_dialog))


        # on non command i.e message - echo the message on Telegram
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        # Run the bot until the user presses Ctrl-C
        application.run_polling()
from bot.openai_api import OpenAIAPI
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class MyChatBot:
    def __init__(self, telegram_bot_token, openai_api_key):
        self.telegram_bot_token = telegram_bot_token
        self.openai_api = OpenAIAPI(openai_api_key)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.full_name}!",
            reply_markup=ForceReply(selective=True),
    )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")


    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        message = update.message.text
        response = self.openai_api.send_message(message)
        await update.message.reply_text(response)



    def run(self) -> None:
        """Запуск чат-бота"""
        application = Application.builder().token(self.telegram_bot_token).build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))

        # on non command i.e message - echo the message on Telegram
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        # Run the bot until the user presses Ctrl-C
        application.run_polling()



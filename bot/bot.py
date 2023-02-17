from dataclasses import dataclass
from typing import List

from bot.openai_api import OpenAIAPI
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from bot.telegram_api import TelegramAPI
from telegram import KeyboardButton

# Define the keyboard with the short commands
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton('/start'), KeyboardButton('/help')],
        [KeyboardButton('/stop'), KeyboardButton('/new')]
    ],
    resize_keyboard=False,
    one_time_keyboard=True
)

@dataclass
class ConversationContext:
    user_id: int
    bot_name: str
    dialog_state: str = "paused"
    message_history: List[str] = None

class MyChatBot:
    def __init__(self, telegram_bot_token, openai_api_key):
        self.telegram_bot_token = telegram_bot_token
        self.openai_api = OpenAIAPI(openai_api_key)
        self.telegram_api = TelegramAPI(telegram_bot_token)
        self.conversations = {}
        self.application: Application = Application.builder().token(self.telegram_bot_token).build()


    def _check_existing_conversation(self, update: Update) -> bool:
        """
        Check if the user has an existing conversation. 
        return True if the user has an existing conversation, False otherwise.
        """
        return update.effective_user.id in self.conversations

    def _create_conversation(self, update: Update) -> None:
        """ Create a new conversation for the user """
        self.conversations[update.effective_user.id] = ConversationContext(
            user_id=update.effective_user.id,
            bot_name=f"Bot_{update.effective_user.id}",
        )
    
    def _swith_dialog_state(self, update: Update, state: str) -> None:
        """ Switch the dialog state of the user"""
        user_id = update.effective_user.id
        context = self.conversations[user_id]
        context.dialog_state = state

    def _get_dialog_state(self, update: Update) -> str:
        """ Get the dialog state of the user. States: "paused", "active" """
        user_id = update.effective_user.id
        print(self.conversations)
        context = self.conversations[user_id]
        return context.dialog_state

    async def start(self, update: Update, callback_context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        print(self._check_existing_conversation(update))
        if not self._check_existing_conversation(update):
            self._create_conversation(update)
        self._swith_dialog_state(update, "active")
        print(
                f"Conversation with user {user_id} has been created", 
                f"State: {self._get_dialog_state(update)}",
        )
        self.conversations[user_id].message_history = []
        await update.message.reply_html(
            text = rf"Hi!. Use /help to get a list of commands",    
        )

    async def stop_dialog(self, update: Update, callback_context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if self._check_existing_conversation(update):
            self._swith_dialog_state(update, "paused")
            await update.message.reply_html(text = rf"Bye!")
            print(
                f"Conversation with user {user_id} has been deleted", 
                f"State: {self._get_dialog_state(update)}",
            )
            del self.conversations[user_id]
        else:
            await update.message.reply_html(
                text = rf"There is no active dialog. Use /start to start a new dialog",
            )
        
    async def new_dialog(self, update: Update, callback_context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if self._check_existing_conversation(update):
            self._swith_dialog_state(update, "active")
            self.conversations[user_id].message_history = []
            await update.message.reply_html(
                text = rf"Hi!. Ask me something. For example: Let's talk about the weather"    
            )
        else:
            await update.message.reply_html(
                text = rf"There is no active dialog, use /start to start a new dialog",
            )
        
    def _is_paused(self, update: Update) -> bool:
        if self._get_dialog_state(update) == "paused":
            return True
        else:
            return False

    async def prepare_conversation(self, update: Update) -> bool:
        print(self.conversations)
        if not self._check_existing_conversation(update):
            self._create_conversation(update)
        if self._is_paused(update):
            return False
        return True

    def update_context_message_history(self, context: ConversationContext, message_with_history: str, response: str) -> None:
        context.message_history = f"{message_with_history}{response}"

    
    async def _send_message(self, update: Update, message: str) -> None:
        user_id = update.effective_user.id
        message = update.message.text

        context = self.conversations[user_id]
        message_with_history = self._get_message_with_history(message, context)
        
        response = self.openai_api.send_message(message_with_history)
        self.update_context_message_history(context, message_with_history, response)
        
        print(context.message_history, context.dialog_state)
        await self.telegram_api.send_message(update.message.chat_id, response, keyboard)

    async def echo(self, update: Update, callback_context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.prepare_conversation(update):
            await self._send_message(update, update.message.text)
        else:
            return None    

    def _get_message_with_history(self, message, context):
        if context.message_history is None:
            message_with_history = f"Human: {message}\nBot:"
        else:
            message_with_history = f"{context.message_history}\nHuman: {message}\nBot:"
        return message_with_history

    async def help_command(self, update: Update, callback_context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued. Explain the bot's purpose"""
        text = (
            "Hi! I'm a bot that can talk to you. I use OpenAI's GPT-3 to generate responses. "
            "Here are some things you can ask me to do:\n\n"
            "📅 Plan your day\n"
            "🍝 Find a recipe\n"
            "💸 Allocate a budget\n"
            "📝 Write a poem or a story\n"
            "🎶 Generate song lyrics\n"
            "🎨 Create art prompts\n"
            "📚 Find book recommendations\n"
            "🗺️ Generate travel itineraries\n"
            "🎬 Come up with movie ideas\n"
            "🎲 Generate random ideas\n\n"
            "Use /stop to stop the conversation.\n"
            "Use /new to start a new conversation.\n"
            "Use /help to see this message again. "
        )
        await update.message.reply_html(text)


    def run(self) -> None:
        """Запуск чат-бота"""

        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("start", self.start, filters.COMMAND, ))
        self.application.add_handler(CommandHandler("help", self.help_command, filters.COMMAND))
        self.application.add_handler(CommandHandler("stop", self.stop_dialog, filters.COMMAND))
        self.application.add_handler(CommandHandler('new', self.new_dialog, filters.COMMAND))

        # on non command i.e message - echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        # Run the bot until the user presses Ctrl-C
        self.application.run_polling()

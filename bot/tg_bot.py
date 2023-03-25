from aiogram import Bot, Dispatcher, executor, types
from config import ConfigManager
import logging
from bot.openai_api import OpenAIManager
from aiogram.utils.exceptions import TelegramAPIError, CantParseEntities

class MyChatBot:
    def __init__(self, telegram_bot_token, openai_api_key):
        # Set up logging
        logging.basicConfig(level=logging.INFO)

        # Create bot and dispatcher instances

        self.bot = Bot(token=telegram_bot_token)
        self.dp = Dispatcher(self.bot)

        # Create OpenAI manager instance
        self.openai_manager = OpenAIManager(openai_api_key)

        # Define message history as an instance variable
        self.message_history = [{"role": "system", "content": "You are a friendly and helpful teaching assistant. You explain concepts in great depth using simple terms, and you give examples to help people learn. At the end of each explanation, you ask a question to check for understanding"}]

        # Register message handlers
        self.dp.register_message_handler(self.send_welcome, commands=['start'])
        self.dp.register_message_handler(self.send_help, commands=['help'])
        self.dp.register_message_handler(self.echo)


    async def setup_bot_commands(self, dispatcher: Dispatcher):
        commands = [
            types.BotCommand(command="/start", description="Start the bot"),
            types.BotCommand(command="/help", description="Get help"),
        ]
        await dispatcher.bot.set_my_commands(commands)

    async def send_welcome(self, message: types.Message):
        await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    
    async def new_conversation(self, message: types.Message):
        self.message_history = [{"role": "system", "content": "You are a friendly and helpful teaching assistant. You explain concepts in great depth using simple terms, and you give examples to help people learn. At the end of each explanation, you ask a question to check for understanding"}]
        await message.reply("Let's start a new conversation.")

    async def send_help(self, message: types.Message):
        """Send a message when the command /help is issued."""
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
        await message.reply(text)

    async def echo(self, message: types.Message):
        try:
            user_input = message.text
            if len(user_input) > 2048:
                await message.answer("Message is too long.")
                raise ValueError("Message is too long.")
            self.message_history.append({"role": "user", "content": user_input})

            num_tokens = sum(len(msg["content"].split()) for msg in self.message_history)
            if num_tokens > 3500:
                self.message_history = self.clean_messages()
                await message.answer(f"Message is too long. {self.message_history}")
                raise ValueError("Message is too long.")
            await self.bot.send_chat_action(message.chat.id, 'typing')

            # Get OpenAI response
            openai_response = await self.openai_manager.get_openai_response(self.message_history)
            self.message_history.append({"role": "assistant", "content": openai_response})

            # Send message with different parse modes until one works
            parse_modes = ['MarkdownV2', 'Markdown', 'HTML']
            for parse_mode in parse_modes:
                try:
                    await message.answer(openai_response, parse_mode=parse_mode)
                    break
                except CantParseEntities:
                    if parse_mode == parse_modes[-1]:
                        raise

        except (TelegramAPIError, ValueError) as e:
            logging.error(f"Error processing message: {str(e)}")
            error_message = "Sorry, there was an error processing your request. Please try again later."
            self.message_history = self.clean_messages()
            await message.answer(error_message)

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            self.message_history = self.clean_messages()

    def clean_messages(self):
        first_message = "You are a friendly and helpful teaching assistant. You explain concepts in great depth using simple terms, and you give examples to help people learn. At the end of each explanation, you ask a question to check for understanding"
        message_history = [{"role": "system", "content": first_message}]
        return message_history

    def start(self):
        executor.start_polling(self.dp, skip_updates=True, on_startup=self.setup_bot_commands)

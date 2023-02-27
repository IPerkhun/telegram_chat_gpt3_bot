import time
import os
import re

import telegram
from telegram.error import BadRequest, RetryAfter

from playwright.sync_api import sync_playwright


import logging

import dotenv
import nest_asyncio



from functools import wraps
nest_asyncio.apply()
dotenv.load_dotenv()

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from telegram.helpers import escape_markdown
from dotenv import load_dotenv

load_dotenv()

# USER_ID = int(os.getenv('TELEGRAM_USER_ID'))
OPEN_AI_EMAIL = os.getenv('OPEN_AI_EMAIL')
OPEN_AI_PASSWORD = os.getenv('OPEN_AI_PASSWORD')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)
# log = logging.getLogger("myapp")

PLAY = sync_playwright().start()
# Chrome doesnt seem to work in headless, so we use firefox
BROWSER = PLAY.firefox.launch_persistent_context(
    user_data_dir="/tmp/playwright",
    headless=(os.getenv('HEADLESS_BROWSER', 'False') == 'True')
)
PAGE = BROWSER.new_page()
# stealth_sync(PAGE)

"""Start the bot."""
# Create the Application and pass it your bot's token.
application = Application.builder().token(TELEGRAM_API_KEY).build()

USER_ID =  67306629

# print(USER_ID)

def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("textarea")

def is_logged_in():
    # See if we have a textarea with data-id="root"
    return get_input_box() is not None

def send_message(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")

class AtrributeError:
    pass

def get_last_message():
    """Get the latest message"""
    page_elements = PAGE.query_selector_all("div[class*='prose']")

    if len(page_elements) == 0:
        response = "No response from OpenAI"
        return response
    
    # get the last element
    prose = page_elements[-1]

    try:
        code_blocks = prose.query_selector_all("pre")
    except Exception as e:
        response = 'Server probably disconnected, try running /reload and then /start again'
        return response
    

    if len(code_blocks) > 0:
        # get all children of prose and add them one by one to respons
        response = ""
        for child in prose.query_selector_all('p,pre'):
            logger.info(child.get_property('tagName'))
            if str(child.get_property('tagName')) == "PRE":
                code_container = child.query_selector("code")
                response += f"\n```\n{escape_markdown(code_container.inner_text(), version=2)}\n```"
            else:
                #replace all <code>x</code> things with `x`
                text = child.inner_html()
                response += escape_markdown(text, version=2)
                response = response.replace("<code\>", "`").replace("</code\>", "`")
    else:
        response = escape_markdown(prose.inner_text(), version=2)
    return response

# create a decorator called auth that receives USER_ID as an argument with wraps
def auth(user_id):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            if update.effective_user.id == user_id:
                await func(update, context)
            else:
                await update.message.reply_text("You are not authorized to use this bot")
        return wrapper
    return decorator

@auth(USER_ID)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

@auth(USER_ID)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

@auth(USER_ID)
async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    print(f"Got a reload command from user {update.effective_user.id}")
    PAGE.reload()
    await update.message.reply_text("Reloaded the browser!")
    await update.message.reply_text("Let's check if it's workin!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    try:
        # Send the message to OpenAI
        send_message(update.message.text)
        await check_loading(update)
        response = get_last_message()
        await update.message.reply_text(response, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    except BadRequest as e:
        # Handle Telegram errors due to invalid message formatting or entities
        await update.message.reply_text(f"Error: {e.message}")
    except RetryAfter as e:
        # Handle Telegram rate limit errors by waiting and retrying
        time.sleep(e.retry_after)
        await echo(update, context)
    except Exception as e:
        # Handle other exceptions by logging the error and notifying the user
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text(
            f"Sorry, an unexpected error occurred. Please try again later. Try running /reload and then /start again {e}"
            )

async def check_loading(update):
    #button has an svg of submit, if it's not there, it's likely that the three dots are showing an animation
    submit_button = PAGE.query_selector_all("textarea+button")[0]
    # with a timeout of 90 seconds, created a while loop that checks if loading is done
    loading = submit_button.query_selector_all(".text-2xl")
    #keep checking len(loading) until it's empty or 45 seconds have passed
    await application.bot.send_chat_action(update.effective_chat.id, "typing")
    start_time = time.time()
    while len(loading) > 0:
        if time.time() - start_time > 90:
            break
        time.sleep(0.5)
        loading = submit_button.query_selector_all(".text-2xl")
        await application.bot.send_chat_action(update.effective_chat.id, "typing")


def start_browser():

    PAGE.goto("https://chat.openai.com/")
    if not is_logged_in():
        print("Please log in to OpenAI Chat")
        print("Press enter when you're done")
        
        PAGE.locator("button", has_text="Log in").click()

        username = PAGE.locator('input[name="username"]')
        username.fill(OPEN_AI_EMAIL)
        username.press("Enter")

        password = PAGE.locator('input[name="password"]')
        password.fill(OPEN_AI_PASSWORD)
        password.press("Enter")
        
        # On first login
        try:
            next_button = PAGE.locator("button", has_text="Next")
            next_button.click()
            next_button = PAGE.locator("button", has_text="Next")
            next_button.click()
            next_button = PAGE.locator("button", has_text="Done")
            next_button.click()
        except:
            pass
    # Clear old conversations
    try:
        PAGE.locator('a:has-text("Clear conversations")').click()
        PAGE.locator('a:has-text("Confirm clear conversations")').click()
    except:
        pass

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reload", reload))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    start_browser()
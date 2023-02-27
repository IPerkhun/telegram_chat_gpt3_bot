#%%
import os
import uuid

from db_utils.user_db_manager import UserDatabaseManager
from db_utils.models.users import User
import dotenv

dotenv.load_dotenv()

tg_api_key = os.getenv('TELEGRAM_API_KEY')
open_ai_password = os.getenv('OPEN_AI_PASSWORD')
open_ai_login = os.getenv('OPEN_AI_EMAIL')
open_ai_api_key = os.getenv('OPEN_AI_API_KEY')


users_db = UserDatabaseManager.get_instance('db_utils/db/users.db')

user_2 = User(id=str(uuid.uuid4()), tg_api_key=tg_api_key, open_ai_password=open_ai_password, open_ai_login=open_ai_login, open_ai_api_key=open_ai_api_key, active=True)
user_3 = User(id=str(uuid.uuid4()), tg_api_key=tg_api_key, open_ai_password=open_ai_password, open_ai_login=open_ai_login, open_ai_api_key=open_ai_api_key, active=True)

#%%
from bot.bot import MyChatBot

all_active_users = users_db.get_active_users()
all_active_users



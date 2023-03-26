#%%
from db_utils.user_db_manager import UserDatabaseManager
from db_utils.models.users import User

db_path = 'db_utils/db/test.db'
db_manager = UserDatabaseManager.get_instance(db_path)


#%%
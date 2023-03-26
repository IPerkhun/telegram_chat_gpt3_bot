#%%
import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from db_utils.models.users import User, Base




logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(level=logging.DEBUG)
formatter =  logging.Formatter("%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


class UserDatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls, db_path):
        if cls._instance is None:
            cls._instance = cls._create_instance(db_path)
            logger.debug(f"Created UserDB instance with path: {db_path}")
        else:
            logger.debug(f"UserDB instance already exists with path: {db_path}")
        return cls._instance

    @classmethod
    def _create_instance(cls, db_path):

        engine = create_engine(f"sqlite:///{db_path}")
        insp = inspect(engine)
        if 'users' not in insp.get_table_names():
            Base.metadata.create_all(engine)
            logger.debug("Created users table")
        else:
            logger.debug("Users table already exists")
        os.chmod(db_path, 0o600)
        Session = sessionmaker(bind=engine)
        session = Session()
        return cls(session)

    def __init__(self, session):
        self.session: Session = session

    def get_all_users(self):
        return self.session.query(User).all()

    def get_active_users(self):
        return self.session.query(User).filter(User.active == True).all()

    def get_user_by_tg_api_key(self, tg_api_key):
        return self.session.query(User).filter(User.tg_api_key == tg_api_key).first()

    def get_user_by_open_ai_login(self, open_ai_login):
        return self.session.query(User).filter(User.open_ai_login == open_ai_login).first()

    def get_user_by_open_ai_api_key(self, open_ai_api_key):
        return self.session.query(User).filter(User.open_ai_api_key == open_ai_api_key).first()

    def create_user(self, user):
        existing_user = self.get_user_by_open_ai_login(user.open_ai_login)
        if existing_user is not None:
            raise ValueError(f"User with open_ai_login={user.open_ai_login} already exists")

        existing_user = self.get_user_by_tg_api_key(user.tg_api_key)
        if existing_user is not None:
            raise ValueError(f"User with tg_api_key={user.tg_api_key} already exists")

        existing_user = self.get_user_by_open_ai_api_key(user.open_ai_api_key)
        if existing_user is not None:
            raise ValueError(f"User with open_ai_api_key={user.open_ai_api_key} already exists")

        self.session.add(user)
        self.session.commit()

    def update_user_status(self, user_id, active):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ValueError(f"User with id={user_id} does not exist")

        user.active = active
        self.session.commit()

    def remove_user(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ValueError(f"User with id={user_id} does not exist")

        self.session.delete(user)
        self.session.commit()



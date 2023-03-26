import json
from sqlalchemy import create_engine, Column, String, Boolean, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    tg_api_key = Column(String)
    open_ai_password = Column(String)
    open_ai_login = Column(String)
    open_ai_api_key = Column(String)
    active = Column(Boolean)
    
    def __repr__(self):
        return json.dumps({
            "id": self.id,
            "tg_api_key": self.tg_api_key,
            "open_ai_password": self.open_ai_password,
            "open_ai_login": self.open_ai_login,
            "open_ai_api_key": self.open_ai_api_key,
            "active": self.active
        }, indent=4)
    
    def __str__(self):
        return self.__repr__()
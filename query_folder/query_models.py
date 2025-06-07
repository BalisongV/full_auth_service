from sqlalchemy import Column, Integer, String
from query_database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, nullable=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) 

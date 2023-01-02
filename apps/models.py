from .database import Base
from sqlalchemy import String, Integer, Column


class Users(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

# class Profiles(Base):
#     __tablename__="profiles"
#     id = Column(Integer, primary_key=True, index=True)
#     address = Column(String)
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///dictionaryy.db', echo=True)
Base = declarative_base()


class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	username = Column(String)
	password = Column(String)

	def __init__(self, username, password):
		self.username = username
		self.password = password


Base.metadata.create_all(engine)
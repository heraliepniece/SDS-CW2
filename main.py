import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine("sqlite:///app.db")  #Uses SQLite to store the database in a file called app.db

class User(Base):
    __tablename__ = 'users' #Creates a table called users

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  #'team_member' or 'project_manager'


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

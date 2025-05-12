from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  # 'team_member' or 'project_manager'
    created_at = Column(String, default=datetime.datetime.utcnow().isoformat)

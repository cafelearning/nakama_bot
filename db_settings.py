import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


DATABASE_URL = 'sqlite:///bot.db'
# Set up SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


# Define the Admin model
class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user ID
    username = Column(String, nullable=True)  # Optional username


def is_user_admin(user_id):
    session = Session()
    result = session.query(Admin).filter_by(user_id=user_id).first()
    session.close()
    return result is not None


# Initialize the database
def init_db():
    Base.metadata.create_all(engine)


# Function to save admin user ID to the database
def save_admin_to_db(user_id):
    session = Session()
    admin = Admin(user_id=user_id)
    session.add(admin)
    try:
        session.commit()
    except:
        session.rollback()  # Ignore duplicate entries
    finally:
        session.close()


def get_admins():
    session = Session()
    result = session.query(Admin).all()
    admins = []
    for admin in result:
        admins.append(admin.user_id)
    return admins


class Episode(Base):
    __tablename__ = 'episodes'
    id = Column(Integer, primary_key=True)
    episode_number = Column(Integer, nullable=False)  # Episode number or title
    anime = Column(String, nullable=False)
    version = Column(String, nullable=False)
    file_id = Column(String, nullable=False)  # Store the file ID for the version


def save_file_to_db(file_id, anime_name, file_number, file_version):
    session = Session()
    file_record = Episode(file_id=file_id, anime=anime_name, episode_number=file_number, version=file_version)
    session.add(file_record)
    session.commit()
    record_id = file_record.id
    session.close()
    return record_id


def get_file_from_db(ep_id):
    session = Session()
    result = session.query(Episode).filter_by(id=ep_id).first()
    session.close()
    return result

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()

from detectoid.config import get_config
from detectoid.model.user import User

session_maker = None

def get_session():
    """
    Returns an sqlalchemy session open on the database
    """
    global session_maker

    if session_maker is None:
        db_uri = get_config()['sqlalchemy.database_uri']
        db_engine = create_engine(db_uri)
        DeclarativeBase.metadata.create_all(db_engine)

        binds = {
            User: db_engine
        }

        session_maker = sessionmaker(autocommit=True, expire_on_commit=False)
        session_maker.configure(binds=binds)

    return session_maker()

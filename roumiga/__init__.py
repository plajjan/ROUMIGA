

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import DateTime, Float, Integer, String, Text, Interval

import datetime

DeclarativeBase = declarative_base()
engine = create_engine('sqlite:///roumiga.db', echo=False)
DeclarativeBase.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()
DBSession = scoped_session(Session)


class Snapshot(DeclarativeBase):
    """ A snapshot - ie the state of a node at a certain point in time
    """
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key = True)
    time = Column(DateTime, default=datetime.datetime.utcnow())
    name = Column(Text)


    def __init__(self, name = None):
        if name:
            self.name = name


    @classmethod
    def list(cls):
        return DBSession.query(Snapshot).all()

    @classmethod
    def from_id(cls, id):
        return DBSession.query(Snapshot).filter(Snapshot.id==id).one()

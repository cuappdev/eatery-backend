from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

Engine = create_engine("sqlite:///newdata.sqlite3", convert_unicode=True)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=Engine))


class TableNameBase(object):
    @declared_attr
    def __tablename__(cls):
        class_name = cls.__name__  # e.g. Hour
        table_name = class_name[0].lower() + class_name[1:] + "s"  # e.g. hours
        return table_name


Base = declarative_base(cls=TableNameBase)
Base.query = Session.query_property()

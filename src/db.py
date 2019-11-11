from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr


engine = create_engine("sqlite:///data.sqlite3", convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


class TableNameBase(object):
    @declared_attr
    def __tablename__(cls):
        class_name = cls.__name__  # e.g. Hour
        table_name = class_name[0].lower() + class_name[1:] + "s"  # e.g. hours
        return table_name


Base = declarative_base(cls=TableNameBase)
Base.query = db_session.query_property()

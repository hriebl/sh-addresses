import sqlalchemy.orm
from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Address(Base):
    __tablename__ = "addresses"

    id = Column(String, primary_key=True)
    postcode = Column(String, ForeignKey("postcodes.id"), nullable=True)
    street = Column(String, ForeignKey("streets.id"), nullable=False)
    number = Column(Integer, nullable=False)
    extension = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)


class Postcode(Base):
    __tablename__ = "postcodes"

    id = Column(String, primary_key=True)
    code = Column(String, nullable=False)
    city = Column(String, nullable=False)


class Street(Base):
    __tablename__ = "streets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class Session(sqlalchemy.orm.Session):
    def __init__(self, path):
        engine = create_engine(f"sqlite:///{path / 'database.db'}")
        Base.metadata.create_all(engine)
        super().__init__(engine)

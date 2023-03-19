from db_session import SqlAlchemyBase
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime


class Tariffs(SqlAlchemyBase):
    __tablename__ = "tariff"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=True)


class ArbAutoUpdates(SqlAlchemyBase):
    __tablename__ = "arb_auto_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wait_time = Column(Integer, nullable=False, unique=True)


class Users(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    username = Column(String, nullable=True)
    sub_type = Column(String, ForeignKey("tariff.name"), nullable=True)
    last_paid_date = Column(DateTime, nullable=True)
    next_pay_date = Column(DateTime, nullable=True)
    arb_auto_update = Column(Integer, ForeignKey("arb_auto_updates.wait_time"), nullable=True)

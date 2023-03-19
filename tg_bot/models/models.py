from sqlalchemy.ext.asyncio import AsyncSession

from db_session import SqlAlchemyBase
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy import select


class Tariffs(SqlAlchemyBase):
    __tablename__ = "tariff"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=True)


class ArbAutoUpdates(SqlAlchemyBase):
    __tablename__ = "arb_auto_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wait_time = Column(Integer, nullable=False, unique=True)

    @classmethod
    async def get_all(cls, session):
        query = await session.execute(select(cls))
        return query.scalars().all()


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

    @classmethod
    async def set_autoupdate(cls, session: AsyncSession, user, wait_time):
        user.arb_auto_update = int(wait_time)
        session.add(user)
        await session.commit()

    @classmethod
    async def get_user_by_tg_id(cls, session: AsyncSession, tg_id):
        query = await session.execute(select(cls).where(cls.tg_id == tg_id))
        return query.scalar()

    @classmethod
    async def load_user_data(cls, session: AsyncSession, tg_id: int, name: str, surname: str, username: str):
        if user := await Users.get_user_by_tg_id(session, tg_id):
            if user.name != name:
                user.name = name
            if user.surname != surname:
                user.surname = surname
            if user.username != username:
                user.username = username
        else:
            user = Users(
                tg_id=tg_id,
                name=name,
                surname=surname,
                username=username
            )

        session.add(user)
        await session.commit()

        return user

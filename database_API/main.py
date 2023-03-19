import asyncio

from fastapi import FastAPI
from auth import CheckUser
from db_session import global_init, SqlAlchemyBase, create_session
from sqladmin import Admin
from admin_config import *
from views import UserView, TariffView, UpdateView
from models import ArbAutoUpdates, Tariffs

app = FastAPI()
engine = global_init(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
authentication_backend = CheckUser(secret_key=JWT_SECRET)
admin = Admin(app, engine, authentication_backend=authentication_backend)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)
    async with create_session() as session:
        for time in [2, 5, 10, 30]:
            autoupdate = ArbAutoUpdates(wait_time=time)
            session.add(autoupdate)
        for default_tariff in [["Базовый", 0], ["Неделя", 159], ["Две недели", 249], ["Месяц", 399]]:
            tariff = Tariffs(name=default_tariff[0], price=default_tariff[-1])
            session.add(tariff)
        await session.commit()


asyncio.create_task(init_models())

admin.add_view(UserView)
admin.add_view(TariffView)
admin.add_view(UpdateView)

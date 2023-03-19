from functools import wraps

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import sqlalchemy.ext.declarative as dec
from sqlalchemy.orm import sessionmaker

SqlAlchemyBase = dec.declarative_base()

__factory = None


async def global_init(user, password, host, port, dbname):
    global __factory

    if __factory:
        return
    conn_str = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_async_engine(conn_str, pool_pre_ping=True)

    # Создание всех таблиц
    async with engine.begin() as conn:
        # await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)

    __factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )


def create_session() -> AsyncSession:
    global __factory
    return __factory()


def session_db(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with create_session() as session:
            return await func(*args, session=session, **kwargs)

    return wrapper

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from db_session import global_init
from admin_config import *
from handlers import register_handlers_default
from handlers.autoupdate import register_handlers_autoupdate
from handlers.exchanges import register_handlers_exchanges
from handlers.percents import register_handlers_percents

logger = logging.getLogger(__name__)


async def main():
    await global_init(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting tg_bot")

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_default(dp)
    register_handlers_exchanges(dp)
    register_handlers_percents(dp)
    register_handlers_autoupdate(dp)

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import textwrap
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ParseMode, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from sqlalchemy.ext.asyncio import AsyncSession

from APIs.CcxtAPI import CcxtAPI
from APIs.PairList import PairList
from db_session import session_db
from keys.percents import get_percents_settings_kb
from keys.settings import *
from models import Users
from states import UserStates


@session_db
async def welcome_message(message: Message, state: FSMContext, session: AsyncSession):
    user_info = message.from_user
    await Users.load_user_data(
        session, user_info["id"],
        user_info["first_name"], user_info["last_name"],
        user_info["username"]
    )

    await state.update_data(chosen_exchanges=[])
    await state.update_data(chosen_percents=None)
    await state.update_data(arbitrage_type=None)

    await message.answer(
        text="Привет!\nЯ бот, который поможет тебе отслеживать актуальный арбитраж по "
             "разным торговым парам криптовалют\n\n",
        reply_markup=get_arbitrages_kb()
    )


@session_db
async def arbitrage_menu_message(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    user_info = callback_query.from_user
    user = await Users.load_user_data(
        session, user_info["id"], user_info["first_name"], user_info["last_name"], user_info["username"]
    )

    chosen_exchanges = user_data.get('chosen_exchanges', [])
    chosen_percents = user_data.get('chosen_percents', None)
    arbitrage_type = user_data.get('arbitrage_type', None)

    setting_kb = get_settings_kb(settings_set=len(chosen_exchanges) > 1 and chosen_percents and user.arb_auto_update)

    await state.reset_state(with_data=False)

    await callback_query.message.edit_text(
        text=f"Вы выбрали:\n"
             f" - Биржи: {', '.join(chosen_exchanges) if chosen_exchanges else 'не выбрано'}\n"
             f" - Проценты: {chosen_percents if chosen_percents else 'не выбраны'}\n"
             f" - Автообновление: каждые {user.arb_auto_update}м",
        reply_markup=setting_kb
    )


@session_db
async def get_arbitrage(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(UserStates.arbitrage_loop)
    msg = await callback_query.message.edit_text(text="Загрузка данных")

    user = await Users.get_user_by_tg_id(session, callback_query.from_user.id)
    user_data = await state.get_data()
    chosen_exchanges = user_data.get('chosen_exchanges')
    chosen_percents = user_data.get('chosen_percents')
    crypto_api = CcxtAPI(msg)

    while True:
        arbitrage = await crypto_api.get_arbitrage(chosen_exchanges, chosen_percents)

        text = PairList.get_percent_arbitrage_text(arbitrage, chosen_percents)
        menu_kb = get_percents_settings_kb(chosen_percents, exclude_selected=True)

        try:
            await msg.edit_text(
                text=textwrap.dedent(text),
                parse_mode=ParseMode.HTML,
                reply_markup=menu_kb
            )
        except MessageNotModified:
            continue
        await asyncio.sleep(user.arb_auto_update * 60)
        user_data = await state.get_data()
        user_state = await state.get_state()
        if user_state != "UserStates:arbitrage_loop" or chosen_percents != user_data.get('chosen_percents'):
            break


def register_handlers_default(dp: Dispatcher):
    dp.register_message_handler(welcome_message, commands=['start', 'help'])
    dp.register_callback_query_handler(
        get_arbitrage, lambda c: c.data == 'arbitrage',
        state=[UserStates.arbitrage_loop, None]
    )
    dp.register_callback_query_handler(
        arbitrage_menu_message, lambda c: c.data in ['menu', 'back'],
        state=['*']
    )

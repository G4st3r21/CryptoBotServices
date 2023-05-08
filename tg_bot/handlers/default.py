import asyncio
import textwrap
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ParseMode, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from sqlalchemy.ext.asyncio import AsyncSession

from APIs import CcxtAPI
from db_session import session_db
from keys.percents import generate_percents_settings_keyboard
from keys.settings import *
from models import Users
from states import UserStates


async def format_arbitrage(type_arb, arbitrages: list):
    if arbitrages == "Не найдено подходящих пар":
        string = arbitrages
    else:
        string = "\n".join([
            f"{arbitrage['symbol']}\n"
            f"{arbitrage['buy_exchange']}/{arbitrage['sell_exchange']} = {'%.2f' % arbitrage['opportunity']}%"
            for arbitrage in arbitrages
        ])
    arbitrage_str = f"Актуальный арбитраж на {datetime.now().time().strftime('%H:%M')}\n" \
                    f"Процентный диапазон: {type_arb}%\n" \
                    f"{string}"

    return arbitrage_str


@session_db
async def menu_message(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    user_info = callback_query.from_user
    user = await Users.load_user_data(
        session, user_info["id"],
        user_info["first_name"], user_info["last_name"],
        user_info["username"]
    )
    chosen_exchanges = user_data.get('chosen_exchanges', None)
    chosen_percents = user_data.get('chosen_percents', None)
    if chosen_exchanges and len(chosen_exchanges) > 1 and chosen_percents and user.arb_auto_update:
        setting_kb = generate_settings_keyboard(settings_set=True)
    else:
        setting_kb = generate_settings_keyboard(settings_set=False)

    await state.reset_state(with_data=False)

    chosen_exchanges = ', '.join(user_data['chosen_exchanges']) \
        if user_data.get('chosen_exchanges') else "не выбрано"
    chosen_percents = user_data['chosen_percents'] \
        if user_data.get('chosen_percents') else "не выбраны"

    await callback_query.message.edit_text(
        text="Вы выбрали:\n"
             f" - Биржи: {chosen_exchanges}\n"
             f" - Проценты: {chosen_percents}\n"
             f" - Автообновление: каждые {user.arb_auto_update}м",
        reply_markup=setting_kb
    )


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

    setting_kb = generate_settings_keyboard()

    await message.answer(
        text="Привет!\nЯ бот, который поможет тебе отслеживать актуальный арбитраж по "
             "разным торговым парам криптовалют\n\n"
             "Выберите по каким биржам исследовать арбитраж(минимум 2)\n"
             "Диапазон процентов, которые вас интересуют\n"
             "И автообновление данных в сообщении",
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

    while True:
        full_arbitrage = await async_test.get_arbitrage(chosen_exchanges)
        percent_arbitrage = full_arbitrage[chosen_percents]

        text = await format_arbitrage(chosen_percents, percent_arbitrage)
        menu_kb = generate_percents_settings_keyboard(chosen_percents)

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
        menu_message, lambda c: c.data in ['menu', 'back'],
        state=['*']
    )

import asyncio
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ParseMode, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from APIs.MarketsAPI import MarketsAPI
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
            f"{arbitrage['pair']}\n"
            f"{arbitrage['buy_exchange']} {arbitrage['sell_exchange']} = {arbitrage['arbitrage']}%"
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

    user_data = await state.get_data()
    chosen_exchanges = user_data.get('chosen_exchanges', None)
    chosen_percents = user_data.get('chosen_percents', None)

    user: Users = await Users.get_user_by_tg_id(session, callback_query.from_user.id)
    menu_kb = generate_percents_settings_keyboard(chosen_percents)

    real_time_state = await state.get_state()
    while user.arb_auto_update and \
            real_time_state == 'UserStates:arbitrage_loop' and \
            chosen_percents == user_data.get('chosen_percents', None):
        api = MarketsAPI()
        await msg.edit_text(text="Получаем список торговых пар для каждой биржи", )
        common_pairs, all_exchanges = await api.get_all_prices(chosen_exchanges)
        await msg.edit_text(text="Находим цену покупки и продажи на каждой бирже для каждой общей пары", )
        buy_sell_prices = await api.get_buy_sell_prices(all_exchanges, common_pairs)
        await msg.edit_text(text="Находим арбитраж на каждой общей паре")
        full_arbitrage = await api.calculate_arbitrage(buy_sell_prices)
        if full_arbitrage:
            await msg.edit_text(text="Проверяем валидность полученных пар")
            valid_arbitrage = await api.check_pair_validity(full_arbitrage[chosen_percents])
        else:
            valid_arbitrage = full_arbitrage[chosen_percents] \
                if len(full_arbitrage[chosen_percents]) > 0 else "Не найдено подходящих пар"

        await msg.edit_text(
            text=await format_arbitrage(chosen_percents, valid_arbitrage),
            parse_mode=ParseMode.HTML,
            reply_markup=menu_kb
        )

        user_data = await state.get_data()
        real_time_state = await state.get_state()
        if real_time_state != 'UserStates:arbitrage_loop' or chosen_percents != user_data.get('chosen_percents', None):
            break
        else:
            await asyncio.sleep(user.arb_auto_update * 60)
        real_time_state = await state.get_state()
        user_data = await state.get_data()


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

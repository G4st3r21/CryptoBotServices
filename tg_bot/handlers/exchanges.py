from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers import menu_message
from keys.exchange import generate_exchange_settings_keyboard
from states import UserStates


async def cmd_exchanges(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    setting_kb = generate_exchange_settings_keyboard(user_data.get('chosen_exchanges', None))

    await callback_query.message.edit_text(
        "Выберите по каким биржам исследовать арбитраж(минимум 2)",
        reply_markup=setting_kb
    )
    await UserStates.choosing_exchange.set()


async def choosing_exchanges(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_data = await state.get_data()

    exchange = callback_query.data
    await UserStates.choosing_percent.set()
    chosen_exchanges: list = user_data.get('chosen_exchanges')
    if exchange != 'back':
        if exchange not in chosen_exchanges:
            chosen_exchanges.append(exchange)
        else:
            chosen_exchanges.remove(exchange)
        await state.update_data(chosen_exchanges=chosen_exchanges)
        await cmd_exchanges(callback_query, state)
    else:
        await menu_message(callback_query, state)


def register_handlers_exchanges(dp: Dispatcher):
    dp.register_callback_query_handler(
        choosing_exchanges, lambda c: c.data != 'menu',
        state=UserStates.choosing_exchange
    )
    dp.register_callback_query_handler(
        cmd_exchanges, lambda c: c.data == 'exchanges_prices',
        state=[UserStates.choosing_exchange, None]
    )

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers import arbitrage_menu_message
from keys.exchange import get_exchange_settings_kb
from states import UserStates


async def cmd_exchanges(callback_query: CallbackQuery, state: FSMContext):
    chosen_exchanges = (await state.get_data()).get('chosen_exchanges', [])
    setting_kb = get_exchange_settings_kb(chosen_exchanges)
    text = "Выберите по каким биржам исследовать арбитраж (минимум 2)"
    await callback_query.message.edit_text(text, reply_markup=setting_kb)
    await UserStates.choosing_exchange.set()


async def choosing_exchanges(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_data = await state.get_data()
    chosen_exchanges = user_data.get('chosen_exchanges', [])
    exchange = callback_query.data
    if exchange == 'back':
        await arbitrage_menu_message(callback_query, state, )
        return
    if exchange not in chosen_exchanges:
        chosen_exchanges.append(exchange)
    else:
        chosen_exchanges.remove(exchange)
    await state.update_data(chosen_exchanges=chosen_exchanges)
    await cmd_exchanges(callback_query, state)


def register_handlers_exchanges(dp: Dispatcher):
    dp.register_callback_query_handler(
        choosing_exchanges, lambda c: c.data != 'menu',
        state=UserStates.choosing_exchange
    )
    dp.register_callback_query_handler(
        cmd_exchanges, lambda c: c.data == 'exchanges_prices',
        state=[UserStates.choosing_exchange, None]
    )

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageNotModified

from handlers import arbitrage_menu_message, get_arbitrage
from keys.percents import get_percents_settings_kb
from states import UserStates


async def cmd_percents(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    chosen_percents = user_data.get('chosen_percents')
    try:
        await callback_query.message.edit_text(
            text="Выбор процентных диапазонов\n"
                 "Выберите в каком процентном диапазоне вывести арбитраж\n",
            reply_markup=get_percents_settings_kb(chosen_percents)
        )
    except MessageNotModified:
        pass
    finally:
        await UserStates.choosing_percent.set()


async def choosing_percents(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    percent = callback_query.data
    if percent != 'back':
        await state.update_data(chosen_percents=percent)
        if await state.get_state() != 'UserStates:arbitrage_loop':
            await cmd_percents(callback_query, state)
        else:
            await get_arbitrage(callback_query, state)
    else:
        await arbitrage_menu_message(callback_query, state, )


def register_handlers_percents(dp: Dispatcher):
    dp.register_callback_query_handler(
        choosing_percents, lambda c: c.data != 'menu',
        state=[UserStates.choosing_percent, UserStates.arbitrage_loop]
    )
    dp.register_callback_query_handler(
        cmd_percents, lambda c: c.data == 'percents',
        state=[UserStates.choosing_percent, None]
    )

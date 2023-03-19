from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db_session import session_db
from handlers import menu_message
from keys.autoupdate import generate_autoupdate_settings_keyboard
from models import Users, ArbAutoUpdates
from states import UserStates


@session_db
async def cmd_autoupdate(callback_query: CallbackQuery, session: AsyncSession):
    user = await Users.get_user_by_tg_id(session, callback_query.from_user.id)
    auto_updates = await ArbAutoUpdates.get_all(session)
    setting_kb = generate_autoupdate_settings_keyboard(auto_updates, user.arb_auto_update)

    await callback_query.message.edit_text(
        "Выберите частоту обновления арбитража",
        reply_markup=setting_kb
    )
    await UserStates.choosing_autoupdate.set()


@session_db
async def choosing_autoupdate(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user = await Users.get_user_by_tg_id(session, callback_query.from_user.id)

    if (autoupdate := int(callback_query.data)) != 'back':
        if user.arb_auto_update != autoupdate:
            await Users.set_autoupdate(session, user, autoupdate)
            await cmd_autoupdate(callback_query)
    else:
        await menu_message(callback_query, state)


def register_handlers_autoupdate(dp: Dispatcher):
    dp.register_callback_query_handler(
        choosing_autoupdate, lambda c: c.data != 'menu',
        state=UserStates.choosing_autoupdate
    )
    dp.register_callback_query_handler(
        cmd_autoupdate, lambda c: c.data == 'autoupdate',
        state=[UserStates.choosing_autoupdate, None]
    )

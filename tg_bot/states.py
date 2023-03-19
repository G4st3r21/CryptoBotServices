from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    choosing_settings = State(state="settings_state")
    choosing_percent = State(state="percents_state")
    choosing_exchange = State(state="exchange_state")
    choosing_autoupdate = State(state="autoupdate_state")
    arbitrage_loop = State(state="arbitrage_loop")

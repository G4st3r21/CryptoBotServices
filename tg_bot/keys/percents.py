from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_percents_settings_keyboard(chosen_percents=None):
    if chosen_percents is None:
        chosen_percents = []

    percents_kb = InlineKeyboardMarkup(row_width=3)
    percents_kb.row(
        InlineKeyboardButton("0.9-3 ✅" if "0.9-3" in chosen_percents else "0.9-3", callback_data="0.9-3"),
        InlineKeyboardButton("3-5 ✅" if "3-5" in chosen_percents else "3-5", callback_data="3-5"),
        InlineKeyboardButton("5-8 ✅" if "5-8" in chosen_percents else "5-8", callback_data="5-8"),
        InlineKeyboardButton("8+ ✅" if "8+" in chosen_percents else "8+", callback_data="8+")
    )
    percents_kb.row(
        InlineKeyboardButton("В меню", callback_data="back"),
    )

    return percents_kb

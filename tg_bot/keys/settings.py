from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_arbitrages_kb():
    setting_kb = InlineKeyboardMarkup(row_width=3)
    setting_kb.row(
        InlineKeyboardButton("DEX", callback_data="DEX"),
        InlineKeyboardButton("CEX", callback_data="CEX"),
        InlineKeyboardButton("P2P", callback_data="P2P")
    )

    return setting_kb


def get_settings_kb(settings_set=False):
    setting_kb = InlineKeyboardMarkup(row_width=2)
    setting_kb.row(
        InlineKeyboardButton("Выбор бирж", callback_data="exchanges_prices"),
        InlineKeyboardButton("Выбор диапазона", callback_data="percents")
    )
    setting_kb.row(
        InlineKeyboardButton("Автообновление", callback_data="autoupdate"),
        InlineKeyboardButton("Управление подпиской", callback_data="subscription")
    )
    if settings_set:
        setting_kb.row(
            InlineKeyboardButton("Поиск арбитража", callback_data="arbitrage"),
        )

    return setting_kb


def get_menu_kb():
    menu_kb = InlineKeyboardMarkup(row_width=1)
    menu_kb.row(
        InlineKeyboardButton("В меню", callback_data="menu"),
    )

    return menu_kb

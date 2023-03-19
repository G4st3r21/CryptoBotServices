from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_exchange_settings_keyboard(chosen_exchanges=None):
    if chosen_exchanges is None:
        chosen_exchanges = []

    exchange_kb = InlineKeyboardMarkup(row_width=3)
    exchange_kb.row(
        InlineKeyboardButton("Binance ✅" if "binance" in chosen_exchanges else "Binance", callback_data="binance"),
        InlineKeyboardButton("Huobi ✅" if "huobi" in chosen_exchanges else "Huobi", callback_data="huobi"),
        InlineKeyboardButton("Kucoin ✅" if "kucoin" in chosen_exchanges else "Kucoin", callback_data="kucoin")
    )
    exchange_kb.row(
        InlineKeyboardButton("В меню", callback_data="back"),
    )

    return exchange_kb

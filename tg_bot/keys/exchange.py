from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_exchange_settings_keyboard(chosen_exchanges=None):
    if chosen_exchanges is None:
        chosen_exchanges = []

    exchange_kb = InlineKeyboardMarkup(row_width=3)

    exchange_kb.row(
        InlineKeyboardButton("Binance ✅" if "binance" in chosen_exchanges else "Binance", callback_data="binance"),
        InlineKeyboardButton("Huobi ✅" if "huobipro" in chosen_exchanges else "Huobi", callback_data="huobipro"),
        InlineKeyboardButton("Kucoin ✅" if "kucoin" in chosen_exchanges else "Kucoin", callback_data="kucoin")
    )
    exchange_kb.row(
        InlineKeyboardButton("Bybit ✅" if "bybit" in chosen_exchanges else "Bybit", callback_data="bybit"),
        InlineKeyboardButton("Gate.io ✅" if "gate" in chosen_exchanges else "Gate.io", callback_data="gate"),
        InlineKeyboardButton("MEXC Global ✅" if "mexc" in chosen_exchanges else "MEXC Global", callback_data="mexc")
    )
    exchange_kb.row(
        InlineKeyboardButton("В меню", callback_data="back"),
    )

    return exchange_kb

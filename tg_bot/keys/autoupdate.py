from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_autoupdate_settings_kb(auto_updates: list, taken_autoupdate):
    auto_updates_kb = InlineKeyboardMarkup(row_width=2)
    for auto_update in auto_updates:
        text = str(auto_update.wait_time) + "м" + " ✅" \
            if auto_update.wait_time == taken_autoupdate else str(auto_update.wait_time) + "м"
        auto_updates_kb.add(InlineKeyboardButton(text, callback_data=auto_update.wait_time))

    auto_updates_kb.row(
        InlineKeyboardButton("Назад", callback_data="back"),
    )

    return auto_updates_kb

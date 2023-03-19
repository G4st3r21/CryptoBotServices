from sqladmin import ModelView

from models import Users, Tariffs, ArbAutoUpdates


class UserView(ModelView, model=Users):
    name = "Пользователь"
    name_plural = "Пользователи"

    column_list = [Users.id, Users.tg_id, Users.username, Users.sub_type]


class TariffView(ModelView, model=Tariffs):
    name = "Тариф"
    name_plural = "Тарифы"

    column_list = [Tariffs.id, Tariffs.name, Tariffs.price]


class UpdateView(ModelView, model=ArbAutoUpdates):
    name = "Автообновление"
    name_plural = "Автообновления"

    column_list = [ArbAutoUpdates.id, ArbAutoUpdates.wait_time]

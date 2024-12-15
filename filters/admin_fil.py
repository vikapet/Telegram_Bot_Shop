from aiogram.filters import Filter
from aiogram import types


# Кастомный фильтр
# Заимствование
class IsAdmin(Filter):
    def __init__(self, admins) -> None:
        self.admins = admins

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.admins

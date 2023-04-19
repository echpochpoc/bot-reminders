from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from core.create_connect import dp


class StateClassFilter(BoundFilter):
    def __init__(self, state_class):
        self.state_class = state_class

    async def check(self, message: types.Message) -> bool:
        state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
        cur_state = await state.get_state()
        if cur_state is None:
            return False
        if self.state_class in cur_state:
            return True

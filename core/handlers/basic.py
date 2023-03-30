from aiogram import types, Dispatcher


async def start_handler(message: types.Message):
    await message.answer('Hi, I can\'t do anything')


async def echo_handler(message: types.Message):
    await message.answer(message.text)


def register_handler_basic(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(echo_handler)

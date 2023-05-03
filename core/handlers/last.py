from aiogram import types, Dispatcher


async def echo_handler(message: types.Message):
    await message.answer('Я тебя не понимаю, используй команды или кнопки. Для помощи нажми на /help')


def register_handler(dp: Dispatcher):
    dp.register_message_handler(echo_handler)

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from core.filters.filters import UserIsRegistered
from core.keyboards.keyboards import get_kb_main_menu

from db.queries import queries
from db import models


async def start_handler(message: types.Message):
    await message.answer('Привет, я бот-напоминалка бета 1.0. Для начала зарегистрируйся. Нажми сюда -> /reg')


async def send_kb_main_menu(message: types.Message):
    """
    Создает клавиатуру главного меню, если она куда-то делась и не вернулась
    """
    kb = get_kb_main_menu()
    await message.answer('Клавиатура создана',
                         reply_markup=kb)


async def send_help(message: types.Message):
    await message.answer('Это бот-напоминалка. Он создает напоминания другим пользователям. '
                         'Команды находятся в Меню (три полосочки в строке набора сообщения) или же их можно '
                         'выбрать в списке ниже (просто кликни):\n\n'
                         '/reg - регистрация (можно перерегистрироваться, напоминания останутся)\n'
                         '/reminder - создать напоминание\n'
                         '/send_users - посмотреть список пользователей и их групп\n'
                         '/send_groups - посмотреть список групп и их пользователей\n'
                         '/keyboard - создать клавиатуру главного меню\n\n'
                         'По всем вопросам и предложениям насчет бота, писать @echpochpoc. \n\n'
                         'Create by Егор Колмогоров🌝')


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Сбрасывает state, из любой точки
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    kb = get_kb_main_menu()
    await message.answer('Операция прервана', reply_markup=kb)
    await state.finish()


async def send_profile(message: types.Message):
    """
    Отправляет профиль пользователя
    """
    user: models.User = await queries.select_user(message.chat.id)
    groups = await queries.select_groups_with_user(message.chat.id)
    text = f'Ваш профиль:\n' \
           f'ID: {user.telegram_id}\n' \
           f'ФИО: {user.fullname}\n' \
           f'Псевдоним: {user.shortname}\n' \
           f'Группы: {", ".join([group.title for group in groups])}'
    if user.photo is not None:
        await message.answer_photo(photo=user.photo, caption=text)
    else:
        await message.answer(text)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(send_help, commands=['help'])
    dp.register_message_handler(send_help, Text(startswith='🆘Помощь'))
    dp.register_message_handler(send_kb_main_menu, commands=['keyboard'])
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
    dp.register_message_handler(send_profile, UserIsRegistered(), Text(startswith='🌝Профиль'))

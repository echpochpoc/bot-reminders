from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='reg',
            description='Регистрация'
        ),
        BotCommand(
            command='reminder',
            description='Создать напоминание'
        ),
        BotCommand(
            command='cancel',
            description='Отмена'
        ),
        BotCommand(
            command='keyboard',
            description='Создать клавиатуру'
        ),
        BotCommand(
            command='send_groups',
            description='Список группы'
        ),
        BotCommand(
            command='send_users',
            description='Список пользователей'
        ),
        BotCommand(
            command='add_group',
            description='Добавить группу'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        ),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

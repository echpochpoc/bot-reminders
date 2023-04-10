from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Старт'
        ),
        BotCommand(
            command='reg',
            description='Регистрации пользователя'
        ),
        BotCommand(
            command='cancel',
            description='Отмена'
        ),
        BotCommand(
            command='test',
            description='Тестирование'
        ),
        BotCommand(
            command='add_group',
            description='Добавить группу'
        ),
        BotCommand(
            command='profile',
            description='Показать профиль'
        ),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

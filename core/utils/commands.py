from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='reg',
            description='Регистрации пользователя'
        ),
        BotCommand(
            command='reminder',
            description='Создать напоминание'
        ),
        BotCommand(
            command='test',
            description='Тестирование'
        ),
        BotCommand(
            command='cancel',
            description='Отмена'
        ),
        BotCommand(
            command='add_group',
            description='Добавить группу'
        ),
        BotCommand(
            command='delete_group',
            description='Удалить группы'
        ),
        BotCommand(
            command='keyboard',
            description='Создать клавиатуру'
        ),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

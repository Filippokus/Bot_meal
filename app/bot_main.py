import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import (
   Bold, as_list, as_marked_section
)

from token_data import TOKEN
from recipes_handler import router

dp = Dispatcher()
dp.include_router(router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик получает сообщения с помощью команды `/start`.
    """
    kb = [
        [
            types.KeyboardButton(text="Команды"),
            types.KeyboardButton(text="Описание бота"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=keyboard)


@dp.message(F.text.lower() == "команды")
async def commands(message: types.Message) -> None:
    """
    Этот обработчик отвечает на сообщение "команды"
    :param message: Объект сообщения, на которое нужно ответить.
    :return: None
    """
    response = as_list(
        as_marked_section(
            Bold("Команды:"),
            "Что бы получить рецепты блюд нужно ввести команду:"
            "/category_search_random [число] - где число это количество блюд",

            marker="✅ ",
        ),
    )

    await message.answer(**response.as_kwargs())


@dp.message(F.text.lower() == "описание бота")
async def description(message: types.Message) -> None:
    await message.answer("Этот бот предоставляет информацию о рецептах "
                         "и ингредиентах по категориям блюд.")


async def main() -> None:
    bot = Bot(TOKEN)
    dp.parse_mode = ParseMode.HTML
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
import aiohttp
import asyncio

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types

from get_cat_and_meals import get_category, get_rnd_meals
from meals_details import get_meals_details
from translator import translate_list_async

router = Router()


class OrderRecipes(StatesGroup):
    waiting_for_category = State()
    waiting_for_recipes = State()
    showing_recipes = State()


@router.message(Command("category_search_random"))
async def cmd_category_search_random(message: Message, command: CommandObject, state: FSMContext) -> None:
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    await state.set_data({"num_recipes": int(command.args)})
    async with aiohttp.ClientSession() as session:
        categories = await get_category(session)
        builder = ReplyKeyboardBuilder()
        for category in categories:
            builder.add(types.KeyboardButton(text=category))
        builder.adjust(5)
        await message.answer('Выберите категорию блюд:', reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.waiting_for_category.state)


@router.message(OrderRecipes.waiting_for_category)
async def collect_recipes(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    num = data.get("num_recipes")
    async with aiohttp.ClientSession() as session:
        meals_info = await get_rnd_meals(session, message.text, num)
    if meals_info:
        meal_ids = [item['idMeal'] for item in meals_info]  # создаем list id блюд
        await state.update_data({'idMeals': meal_ids})  # сохраняем list id в state
        meals = [item['Meal'] for item in meals_info]  # создаем list наименований блюд
        translated_meals = await translate_list_async(meals)  # переводим list наименований блюд
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Покажи рецепты'))
        separator = '\n'
        await message.answer(f"Как вам такие варианты:\n{separator.join(item for item in translated_meals)}",
                             reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.waiting_for_recipes.state)
    else:
        await message.answer("Извините, мы не смогли найти блюда по вашему запросу.")


@router.message(OrderRecipes.waiting_for_recipes)
async def show_recipes(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    meal_ids = data.get("idMeals")
    if not meal_ids:
        await message.answer("Извините, мы не смогли найти блюда по вашему запросу.")
        return
    async with aiohttp.ClientSession() as session:
        tasks = [get_meals_details(session, meal_id) for meal_id in meal_ids]
        meals_details = await asyncio.gather(*tasks)
    for meal in meals_details:
        name = meal['name']
        instructions = meal['instructions']
        ingredients = meal['ingredients']
        response_text = f"{name}\n\nИнструкции:\n{instructions}\n\nИнгредиенты:\n{ingredients}"
        await message.answer(response_text)

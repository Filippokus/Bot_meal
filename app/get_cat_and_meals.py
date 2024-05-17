from random import sample


async def get_category(session) -> list:
    async with session.get(url="https://www.themealdb.com/api/json/v1/1/list.php?c=list") as resp:
        data = await resp.json()
        categories = [meal['strCategory'] for meal in data['meals']]
        return categories


async def get_rnd_meals(session, category: str, num_recipes: int) -> list:
    async with session.get(url=f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}") as resp:
        data = await resp.json()
        if data is None or 'meals' not in data or data['meals'] is None:
            print(f"Ошибка: Получен некорректный ответ API для категории {category}")
            print(f"Ответ: {data}")
            return []

        meals_info = [{'Meal': meal['strMeal'], 'idMeal': meal['idMeal']} for meal in data['meals']]

        if num_recipes > len(meals_info):
            print(f"Запрошено больше рецептов, чем доступно. Возвращаем все {len(meals_info)} рецептов.")
            num_recipes = len(meals_info)

        return sample(meals_info, k=num_recipes)

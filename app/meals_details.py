from translator import translate_list_async


async def get_meals_details(session, meal_id) -> dict:
    url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}'
    async with session.get(url) as response:
        data = await response.json()
        meal = data['meals'][0]
        meal_details = [
            meal['strMeal'],
            meal['strInstructions'],
            get_ingredients_and_measure(meal)
        ]
        translated_meals = await translate_list_async(meal_details)
    return {
        'name': translated_meals[0],
        'instructions': translated_meals[1],
        'ingredients': translated_meals[2]
    }


def get_ingredients_and_measure(meal) -> str:
    ingredients = []
    for i in range(1, 21):
        ingredient = meal[f'strIngredient{i}']
        measure = meal[f'strMeasure{i}']
        if ingredient:
            ingredient_with_measure = f"{ingredient} - {measure}"
            ingredients.append(ingredient_with_measure)
    ingredients_str = "\n".join([f"{idx + 1}. {ingredient}" for idx, ingredient in enumerate(ingredients)])
    return ingredients_str

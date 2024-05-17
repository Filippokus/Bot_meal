import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from easygoogletranslate import EasyGoogleTranslate

# Инициализация переводчика
translator = EasyGoogleTranslate(
    source_language='en',
    target_language='ru',
    timeout=10
)


# Асинхронная функция для перевода текста
async def translate_text(executor, text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, translator.translate, text)


# Асинхронная функция для перевода списка слов
async def translate_list_async(items_list) -> List[str]:
    with ThreadPoolExecutor() as executor:
        tasks = [translate_text(executor, word) for word in items_list]
        return await asyncio.gather(*tasks)

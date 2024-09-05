import asyncio
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
import logging

executor = ThreadPoolExecutor()

def translate_sync(text: str, target_language: str) -> str:
    """
    Synchronized function to translate text.

    :param text: Text to be translated.
    :param target_language: Target language for translation.
    :return: Translated text.
    """
    translator = GoogleTranslator(source="auto", target=target_language)
    translated = translator.translate(text)
    return translated

async def translate_text(text: str, target_language: str = 'uk') -> str:
    """
    Asynchronously translates text using GoogleTranslator.

    :param text: Text to be translated.
    :param target_language: Target language for translation.
    :return: Translated text.
    """
    loop = asyncio.get_running_loop()
    try:
        # Executing a synchronous function in an asynchronous context
        translated = await loop.run_in_executor(executor, translate_sync, text, target_language)
        return translated
    except Exception as e:
        logging.error(f"Error during translation: {str(e)}")
        return "Translation Error"

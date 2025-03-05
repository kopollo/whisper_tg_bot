import logging
import os

import dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Вставьте ваш токен бота здесь
dotenv.load_dotenv('.env')
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WHISPER_SERVER_URL = os.environ.get("WHISPER_SERVER_URL")
# SERVER_URL = 'http://127.0.0.1:8000/transcribe'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import httpx


async def send_audio_to_server(file_path):
    file_path = str(file_path)
    async with httpx.AsyncClient(timeout=60.0) as client:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        files = {'file': (file_path, audio_data, 'audio/mpeg')}
        try:
            response = await client.post(WHISPER_SERVER_URL, files=files)
            response.raise_for_status()
            result = response.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            return {"error": "Failed to process the audio file"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            return {"error": "Failed to process the audio file"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне аудиофайл, и я расшифрую его для вас.')


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio_file = update.message.audio or update.message.voice
    if audio_file:
        file = await context.bot.get_file(audio_file.file_id)
        file_path = await file.download_to_drive()
        await update.message.reply_text('Файл получен, начинаю обработку...')

        result = await send_audio_to_server(file_path)

        if 'error' in result:
            await update.message.reply_text(f"Произошла ошибка: {result['error']}")
        else:
            await update.message.reply_text(f"Результат расшифровки: {result['text']}")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))

    application.run_polling()


if __name__ == '__main__':
    main()

import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InputMediaPhoto

# ====== Переменные окружения ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
THREAD_ID = int(os.getenv("THREAD_ID", 0)) or None

# ====== Инициализация бота ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

# ====== Вопросы с уточнением примера ======
QUESTIONS = [
    "1️⃣ Ваш игровой ник:",
    "2️⃣ Ваш Telegram никнейм (отправьте свой @username):",
    "3️⃣ Пришлите скрин вашего персонажа (пример: БМ и ник видны, вкладка уровня открыта):",
    "4️⃣ Пришлите скрин вашего круга:",
    "5️⃣ В каких гильдиях ранее состояли?",
    "6️⃣ Причина ухода из гильдии?",
    "7️⃣ Почему вы выбрали наш клан?"
]

# ====== Обработчики ======
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в приёмку WinxClub!\nОтветьте, пожалуйста, на несколько вопросов."
    )
    user_data[message.from_user.id] = {"step": 0, "answers": []}
    await message.answer(QUESTIONS[0])

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Введите /start, чтобы начать опрос.")
        return

    data = user_data[user_id]
    step = data["step"]

    # Сохраняем текст или фото
    if message.photo:
        file_id = message.photo[-1].file_id
        data["answers"].append(("photo", file_id))
    else:
        data["answers"].append(("text", message.text))

    data["step"] += 1

    if data["step"] < len(QUESTIONS):
        await message.answer(QUESTIONS[data["step"]])
    else:
        await message.answer("Спасибо за ваш отклик, ожидайте обратную связь от офицеров гильдии.")
        await send_results_to_group(message.from_user, data["answers"])
        del user_data[user_id]

# ====== Функция отправки анкеты ======
async def send_results_to_group(user, answers):
    # Текст анкеты для подписи первого фото
    caption_text = (
        f"📥 Анкета от {user.full_name} (@{user.username})\n\n"
        f"1. Игровой ник: {answers[0][1] if answers[0][0]=='text' else '[скрин прислан]'}\n"
        f"2. Telegram: {answers[1][1] if answers[1][0]=='text' else '[скрин прислан]'}\n"
        f"3. В каких гильдиях ранее: {answers[4][1] if len(answers)>4 and answers[4][0]=='text' else '[нет данных]'}\n"
        f"4. Причина ухода: {answers[5][1] if len(answers)>5 and answers[5][0]=='text' else '[нет данных]'}\n"
        f"5. Почему выбрали наш клан: {answers[6][1] if len(answers)>6 and answers[6][0]=='text' else '[нет данных]'}"
    )

    media = []

    # Первый скрин с подписью
    if len(answers) > 2 and answers[2][0] == "photo":
        media.append(InputMediaPhoto(media=answers[2][1], caption=caption_text))

    # Второй скрин без подписи
    if len(answers) > 3 and answers[3][0] == "photo":
        media.append(InputMediaPhoto(media=answers[3][1]))

    # Отправляем все фото и текст одним постом
    if media:
        await bot.send_media_group(chat_id=GROUP_CHAT_ID, media=media, message_thread_id=THREAD_ID)
    else:
        # Если фото нет, просто текст
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=caption_text, message_thread_id=THREAD_ID)

# ====== Запуск бота ======
asyncio.run(dp.start_polling(bot))

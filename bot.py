import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
THREAD_ID = int(os.getenv("THREAD_ID", 0)) or None

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

QUESTIONS = [
    "1️⃣ Ваш игровой ник:",
    "2️⃣ Ваш Telegram никнейм (отправьте свой @username):",
    "3️⃣ Пришлите скрин вашего персонажа (пример: лицо и ник видны):",
    "4️⃣ Пришлите скрин вашего круга:",
    "5️⃣ В каких гильдиях ранее состояли?",
    "6️⃣ Причина ухода из гильдии?",
    "7️⃣ Почему вы выбрали наш клан?"
]

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

async def send_results_to_group(user, answers):
    text_parts = [
        f"📥 **Новая анкета от {user.full_name} (@{user.username})**",
        "",
        f"1. Игровой ник: {answers[0][1] if answers[0][0]=='text' else '[скрин прислан]'}",
        f"2. Telegram: {answers[1][1] if answers[1][0]=='text' else '[скрин прислан]'}",
        f"5. Гильдии ранее: {answers[4][1] if len(answers)>4 and answers[4][0]=='text' else '[нет данных]'}",
        f"6. Причина ухода: {answers[5][1] if len(answers)>5 and answers[5][0]=='text' else '[нет данных]'}",
        f"7. Почему выбрали нас: {answers[6][1] if len(answers)>6 and answers[6][0]=='text' else '[нет данных]'}",
    ]
    text_message = "\n".join(text_parts)

    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=text_message,
        message_thread_id=THREAD_ID,
        parse_mode="Markdown"
    )

    captions = ["Скрин персонажа", "Скрин круга"]

for idx, i in enumerate([2, 3]):  # ответы с фото — 3-й и 4-й вопрос
    if len(answers) > i and answers[i][0] == "photo":
        await bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=answers[i][1],
            caption=captions[idx],
            message_thread_id=THREAD_ID
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

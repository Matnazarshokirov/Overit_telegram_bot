import os
import random
import json
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv

# .env faylni o‘qish (agar fayl nomi api.env bo‘lsa, shu faylni ko‘rsatamiz)
load_dotenv(dotenv_path="api.env")

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN .env faylidan o'qilmadi!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users_file = "data/users.json"

# Foydalanuvchilar ma'lumotini yuklash
if os.path.exists(users_file):
    with open(users_file, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"level": 0, "falls": 0}
        save_users()
    await message.answer("🧗‍♂️ O‘yin boshlandi! /sakra buyrug‘ini bosib harakat qil!")

@dp.message_handler(commands=['sakra'])
async def jump(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"level": 0, "falls": 0}
    move = random.choice(["up", "fall", "stay"])
    if move == "up":
        users[uid]["level"] += 1
        txt = "🔼 Yuqoriga chiqdingiz!"
        img = "data/images/up.jpg"
    elif move == "fall":
        users[uid]["level"] = max(0, users[uid]["level"] - random.randint(1, 3))
        users[uid]["falls"] += 1
        txt = "💥 Sirpandingiz!"
        img = "data/images/fall.jpg"
    else:
        txt = "😐 Joyida qoldingiz..."
        img = "data/images/stay.jpg"
    save_users()
    try:
        with open(img, "rb") as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"{txt} Pog‘ona: {users[uid]['level']}")
    except FileNotFoundError:
        await message.answer(f"{txt} Pog‘ona: {users[uid]['level']} (rasm topilmadi)")

@dp.message_handler(commands=['profil'])
async def profile(message: types.Message):
    uid = str(message.from_user.id)
    user = users.get(uid, {"level": 0, "falls": 0})
    await message.answer(f"👤 Sizning statistikangiz:\nPog‘ona: {user['level']}\nYiqilishlar: {user['falls']}")

@dp.message_handler(commands=['top'])
async def top_players(message: types.Message):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["level"], reverse=True)[:5]
    text = "🏆 Eng yuqori pog‘onadagi o‘yinchilar:\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. ID: {uid} – Pog‘ona: {data['level']}\n"
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

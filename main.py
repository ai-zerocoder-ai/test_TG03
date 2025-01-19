import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import logging
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка токена из .env файла
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Вызов функции для создания базы данных
init_db()

# Определение состояний для FSM
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Обработка команды /start
@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

# Обработка ввода имени
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

# Обработка ввода возраста
@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("В каком классе ты учишься?")
    await state.set_state(Form.grade)

# Обработка ввода класса
@dp.message(Form.grade)
async def process_grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    age = user_data['age']
    grade = message.text

    # Сохранение данных в базу данных
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)', (name, age, grade))
    conn.commit()
    conn.close()

    await message.answer(f"Спасибо! Мы сохранили твои данные:\nИмя: {name}\nВозраст: {age}\nКласс: {grade}")
    await state.clear()

# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

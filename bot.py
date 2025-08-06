import os
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

TARIFFS = {
    "Домашній інтернет - варіант №1\n(3 місяці безкоштовно, потім 250 грн/міс.)":
        "Домашній інтернет (3 місяці безкоштовно)",

    "Домашній інтернет - варіант №2\n(6 місяців по 125 грн, потім 250 грн/міс.)":
        "Домашній інтернет (6 місяців по 125 грн)",

    "Домашній інтернет +TV Start\n(3 місяці безкоштовно, потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (3 місяці безкоштовно, потім 300 грн/міс.)",
    
    "Домашній інтернет +TV Pro\n(3 місяці безкоштовно, потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (3 місяці безкоштовно, потім 325 грн/міс.)",

    "Домашній інтернет +TV Max\n(3 місяці безкоштовно, потім 375 грн/міс.)":
        "Домашній інтернет +TV Max (3 місяці безкоштовно, потім 375 грн/міс.)"
}

# 🔎 Проверка ФІО
def is_valid_full_name(text):
    return bool(re.match(r"^[А-ЯІЇЄҐ][а-яіїєґ']+\s[А-ЯІЇЄҐ][а-яіїєґ']+\s[А-ЯІЇЄҐ][а-яіїєґ']+$", text.strip()))

# 🔎 Проверка телефона
def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")

    await bot.send_photo(
        message.chat.id,
        "https://www.vodafone.ua/storage/editor/fotos/7f387e69a10a3da04355e7cf885e59c5_1741849417.jpg"
    )

    await message.answer(
        "👋 *Вітаємо у Vodafone 🇺🇦*\n\n"
        "👻 *Я Ваш бот Тарас*\n"
        "💪  *Переваги домашнього інтернету від Vodafone це...*\n"
        "✅ *Нова та якісна мережа!*\n"
        "✅ *Cучасна технологія GPON!*\n"
        "✅ *Швидкість 1Гігабіт/сек.!*\n"
        "✅ *Безкоштовне та швидке підключення!*\n"
        "✅ *Понад 72 години працює без світла!*\n"
        "✅ *Акційні тарифи!*\n\n"
        "👉 *Домашній інтернет  - варіант №1*\n"
        "*3 місяці безкоштовно*, далі 250 грн/міс.\n\n"
        "👉 *Домашній інтернет - варіант №2*\n"
        "*6 місяців по 125 грн/міс.*, далі 250 грн/міс.\n\n"
        "👉 *Домашній інтернет + TV Start *\n"
        "*3 місяці безкоштовно*, далі 300 грн/міс.\n\n"
        "👉 *Домашній інтернет + TV Pro*\n"
        "*3 місяці безкоштовно*, далі 325 грн/міс.\n\n"
        "👉 *Домашній інтернет + TV Max*\n"
        "*3 місяці безкоштовно*, далі 375 грн/міс.\n\n"
        "Натисніть «Залишити заявку», щоб почати.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.message_handler(lambda message: message.text == "Залишити заявку")
async def get_name(message: types.Message):
    user_data[message.chat.id] = {}
    await message.answer("Введіть повністю ваше прізвище, ім'я та по батькові\n(наприклад: Тарасов Тарас Тарасович):")

@dp.message_handler(lambda_

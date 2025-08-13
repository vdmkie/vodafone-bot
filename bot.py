import os
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

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")

    # 🔽 Картинка по ссылке
    await bot.send_photo(
        message.chat.id,
        "https://www.vodafone.ua/storage/editor/fotos/7f387e69a10a3da04355e7cf885e59c5_1741849417.jpg"  # замените на нужную ссылку
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

@dp.message_handler(commands=['id'])
async def send_chat_id(message: types.Message):
    await message.answer(f"Ваш CHAT_ID: `{message.chat.id}`", parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "Залишити заявку")
async def get_name(message: types.Message):
    user_data[message.chat.id] = {}
    await message.answer("Введіть повністю ваше прізвище, ім'я та по батькові\n"
                         "(наприклад: Тарасов Тарас Тарасович):")

@dp.message_handler(lambda message: message.chat.id in user_data and 'name' not in user_data[message.chat.id])
async def get_address(message: types.Message):
    user_data[message.chat.id]['name'] = message.text
    await message.answer("Введіть повністю вашу адресу для підключення\n"
                         "(місто, вулиця, будинок, квартира):")

@dp.message_handler(lambda message: message.chat.id in user_data and 'address' not in user_data[message.chat.id])
async def get_phone(message: types.Message):
    user_data[message.chat.id]['address'] = message.text
    await message.answer("Введіть повністю ваш номер телефону\n"
                         "(починаючи з 380_____________):")

@dp.message_handler(lambda message: message.chat.id in user_data and 'phone' not in user_data[message.chat.id])
async def choose_tariff(message: types.Message):
    user_data[message.chat.id]['phone'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for tariff_name in TARIFFS:
        markup.add(tariff_name)
    await message.answer("Оберіть тариф:", reply_markup=markup)

@dp.message_handler(lambda message: message.chat.id in user_data and 'tariff' not in user_data[message.chat.id])
async def finish(message: types.Message):
    if message.text not in TARIFFS:
        await message.answer("Будь ласка, оберіть тариф зі списку.")
        return

    user_data[message.chat.id]['tariff'] = message.text
    data = user_data[message.chat.id]

    text = (
        "📩 Нова заявка на підключення інтернету:\n\n"
        f"👤 ПІБ: {data['name']}\n"
        f"🏠 Адреса: {data['address']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📦 Обраний тариф: {TARIFFS[data['tariff']]}"
    )

    await bot.send_message(CHAT_ID, text)

    await message.answer(
        "✅ Дякуємо! Ваша заявка надіслана. Ми зв'яжемося з вами найближчим часом.",
        reply_markup=types.ReplyKeyboardRemove()
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")
    await message.answer("Якщо бажаєте залишити ще одну заявку — натисніть кнопку нижче.", reply_markup=markup)

    del user_data[message.chat.id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
import os
import logging
import re
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

# --- Валидация полей ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+$", name.strip()))

def is_valid_address(address):
    return bool(re.search(r"[а-яА-ЯіїІЇЄєҐґ]+\s.+\d+", address.strip()))

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Старт ---
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

# --- Запуск заявки ---
@dp.message_handler(lambda message: message.text == "Залишити заявку")
async def get_name(message: types.Message):
    user_data[message.chat.id] = {}
    await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")

# --- Ввод ПІБ ---
@dp.message_handler(lambda message: message.chat.id in user_data and not user_data[message.chat.id])
async def handle_name(message: types.Message):
    if not is_valid_name(message.text):
        await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        return
    user_data[message.chat.id]['name'] = message.text.strip()
    await message.answer("✅ Прийнято.\n\nВведіть адресу підключення (місто, вулиця, будинок, квартира):")

# --- Ввод адреси ---
@dp.message_handler(lambda message: message.chat.id in user_data and 'name' in user_data[message.chat.id] and 'address' not in user_data[message.chat.id])
async def handle_address(message: types.Message):
    if not is_valid_address(message.text):
        await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        return
    user_data[message.chat.id]['address'] = message.text.strip()
    await message.answer("✅ Прийнято.\n\nВведіть номер телефону (починаючи з 380...):")

# --- Ввод телефону ---
@dp.message_handler(lambda message: message.chat.id in user_data and 'address' in user_data[message.chat.id] and 'phone' not in user_data[message.chat.id])
async def handle_phone(message: types.Message):
    if not is_valid_phone(message.text):
        await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        return
    user_data[message.chat.id]['phone'] = message.text.strip()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for tariff in TARIFFS:
        markup.add(tariff)
    await message.answer("Оберіть тариф:", reply_markup=markup)

# --- Вибір тарифу ---
@dp.message_handler(lambda message: message.chat.id in user_data and 'phone' in user_data[message.chat.id] and 'tariff' not in user_data[message.chat.id])
async def handle_tariff(message: types.Message):
    if message.text not in TARIFFS:
        await message.answer("❗ Оберіть тариф зі списку.")
        return

    user_data[message.chat.id]['tariff'] = message.text.strip()
    data = user_data[message.chat.id]

    text = (
        "📩 Заявка від Рогальов Вадим:\n\n"
        f"👤 ПІБ: {data['name']}\n"
        f"🏠 Адреса: {data['address']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📦 Тариф: {TARIFFS[data['tariff']]}"
    )
    await bot.send_message(CHAT_ID, text)

    # Кнопки после отправки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити", "Замовити зворотній зв'язок")

    await message.answer("✅ Заявку надіслано. Оберіть подальшу дію:", reply_markup=markup)

# --- Завершення: очищення ---
@dp.message_handler(lambda message: message.text == "Завершити")
async def done(message: types.Message):
    if message.chat.id in user_data:
        del user_data[message.chat.id]
    await message.answer("🧹 Готово. Гарного дня! Наш менеджер вже працює над заявкою 👋", reply_markup=types.ReplyKeyboardRemove())

# --- Зворотній зв'язок ---
@dp.message_handler(lambda message: message.text == "Замовити зворотній зв'язок")
async def callback_request(message: types.Message):
    data = user_data.get(message.chat.id)
    if not data:
        await message.answer("❗ Дані відсутні. Почніть знову /start.")
        return

    text = (
        "📞 Клієнт просить зворотній зв'язок:\n\n"
        f"👤 ПІБ: {data['name']}\n"
        f"📞 Телефон: {data['phone']}"
    )

    await bot.send_message(CHAT_ID, text)
    await message.answer("🔔 Запит на зворотній зв'язок надіслано!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

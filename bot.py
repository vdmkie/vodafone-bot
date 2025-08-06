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

def is_valid_name(name):
    return bool(re.match(r"^[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+$", name.strip()))

def is_valid_address(address):
    return bool(re.search(r"[а-яА-ЯіїІЇЄєҐґ]+\s.+\d+", address.strip()))

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

async def save_msg_id(message, reply):
    user_data.setdefault(message.chat.id, {}).setdefault("messages", []).append(reply.message_id)

async def clear_history(chat_id):
    messages = user_data.get(chat_id, {}).get("messages", [])
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_data[message.chat.id] = {"messages": []}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")

    photo = await bot.send_photo(
        message.chat.id,
        "https://www.vodafone.ua/storage/editor/fotos/7f387e69a10a3da04355e7cf885e59c5_1741849417.jpg"
    )
    user_data[message.chat.id]["messages"].append(photo.message_id)

    msg = await message.answer(
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
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.text == "Залишити заявку")
async def get_name(message: types.Message):
    user_data[message.chat.id] = {"messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.chat.id in user_data and not user_data[message.chat.id].get("name"))
async def handle_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        await save_msg_id(message, msg)
        return
    user_data[message.chat.id]['name'] = message.text.strip()
    msg = await message.answer("✅ Прийнято.\n\nВведіть адресу підключення (місто, вулиця, будинок, квартира):")
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.chat.id in user_data and 'name' in user_data[message.chat.id] and 'address' not in user_data[message.chat.id])
async def handle_address(message: types.Message):
    if not is_valid_address(message.text):
        msg = await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        await save_msg_id(message, msg)
        return
    user_data[message.chat.id]['address'] = message.text.strip()
    msg = await message.answer("✅ Прийнято.\n\nВведіть номер телефону (починаючи з 380...):")
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.chat.id in user_data and 'address' in user_data[message.chat.id] and 'phone' not in user_data[message.chat.id])
async def handle_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        await save_msg_id(message, msg)
        return
    user_data[message.chat.id]['phone'] = message.text.strip()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for tariff in TARIFFS:
        markup.add(tariff)
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.chat.id in user_data and 'phone' in user_data[message.chat.id] and 'tariff' not in user_data[message.chat.id])
async def handle_tariff(message: types.Message):
    if message.text not in TARIFFS:
        msg = await message.answer("❗ Оберіть тариф зі списку.")
        await save_msg_id(message, msg)
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

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити", "Замовити зворотній зв'язок")
    msg = await message.answer("✅ Заявку надіслано. Оберіть подальшу дію:", reply_markup=markup)
    await save_msg_id(message, msg)

@dp.message_handler(lambda message: message.text == "Завершити")
async def done(message: types.Message):
    await clear_history(message.chat.id)
    user_data.pop(message.chat.id, None)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")
    msg = await message.answer("🧹 Готово. Почнімо з початку 👇", reply_markup=markup)
    user_data.setdefault(message.chat.id, {}).setdefault("messages", []).append(msg.message_id)

@dp.message_handler(lambda message: message.text == "Замовити зворотній зв'язок")
async def callback_request(message: types.Message):
    data = user_data.get(message.chat.id)
    if not data:
        msg = await message.answer("❗ Дані відсутні. Почніть знову /start.")
        await save_msg_id(message, msg)
        return

    text = (
        "📞 Клієнт просить зворотній зв'язок:\n\n"
        f"👤 ПІБ: {data['name']}\n"
        f"📞 Телефон: {data['phone']}"
    )
    await bot.send_message(CHAT_ID, text)

    await clear_history(message.chat.id)
    user_data.pop(message.chat.id, None)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку")
    msg = await message.answer("🔔 Запит на зворотній зв'язок надіслано! Почнімо спочатку 👇", reply_markup=markup)
    user_data.setdefault(message.chat.id, {}).setdefault("messages", []).append(msg.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

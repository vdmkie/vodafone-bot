import os
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    user_data[message.chat.id] = {"messages": [], "step": None}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку", "Замовити консультацію")
    markup.add("Перевірити покриття")

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
        "Оберіть дію з меню нижче 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Початок заявки ---
@dp.message_handler(lambda message: message.text == "Залишити заявку")
async def request_name(message: types.Message):
    user_data[message.chat.id] = {"step": "waiting_for_name", "messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Обробка ПІБ ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "waiting_for_name")
async def handle_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["name"] = message.text.strip()
    user_data[message.chat.id]["step"] = "waiting_for_address"
    msg = await message.answer("✅ Прийнято. Введіть адресу підключення (місто, вулиця, будинок, квартира):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Обробка адреси ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "waiting_for_address")
async def handle_address(message: types.Message):
    if not is_valid_address(message.text):
        msg = await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["address"] = message.text.strip()
    user_data[message.chat.id]["step"] = "waiting_for_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Обробка телефону ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "waiting_for_phone")
async def handle_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["phone"] = message.text.strip()
    user_data[message.chat.id]["step"] = "waiting_for_tariff"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for tariff in TARIFFS:
        markup.add(tariff)
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Обробка тарифу ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "waiting_for_tariff")
async def handle_tariff(message: types.Message):
    if message.text not in TARIFFS:
        msg = await message.answer("❗ Оберіть тариф зі списку.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return

    user_data[message.chat.id]["tariff"] = message.text
    text = (
        "📩 Автор заявки Рогальов Вадим:\n\n"
        f"👤 ПІБ: {user_data[message.chat.id]['name']}\n"
        f"🏠 Адреса: {user_data[message.chat.id]['address']}\n"
        f"📞 Телефон: {user_data[message.chat.id]['phone']}\n"
        f"📦 Тариф: {TARIFFS[message.text]}"
    )
    await bot.send_message(CHAT_ID, text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити", "Замовити зворотній зв'язок")

    msg = await message.answer("✅ Заявку надіслано. Оберіть дію:", reply_markup=markup)
    user_data[message.chat.id]["messages"].append(msg.message_id)
    user_data[message.chat.id]["step"] = "completed"

# --- Замовити консультацію ---
@dp.message_handler(lambda message: message.text == "Замовити консультацію")
async def request_consult_name(message: types.Message):
    user_data[message.chat.id] = {"step": "consult_name", "messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consult_name")
async def handle_consult_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["name"] = message.text.strip()
    user_data[message.chat.id]["step"] = "consult_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consult_phone")
async def handle_consult_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return

    user_data[message.chat.id]["phone"] = message.text.strip()

    text = (
        "📞 Запит на консультацію:\n\n"
        f"👤 ПІБ: {user_data[message.chat.id]['name']}\n"
        f"📞 Телефон: {user_data[message.chat.id]['phone']}"
    )
    await bot.send_message(CHAT_ID, text)

    await message.answer("✅ Ваш запит на консультацію надіслано! Ми зателефонуємо найближчим часом.")
    await reset_user_state(message)

# --- Перевірити покриття ---
@dp.message_handler(lambda message: message.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Відкрити карту покриття 🌐",
            url="https://vodafone.ua/uk/internet-home/coverage"
        )
    )
    await message.answer("🔍 Натисніть кнопку нижче, щоб перевірити покриття:", reply_markup=markup)

# --- Завершення та очищення ---
async def reset_user_state(message: types.Message, show_start=True):
    for msg_id in user_data.get(message.chat.id, {}).get("messages", []):
        try:
            await bot.delete_message(message.chat.id, msg_id)
        except:
            pass
    user_data[message.chat.id] = {}

    if show_start:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Залишити заявку", "Замовити консультацію")
        markup.add("Перевірити покриття")
        await message.answer("👋 Повертаємося до початку. Оберіть дію:", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "Завершити")
async def handle_finish(message: types.Message):
    await reset_user_state(message)

@dp.message_handler(lambda message: message.text == "Замовити зворотній зв'язок")
async def handle_callback(message: types.Message):
    data = user_data.get(message.chat.id, {})
    if not all(k in data for k in ("name", "phone")):
        await message.answer("❗ Дані відсутні. Почніть знову /start.")
        return

    text = (
        "📞 Клієнт просить зворотній зв'язок:\n\n"
        f"👤 ПІБ: {data['name']}\n"
        f"📞 Телефон: {data['phone']}"
    )
    await bot.send_message(CHAT_ID, text)
    await reset_user_state(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

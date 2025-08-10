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
    "Домашній інтернет -125грн/міс.\n(акція до 01.01.2026р., потім 250 грн/міс.)":
        "Домашній інтернет (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акція до 01.01.2026р., потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акція до 01.01.2026р., потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Max - 125гн/міс.\n(акція до 01.01.2026р., потім 375 грн/міс.)":
        "Домашній інтернет +TV Max (125грн/міс. до 26 року)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.\n(6 місяців безкоштовно, потім 250 грн/міс.)":
        "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start - 0грн/6міс.\n(6 місяців безкоштовно, потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro - 0грн/6міс.\n(6 місяців безкоштовно, потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max - 0грн/6міс.\n(6 місяців безкоштовно, потім 375 грн/міс.)":
        "Домашній інтернет +TV Max (0грн/6міс)"
}

# --- Валидация ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+$", name.strip()))

def is_valid_address(address):
    return bool(re.search(r"[а-яА-ЯіїІЇЄєҐґ]+\s.+\d+", address.strip()))

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Помощник для добавления ID сообщений ---
def add_message(chat_id, message_id):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    if "messages" not in user_data[chat_id]:
        user_data[chat_id]["messages"] = []
    user_data[chat_id]["messages"].append(message_id)

# --- Старт ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку", "Замовити консультацію")
    markup.add("Перевірити покриття")
    markup.add("Промо-код")  # Добавлена новая кнопка

    photo = await bot.send_photo(
        chat_id,
        "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%B0%D0%BA%D1%86%D0%B8%D1%8F.png?raw=true"
    )
    add_message(chat_id, photo.message_id)

    msg = await message.answer(
        "👋 *Вітаємо у Vodafone 🇺🇦*\n\n"
        "💪  *Наші переваги це...*\n"
        "✅ *Нова та якісна мережа!*\n"
        "✅ *Cучасна технологія GPON!*\n"
        "✅ *Швидкість до 1Гігабіт/сек.!*\n"
        "✅ *Безкоштовне підключення!*\n"
        "✅ *Понад 72 години працює без світла!*\n"
        "✅ *Акційні тарифи!*\n\n" 
        "👉 *Домашній інтернет - 125грн/міс.*\n*акційна абонплата до 01.01.2026, далі 250 грн/міс.*\n\n" 
        "👉 *Домашній інтернет + TV Start - 125грн/міс.*\n*акційна абонплата  до 01.01.2026, далі 300 грн/міс.*\n\n" 
        "👉 *Домашній інтернет + TV Pro - 125грн/міс.*\n*акційна абонплата  до 01.01.2026, далі 325 грн/міс.*\n\n" 
        "👉 *Домашній інтернет + TV Max - 125грн/міс.*\n*акційна абонплата  до 01.01.2026, далі 375 грн/міс.*\n\n"
        "Оберіть дію з меню нижче 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    add_message(chat_id, msg.message_id)
    add_message(chat_id, message.message_id)  # Добавляем сообщение пользователя

# --- Обработка промо-кода ---
@dp.message_handler(lambda m: m.text == "Промо-код")
async def promo_request(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": "waiting_for_promo", "messages": []}
    add_message(chat_id, message.message_id)

    msg = await message.answer("Введіть промо-код:")
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if message.text.strip().lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
        add_message(chat_id, msg.message_id)
    else:
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити' для виходу.")
        add_message(chat_id, msg.message_id)

# --- Заявка ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_name")
async def handle_name(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["name"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_address"
    msg = await message.answer("✅ Прийнято. Введіть адресу підключення (місто, вулиця, будинок, квартира):")
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_address")
async def handle_address(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if not is_valid_address(message.text):
        msg = await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["address"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_phone")
async def handle_phone(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["phone"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_tariff"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Выбор тарифов зависит от промо
    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    for tariff in tariffs:
        markup.add(tariff)
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def handle_tariff(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    if message.text not in tariffs:
        msg = await message.answer("❗ Оберіть тариф зі списку.")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["tariff"] = message.text
    text = (
        "📩 Автор заявки Рогальов Вадим:\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"🏠 Адреса: {user_data[chat_id]['address']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}\n"
        f"📦 Тариф: {tariffs[message.text]}"
    )
    await bot.send_message(CHAT_ID, text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити")

    msg = await message.answer("✅ Заявку надіслано. Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)
    add_message(chat_id, msg.message_id)
    user_data[chat_id]["step"] = "completed"

# --- Консультація ---
@dp.message_handler(lambda m: m.text == "Замовити консультацію")
async def request_consult_name(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": "consult_name", "messages": []}
    add_message(chat_id, message.message_id)

    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def handle_consult_name(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["name"] = message.text.strip()
    user_data[chat_id]["step"] = "consult_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
async def handle_consult_phone(message: types.Message):
    chat_id = message.chat.id
    add_message_

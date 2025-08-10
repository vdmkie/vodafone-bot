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
    "Домашній інтернет -125грн/міс.\n(акційна абонплата до 01.01.2026р., потім 250 грн/міс.)":
        "Домашній інтернет (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акційна абонплата до 01.01.2026р., потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акційна абонплата до 01.01.2026р., потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (125грн/міс. до 26 року)",
    "Домашній інтернет +TV Max - 125гн/міс.\n(акційна абонплата до 01.01.2026р.)":
        "Домашній інтернет +TV Max (125грн/міс. до 26 року)"
}

# --- Валидация ---
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
        "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%94%D0%BE%D0%B1%D0%B0%D0%B2%D0%B8%D1%82%D1%8C%20%D0%9F%D0%BE%D0%B4%D0%B7%D0%B0%D0%B3%D0%BE%D0%BB%D0%BE_20250810_151721_0000.png?raw=true"
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
        "👉 *Домашній інтернет - 125грн/міс.*\n" "*акійна абонплата до 01.01.2026, далі 250 грн/міс.\n\n" 
        "👉 *Домашній інтернет + TV Start - 125грн/міс.*\n" "*акійна абонплата  до 01.01.2026, далі 300 грн/міс.*\n\n" 
        "👉 *Домашній інтернет + TV Pro - 125грн/міс.*\n" "*акійна абонплата  до 01.01.2026, далі 325 грн/міс.*\n\n" 
        "👉 *Домашній інтернет + TV Max - 125грн/міс.*\n" "*акійна абонплата  до 01.01.2026*, далі 375 грн/міс.*\n\n"

        "Оберіть дію з меню нижче 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    user_data[message.chat.id]["messages"].append(msg.message_id)

# --- Заявка ---
@dp.message_handler(lambda m: m.text == "Залишити заявку")
async def request_name(message: types.Message):
    user_data[message.chat.id] = {"step": "waiting_for_name", "messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_name")
async def handle_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["name"] = message.text.strip()
    user_data[message.chat.id]["step"] = "waiting_for_address"
    msg = await message.answer("✅ Прийнято. Введіть адресу підключення (місто, вулиця, будинок, квартира):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_address")
async def handle_address(message: types.Message):
    if not is_valid_address(message.text):
        msg = await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["address"] = message.text.strip()
    user_data[message.chat.id]["step"] = "waiting_for_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_phone")
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

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
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
    markup.add("Завершити")

    msg = await message.answer("✅ Заявку надіслано. Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)
    user_data[message.chat.id]["messages"].append(msg.message_id)
    user_data[message.chat.id]["step"] = "completed"

# --- Консультація ---
@dp.message_handler(lambda m: m.text == "Замовити консультацію")
async def request_consult_name(message: types.Message):
    user_data[message.chat.id] = {"step": "consult_name", "messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def handle_consult_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["name"] = message.text.strip()
    user_data[message.chat.id]["step"] = "consult_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    user_data[message.chat.id]["messages"].append(msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
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

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити")
    await message.answer("✅ Ваш запит на консультацію надіслано! Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)

# --- Перевірити покриття ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    markup_url = InlineKeyboardMarkup()
    markup_url.add(
        InlineKeyboardButton(
            text="Відкрити карту покриття 🌐",
            url="https://vodafone.ua/uk/internet-home/coverage"
        )
    )
    markup_finish = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_finish.add("Завершити")

    msg = await message.answer("🔍 Натисніть кнопку нижче, щоб перевірити покриття:", reply_markup=markup_url)
    user_data[message.chat.id] = {"messages": [msg.message_id], "step": None}

    await message.answer("Коли закінчите — натисніть 'Завершити'", reply_markup=markup_finish)

# --- Завершити ---
async def reset_user_state(message: types.Message):
    for msg_id in user_data.get(message.chat.id, {}).get("messages", []):
        try:
            await bot.delete_message(message.chat.id, msg_id)
        except:
            pass
    user_data[message.chat.id] = {}

    # Повертаємо стартове меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку", "Замовити консультацію")
    markup.add("Перевірити покриття")
    await message.answer("👋 Повертаємося до початку. Оберіть дію:", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "Завершити")
async def handle_finish(message: types.Message):
    await reset_user_state(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

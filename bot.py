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

# --- Заявка ---
@dp.message_handler(lambda m: m.text == "Залишити заявку")
async def request_name(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": "waiting_for_name", "messages": []}
    add_message(chat_id, message.message_id)

    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    add_message(chat_id, msg.message_id)

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
    for tariff in TARIFFS:
        markup.add(tariff)
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    add_message(chat_id, msg.message_id)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def handle_tariff(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    if message.text not in TARIFFS:
        msg = await message.answer("❗ Оберіть тариф зі списку.")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["tariff"] = message.text
    text = (
        "📩 Автор заявки Рогальов Вадим:\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"🏠 Адреса: {user_data[chat_id]['address']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}\n"
        f"📦 Тариф: {TARIFFS[message.text]}"
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
    add_message(chat_id, message.message_id)

    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        add_message(chat_id, msg.message_id)
        return

    user_data[chat_id]["phone"] = message.text.strip()

    text = (
        "📞 Запит на консультацію:\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}"
    )
    await bot.send_message(CHAT_ID, text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити")
    msg = await message.answer("✅ Ваш запит на консультацію надіслано! Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)
    add_message(chat_id, msg.message_id)
    user_data[chat_id]["step"] = "completed"

# --- Перевірити покриття ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    chat_id = message.chat.id
    add_message(chat_id, message.message_id)

    markup_url = types.InlineKeyboardMarkup()
    markup_url.add(
        types.InlineKeyboardButton(
            text="Відкрити карту покриття 🌐",
            url="https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257289%2C30.529932392320312&z=11"
        )
    )
    markup_finish = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_finish.add("Завершити")

    msg = await message.answer("🔍 Натисніть кнопку нижче, щоб перевірити покриття:", reply_markup=markup_url)
    add_message(chat_id, msg.message_id)

    await message.answer("Коли закінчите — натисніть 'Завершити'", reply_markup=markup_finish)

# --- Завершити ---
async def reset_user_state(message: types.Message):
    chat_id = message.chat.id

    # Удаляем все сообщения, сохранённые для данного пользователя
    for msg_id in user_data.get(chat_id, {}).get("messages", []):
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass

    # Удаляем сообщение пользователя (команду "Завершити") отдельно на всякий случай
    try:
        await bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass

    user_data[chat_id] = {}

    # Отправляем кнопку "Старт"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Старт")
    await message.answer("👋 Повертаємося до початку. Натисніть 'Старт' для початку.", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "Завершити")
async def handle_finish(message: types.Message):
    add_message(message.chat.id, message.message_id)
    await reset_user_state(message)

@dp.message_handler(lambda m: m.text == "Старт")
async def handle_start_button(message: types.Message):
    add_message(message.chat.id, message.message_id)
    await start(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

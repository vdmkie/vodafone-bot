import os
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")  # Токен бота
CHAT_ID = int(os.getenv("CHAT_ID"))  # ID адміністратора для заявок

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Збереження стану користувачів
user_data = {}

# Тарифи
TARIFFS = {
    "Домашній інтернет -125грн/міс.": "Домашній інтернет (125грн/міс.)",
    "Домашній інтернет +TV Start - 125грн/міс.": "Домашній інтернет +TV Start (125грн/міс.)",
    "Домашній інтернет +TV Pro - 125грн/міс.": "Домашній інтернет +TV Pro (125грн/міс.)",
    "Домашній інтернет +TV Max - 125грн/міс.": "Домашній інтернет +TV Max (125грн/міс.)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.": "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start - 0грн/6міс.": "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro - 0грн/6міс.": "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max - 0грн/6міс.": "Домашній інтернет +TV Max (0грн/6міс.)"
}

# Покриття міст
CITIES_COVERAGE = {
    "Київ": "https://www.google.com/maps/d/viewer?mid=...",
    "Львів": "https://www.google.com/maps/d/viewer?mid=..."
    # додайте решту міст
}

# --- Валідація ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 15

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Клавіатури ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття", "Які канали входять у тариф")
    return markup

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Назад")
    return markup

def get_finish_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Завершити")
    return markup

# --- Старт ---
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_data[message.chat.id] = {"messages": [], "step": None}
    await message.answer("Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())

# --- Головне меню ---
@dp.message_handler(lambda m: m.text == "Замовити підключення")
async def order_connect(message: types.Message):
    user_data[message.chat.id]["step"] = "name"
    await message.answer("Введіть ПІБ:", reply_markup=get_back_keyboard())

@dp.message_handler(lambda m: m.text == "Назад")
async def go_back(message: types.Message):
    user_data[message.chat.id]["step"] = None
    await message.answer("Повернулись у головне меню:", reply_markup=get_main_menu())

# --- Введення даних ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "name")
async def enter_name(message: types.Message):
    if not is_valid_name(message.text):
        await message.answer("Невірний формат ПІБ. Спробуйте ще раз:")
        return
    user_data[message.chat.id]["name"] = message.text
    user_data[message.chat.id]["step"] = "address"
    await message.answer("Введіть адресу (мін. 15 символів):")

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "address")
async def enter_address(message: types.Message):
    if not is_valid_address(message.text):
        await message.answer("Занадто коротка адреса. Спробуйте ще раз:")
        return
    user_data[message.chat.id]["address"] = message.text
    user_data[message.chat.id]["step"] = "phone"
    await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "phone")
async def enter_phone(message: types.Message):
    if not is_valid_phone(message.text):
        await message.answer("Невірний формат телефону. Спробуйте ще раз:")
        return
    user_data[message.chat.id]["phone"] = message.text
    user_data[message.chat.id]["step"] = "promo"
    await message.answer("Якщо маєте промокод — введіть його, або напишіть 'Немає':")

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "promo")
async def enter_promo(message: types.Message):
    promo = message.text.strip().lower()
    if promo != "немає":
        user_data[message.chat.id]["tariffs"] = PROMO_TARIFFS
    else:
        user_data[message.chat.id]["tariffs"] = TARIFFS
    # Вибір тарифу
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for t in user_data[message.chat.id]["tariffs"].keys():
        markup.add(t)
    user_data[message.chat.id]["step"] = "tariff"
    await message.answer("Оберіть тариф:", reply_markup=markup)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "tariff")
async def choose_tariff(message: types.Message):
    tariffs = user_data[message.chat.id]["tariffs"]
    if message.text not in tariffs:
        await message.answer("Оберіть тариф з кнопок нижче.")
        return
    user_data[message.chat.id]["tariff"] = tariffs[message.text]
    # Підтвердження заявки
    name = user_data[message.chat.id]["name"]
    address = user_data[message.chat.id]["address"]
    phone = user_data[message.chat.id]["phone"]
    tariff = user_data[message.chat.id]["tariff"]
    text = (f"✅ Заявка на підключення:\n\n"
            f"👤 {name}\n🏠 {address}\n📞 {phone}\n📦 {tariff}")
    await bot.send_message(CHAT_ID, text)
    await message.answer("Ваша заявка прийнята! Очікуйте дзвінка оператора.",
                         reply_markup=get_finish_keyboard())
    user_data[message.chat.id]["step"] = "finish"

# --- Завершення ---
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_dialog(message: types.Message):
    user_data[message.chat.id]["step"] = None
    await message.answer("Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())

# --- Перевірка покриття ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for city in CITIES_COVERAGE.keys():
        markup.add(city)
    markup.add("Назад")
    user_data[message.chat.id]["step"] = "coverage_city"
    await message.answer("Оберіть місто:", reply_markup=markup)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "coverage_city")
async def coverage_city(message: types.Message):
    city = message.text
    if city in CITIES_COVERAGE:
        await message.answer(f"📍 Покриття у місті {city}: {CITIES_COVERAGE[city]}",
                             reply_markup=get_finish_keyboard())
        user_data[message.chat.id]["step"] = "finish"
    elif city == "Назад":
        await go_back(message)
    else:
        await message.answer("Оберіть місто з кнопок.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

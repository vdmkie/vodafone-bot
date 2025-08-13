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

# --- Тарифи ---
TARIFFS = {
    "Домашній інтернет -125грн/міс.\n(акційна до 31.12.2026)":
        "Домашній інтернет (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Start -125грн/міс.\n(акційна до 31.12.2026)":
        "Домашній інтернет +TV Start (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Pro -125грн/міс.\n(акційна до 31.12.2026)":
        "Домашній інтернет +TV Pro (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Max -125грн/міс.\n(акційна до 31.12.2026)":
        "Домашній інтернет +TV Max (125грн/міс. до кінця 26 року)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.\n(6 місяців безкоштовно)":
        "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start -0грн/6міс.\n(6 місяців безкоштовно)":
        "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro -0грн/6міс.\n(6 місяців безкоштовно)":
        "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max -0грн/6міс.\n(6 місяців безкоштовно)":
        "Домашній інтернет +TV Max (0грн/6міс.)"
}

CITIES_COVERAGE = {
    "Київ": "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY",
    "Львів": "https://www.google.com/maps/d/u/0/viewer?mid=1CzE-aG4mdBTiu47Oj2u_lDDPDiNdwsAl",
    "Одеса": "https://www.google.com/maps/d/u/0/viewer?mid=1WlFwsqR57hxtJvzWKHHpguYjw-Gvv6QU"
}

# --- Валидация ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 15

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Служебные ---
async def add_message(chat_id, message):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    user_data[chat_id]["messages"].append(message.message_id)

async def clear_all_except_start(chat_id: int):
    if chat_id not in user_data:
        return
    messages = user_data[chat_id].get("messages", [])
    to_delete = messages[2:]
    for msg_id in to_delete:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass
    user_data[chat_id]["messages"] = messages[:2]
    user_data[chat_id]["step"] = None

# --- Клавиатуры ---
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
async def send_welcome(message: types.Message):
    await clear_all_except_start(message.chat.id)
    user_data[message.chat.id] = {"messages": [], "step": None}
    msg = await message.answer("Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())
    await add_message(message.chat.id, msg)

# --- Обработка главного меню ---
@dp.message_handler(lambda m: m.text == "Замовити підключення")
async def order_connect(message: types.Message):
    await add_message(message.chat.id, message)
    user_data[message.chat.id]["step"] = "name"
    msg = await message.answer("Введіть ПІБ:", reply_markup=get_back_keyboard())
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: m.text == "Назад")
async def go_back(message: types.Message):
    await send_welcome(message)

# --- Ввод данных ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "name")
async def enter_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("Невірний формат ПІБ. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["name"] = message.text
    user_data[message.chat.id]["step"] = "address"
    msg = await message.answer("Введіть адресу (мін. 15 символів):")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "address")
async def enter_address(message: types.Message):
    if not is_valid_address(message.text):
        msg = await message.answer("Занадто коротка адреса. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["address"] = message.text
    user_data[message.chat.id]["step"] = "phone"
    msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "phone")
async def enter_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("Невірний формат телефону. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["phone"] = message.text
    user_data[message.chat.id]["step"] = "promo"
    msg = await message.answer("Якщо маєте промокод — введіть його, або напишіть 'Немає':")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "promo")
async def enter_promo(message: types.Message):
    promo = message.text.strip().lower()
    if promo != "немає":
        user_data[message.chat.id]["tariffs"] = PROMO_TARIFFS
    else:
        user_data[message.chat.id]["tariffs"] = TARIFFS

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in user_data[message.chat.id]["tariffs"].keys():
        markup.add(t)
    user_data[message.chat.id]["step"] = "tariff"
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "tariff")
async def choose_tariff(message: types.Message):
    tariffs = user_data[message.chat.id]["tariffs"]
    if message.text not in tariffs:
        msg = await message.answer("Оберіть тариф з кнопок нижче.")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["tariff"] = tariffs[message.text]

    # Подтверждение заявки
    name = user_data[message.chat.id]["name"]
    address = user_data[message.chat.id]["address"]
    phone = user_data[message.chat.id]["phone"]
    tariff = user_data[message.chat.id]["tariff"]

    text = f"✅ Заявка на підключення:\n\n👤 {name}\n🏠 {address}\n📞 {phone}\n📦 {tariff}"
    await bot.send_message(CHAT_ID, text)

    msg = await message.answer("Ваша заявка прийнята! Очікуйте дзвінка оператора.",
                               reply_markup=get_finish_keyboard())
    await add_message(message.chat.id, msg)
    user_data[message.chat.id]["step"] = "finish"

# --- Завершение ---
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_dialog(message: types.Message):
    await clear_all_except_start(message.chat.id)
    msg = await message.answer("Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())
    await add_message(message.chat.id, msg)

# --- Перевірка покриття ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in CITIES_COVERAGE.keys():
        markup.add(city)
    markup.add("Назад")
    user_data[message.chat.id]["step"] = "coverage_city"
    msg = await message.answer("Оберіть місто:", reply_markup=markup)
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "coverage_city")
async def coverage_city(message: types.Message):
    city = message.text
    if city in CITIES_COVERAGE:
        link = CITIES_COVERAGE[city]
        await message.answer(f"📍 Покриття у місті {city}: {link}", reply_markup=get_finish_keyboard())
        user_data[message.chat.id]["step"] = "finish"
    elif city == "Назад":
        await send_welcome(message)
    else:
        msg = await message.answer("Оберіть місто з кнопок.")
        await add_message(message.chat.id, msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

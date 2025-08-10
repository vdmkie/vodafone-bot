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
        "Домашній інтернет +TV Max (0грн/6міс.)"
}

def is_valid_name(name):
    return bool(re.match(r"^[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+\s[А-ЯІЇЄҐа-яіїєґ]+$", name.strip()))

def is_valid_address(address):
    return bool(re.search(r"[а-яА-ЯіїІЇЄєҐґ]+\s.+\d+", address.strip()))

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

async def add_message(chat_id, message):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    user_data[chat_id]["messages"].append(message.message_id)

async def delete_all_messages(chat_id):
    if chat_id in user_data:
        for msg_id in user_data[chat_id].get("messages", []):
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_data[chat_id]["messages"] = []

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття")
    markup.add("Промо-код")
    return markup

def get_finish_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити")
    return markup

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}

    photo_url = "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%B0%D0%BA%D1%86%D0%B8%D1%8F.png?raw=true"
    photo = await bot.send_photo(chat_id, photo_url)
    await add_message(chat_id, photo)

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
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await add_message(chat_id, msg)
    await add_message(chat_id, message)

@dp.message_handler(lambda message: message.text == "Замовити підключення")
async def order_connection(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id]["step"] = "get_name"
    msg = await message.answer("Введіть, будь ласка, ваше ПІБ (три слова через пробіл):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "get_name")
async def process_name(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    if not is_valid_name(name):
        msg = await message.answer("Невірний формат ПІБ. Введіть три слова через пробіл, тільки літери:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["name"] = name
    user_data[chat_id]["step"] = "get_address"
    msg = await message.answer("Введіть, будь ласка, вашу адресу (вулиця, будинок, квартира):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "get_address")
async def process_address(message: types.Message):
    chat_id = message.chat.id
    address = message.text.strip()
    if not is_valid_address(address):
        msg = await message.answer("Невірний формат адреси. Спробуйте ще раз:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["address"] = address
    user_data[chat_id]["step"] = "get_phone"
    msg = await message.answer("Введіть, будь ласка, номер телефону в форматі 380XXXXXXXXX:")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "get_phone")
async def process_phone(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    if not is_valid_phone(phone):
        msg = await message.answer("Невірний формат номера телефону. Введіть у форматі 380XXXXXXXXX:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["phone"] = phone
    user_data[chat_id]["step"] = "choose_tariff"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in TARIFFS.keys():
        markup.add(t)
    markup.add("Завершити")
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "choose_tariff")
async def process_tariff(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    if text == "Завершити":
        await message.answer("Дякуємо! Ваші дані збережено.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        await delete_all_messages(chat_id)
        return
    if text not in TARIFFS:
        msg = await message.answer("Будь ласка, оберіть тариф зі списку.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["tariff"] = TARIFFS[text]
    await message.answer(f"Дякуємо! Ви обрали тариф: {TARIFFS[text]}", reply_markup=get_main_menu())
    user_data[chat_id]["step"] = None
    await delete_all_messages(chat_id)

@dp.message_handler(lambda message: message.text == "Промо-код")
async def promo_code(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id]["step"] = "promo_code"
    msg = await message.answer("Введіть ваш промо-код:")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "promo_code")
async def process_promo_code(message: types.Message):
    chat_id = message.chat.id
    code = message.text.strip()
    # Пример проверки кода (можешь заменить на реальную логику)
    valid_codes = {"PROMO2025": True}
    if code not in valid_codes:
        msg = await message.answer("Невірний промо-код. Спробуйте ще раз або надішліть 'Відміна' для виходу.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["step"] = "choose_promo_tariff"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in PROMO_TARIFFS.keys():
        markup.add(t)
    markup.add("Відміна")
    msg = await message.answer("Оберіть тариф з промо-кодом:", reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "choose_promo_tariff")
async def process_promo_tariff(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    if text == "Відміна":
        await message.answer("Відміна. Повернення до головного меню.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        await delete_all_messages(chat_id)
        return
    if text not in PROMO_TARIFFS:
        msg = await message.answer("Будь ласка, оберіть тариф зі списку або 'Відміна'.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["promo_tariff"] = PROMO_TARIFFS[text]
    await message.answer(f"Дякуємо! Ви обрали тариф з промо-кодом: {PROMO_TARIFFS[text]}", reply_markup=get_main_menu())
    user_data[chat_id]["step"] = None
    await delete_all_messages(chat_id)

@dp.message_handler(lambda message: message.text == "Замовити консультацію")
async def order_consultation(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id]["step"] = "consultation_name"
    msg = await message.answer("Введіть, будь ласка, ваше ПІБ для консультації:")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consultation_name")
async def process_consultation_name(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    if not is_valid_name(name):
        msg = await message.answer("Невірний формат ПІБ. Введіть три слова через пробіл, тільки літери:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["consult_name"] = name
    user_data[chat_id]["step"] = "consult_phone"
    msg = await message.answer("Введіть, будь ласка, номер телефону для консультації (380XXXXXXXXX):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consult_phone")
async def process_consultation_phone(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    if not is_valid_phone(phone):
        msg = await message.answer("Невірний формат номера телефону. Введіть у форматі 380XXXXXXXXX:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["consult_phone"] = phone
    user_data[chat_id]["step"] = None
    await message.answer("Дякуємо! Ми зв’яжемося з вами найближчим часом.", reply_markup=get_main_menu())
    await delete_all_messages(chat_id)

@dp.message_handler(lambda message: message.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    msg = await message.answer("Для перевірки покриття введіть вашу адресу:")
    await add_message(chat_id, msg)
    user_data[chat_id]["step"] = "coverage_address"

@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "coverage_address")
async def process_coverage_address(message: types.Message):
    chat_id = message.chat.id
    address = message.text.strip()
    if not is_valid_address(address):
        msg = await message.answer("Невірний формат адреси. Спробуйте ще раз:")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["step"] = None
    # Тут можеш додати логіку перевірки покриття по адресі
    await message.answer(f"Перевірка покриття для адреси:\n{address}\nДякуємо за звернення!", reply_markup=get_main_menu())
    await delete_all_messages(chat_id)

@dp.message_handler(lambda message: message.text == "Завершити")
async def finish(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id]["step"] = None
    await message.answer("Дякуємо! Якщо бажаєте почати заново, надішліть /start.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

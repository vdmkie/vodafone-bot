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

PROMO_CODE = "vdmkie"

def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 10

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
    return markup

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None, "promo": False}

    photo_url = "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%B0%D0%BA%D1%86%D0%B8%D1%8F.png?raw=true"
    photo = await bot.send_photo(chat_id, photo_url)
    await add_message(chat_id, photo)

    msg = await message.answer(
        "👋 *Вітаю! Я Ваш чат-бот Тарас*\n\n"
        "💪  *Переваги нашого провайдера це...*\n"
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

# === Обработка выбора из главного меню ===
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Перевірити покриття"])
async def menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    await add_message(chat_id, message)

    if message.text == "Замовити підключення":
        # Спрашиваем про промо-код
        user_data[chat_id]["step"] = "ask_promo"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так", "Ні")
        msg = await message.answer("Чи маєте ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Перевірити покриття":
        user_data[chat_id]["step"] = "check_coverage"
        await handle_coverage(message)

# Обработка ответа на вопрос про промо-код
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo")
async def ask_promo_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    await add_message(chat_id, message)

    if text == "так":
        user_data[chat_id]["step"] = "waiting_for_promo"
        msg = await message.answer("Введіть промо-код:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    elif text == "ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так", "Ні")
        msg = await message.answer("Будь ласка, оберіть 'Так' або 'Ні'.", reply_markup=markup)
        await add_message(chat_id, msg)

# Обработка ввода промо-кода
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text.lower() == PROMO_CODE:
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):")
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Завершити")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити' для виходу.", reply_markup=markup)
        await add_message(chat_id, msg)
        user_data[chat_id]["step"] = "waiting_for_promo"

# === Обработка "Замовити підключення" - сбор данных (имя, адрес, телефон) ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["waiting_for_name", "waiting_for_address", "waiting_for_phone"])
async def order_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if step == "waiting_for_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "waiting_for_address"
        msg = await message.answer("Введіть повну адресу на підключення (місто, вулиця, будинок, квартира):")
        await add_message(chat_id, msg)

    elif step == "waiting_for_address":
        if not is_valid_address(text):
            msg = await message.answer("❗ Адреса занадто коротка або некоректна. Спробуйте ще раз:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "waiting_for_phone"
        msg = await message.answer("Введіть свій номер телефону у форматі 380xxxxxxxxx (без +):")
        await add_message(chat_id, msg)

    elif step == "waiting_for_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Номер телефону повинен містити 12 цифр і починатися з 380 (наприклад: 380991234567). Спробуйте ще раз:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text

        # Выбор тарифов
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for t in tariffs.keys():
            markup.add(t)
        msg = await message.answer("Обери тариф:", reply_markup=markup)
        user_data[chat_id]["step"] = "waiting_for_tariff"
        await add_message(chat_id, msg)

# Выбор тарифа
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS

    await add_message(chat_id, message)

    if text not in tariffs:
        msg = await message.answer("Будь ласка, оберіть тариф із запропонованого списку.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["tariff"] = tariffs[text]
    user_data[chat_id]["step"] = "confirm_order"

    data = user_data[chat_id]
    confirm_text = (
        f"Перевірте, будь ласка, дані замовлення:\n\n"
        f"ПІБ: {data['name']}\n"
        f"Адреса: {data['address']}\n"
        f"Телефон: {data['phone']}\n"
        f"Тариф: {text}\n\n"
        f"Для підтвердження натисніть 'Підтвердити', для скасування - 'Скасувати'."
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Підтвердити", "Скасувати")
    msg = await message.answer(confirm_text, reply_markup=markup)
    await add_message(chat_id, msg)

# Подтверждение или отмена заказа
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "confirm_order")
async def confirm_order_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    await add_message(chat_id, message)

    if text == "підтвердити":
        data = user_data[chat_id]
        order_text = (
            f"НОВЕ ЗАМОВЛЕННЯ\n"
            f"ПІБ: {data['name']}\n"
            f"Адреса: {data['address']}\n"
            f"Телефон: {data['phone']}\n"
            f"Тариф: {data['tariff']}\n"
            f"Промо-код: {'так' if data.get('promo') else 'ні'}"
        )
        await bot.send_message(CHAT_ID, order_text)
        await message.answer("Дякуємо! Ваше замовлення прийнято. Ми з вами зв’яжемося найближчим часом.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["messages"] = []
    elif text == "скасувати":
        await message.answer("Замовлення скасовано.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["messages"] = []
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Підтвердити", "Скасувати")
        await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Скасувати'.", reply_markup=markup)

# Обработка "Замовити консультацію" — сбор имени и телефона
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def consult_name_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if not is_valid_name(text):
        msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["consult_name"] = text
    user_data[chat_id]["step"] = "consult_phone"
    msg = await message.answer("Введіть свій номер телефону у форматі 380xxxxxxxxx (без +):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
async def consult_phone_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if not is_valid_phone(text):
        msg = await message.answer("❗ Номер телефону повинен містити 12 цифр і починатися з 380 (наприклад: 380991234567). Спробуйте ще раз:")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["consult_phone"] = text
    data = user_data[chat_id]
    consult_text = (
        f"НОВА КОНСУЛЬТАЦІЯ\n"
        f"ПІБ: {data['consult_name']}\n"
        f"Телефон: {data['consult_phone']}"
    )
    await bot.send_message(CHAT_ID, consult_text)
    await message.answer("Дякуємо! Ми передзвонимо вам найближчим часом.", reply_markup=get_main_menu())
    user_data[chat_id]["step"] = None
    user_data[chat_id]["messages"] = []

# Проверка покрытия — заглушка, можно доработать под реальные данные
async def handle_coverage(message):
    chat_id = message.chat.id
    msg = await message.answer(
        "Для перевірки покриття введіть свою адресу або район.\n\n"
        "Поки що ця функція знаходиться в розробці."
    )
    await add_message(chat_id, msg)

@dp.message_handler()
async def fallback(message: types.Message):
    chat_id = message.chat.id
    step = user_data.get(chat_id, {}).get("step")
    if step:
        msg = await message.answer("Будь ласка, користуйтеся меню або завершіть поточну дію.")
        await add_message(chat_id, msg)
    else:
        await start(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

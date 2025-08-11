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

def with_finish_button(*buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for btn in buttons:
        markup.add(btn)
    markup.add("Завершити")
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

# Обработчик для завершения в любой момент
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    await delete_all_messages(chat_id)
    await message.answer("Дія скасована. Ви повернулися в головне меню.", reply_markup=get_main_menu())

# === Обработка выбора из главного меню ===
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Перевірити покриття"])
async def menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    await add_message(chat_id, message)

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "ask_promo"
        markup = with_finish_button("Так", "Ні")
        msg = await message.answer("Чи маєте ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=with_finish_button())
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
        msg = await message.answer("Введіть промо-код:", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    elif text == "ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button("Так", "Ні")
        msg = await message.answer("Будь ласка, оберіть 'Так' або 'Ні'.", reply_markup=markup)
        await add_message(chat_id, msg)

# Обработка ввода промо-кода
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    promo = message.text.strip().lower()
    await add_message(chat_id, message)

    if promo == PROMO_CODE:
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Промо-код прийнято!\nВведіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити' для виходу.", reply_markup=markup)
        await add_message(chat_id, msg)

# Ввод ПІБ
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_name")
async def name_handler(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    await add_message(chat_id, message)

    if is_valid_name(name):
        user_data[chat_id]["name"] = name
        user_data[chat_id]["step"] = "waiting_for_address"
        msg = await message.answer("Введіть повну адресу (місто, вулиця, будинок, квартира):", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Некоректний формат ПІБ. Введіть повністю (три слова з великої літери через пробіл).", reply_markup=markup)
        await add_message(chat_id, msg)

# Ввод адреси
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_address")
async def address_handler(message: types.Message):
    chat_id = message.chat.id
    address = message.text.strip()
    await add_message(chat_id, message)

    if is_valid_address(address):
        user_data[chat_id]["address"] = address
        user_data[chat_id]["step"] = "waiting_for_phone"
        msg = await message.answer("Введіть номер телефону в форматі 380*********:", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Адреса занадто коротка або некоректна. Будь ласка, введіть повну адресу.", reply_markup=markup)
        await add_message(chat_id, msg)

# Ввод телефона
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_phone")
async def phone_handler(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    await add_message(chat_id, message)

    if is_valid_phone(phone):
        user_data[chat_id]["phone"] = phone
        user_data[chat_id]["step"] = "waiting_for_tariff"

        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS

        markup = with_finish_button(*tariffs.keys())
        msg = await message.answer("Оберіть тариф:", reply_markup=markup)
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380*********.", reply_markup=markup)
        await add_message(chat_id, msg)

# Выбор тарифа
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_handler(message: types.Message):
    chat_id = message.chat.id
    tariff_text = message.text.strip()
    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS

    if tariff_text in tariffs:
        user_data[chat_id]["tariff"] = tariffs[tariff_text]

        await delete_all_messages(chat_id)

        # Подготовка сообщения с заказом
        text = (
            f"Новий замовлення підключення!\n\n"
            f"ПІБ: {user_data[chat_id]['name']}\n"
            f"Адреса: {user_data[chat_id]['address']}\n"
            f"Телефон: {user_data[chat_id]['phone']}\n"
            f"Тариф: {user_data[chat_id]['tariff']}\n"
            f"Промо-код: {'Так' if promo else 'Ні'}"
        )

        await bot.send_message(CHAT_ID, text)
        await message.answer("Дякуємо за замовлення! Незабаром з вами зв'яжуться.", reply_markup=get_main_menu())
        user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    else:
        markup = with_finish_button(*tariffs.keys())
        msg = await message.answer("Будь ласка, оберіть тариф зі списку або натисніть 'Завершити' для виходу.", reply_markup=markup)
        await add_message(chat_id, msg)

# Заказ консультации - ввод имени
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def consult_name_handler(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    await add_message(chat_id, message)

    if is_valid_name(name):
        user_data[chat_id]["consult_name"] = name
        user_data[chat_id]["step"] = "consult_phone"
        msg = await message.answer("Введіть номер телефону в форматі 380*********:", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Некоректний формат ПІБ. Введіть повністю (три слова з великої літери через пробіл).", reply_markup=markup)
        await add_message(chat_id, msg)

# Заказ консультации - ввод телефона
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
async def consult_phone_handler(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    await add_message(chat_id, message)

    if is_valid_phone(phone):
        user_data[chat_id]["consult_phone"] = phone
        await delete_all_messages(chat_id)

        text = (
            f"Новий запит на консультацію!\n\n"
            f"ПІБ: {user_data[chat_id]['consult_name']}\n"
            f"Телефон: {user_data[chat_id]['consult_phone']}"
        )
        await bot.send_message(CHAT_ID, text)
        await message.answer("Дякуємо! Незабаром з вами зв'яжуться.", reply_markup=get_main_menu())
        user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380*********.", reply_markup=markup)
        await add_message(chat_id, msg)

# Проверка покрытия (запрос адреса)
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "check_coverage")
async def handle_coverage(message: types.Message):
    chat_id = message.chat.id
    if user_data[chat_id].get("step") == "check_coverage" and "coverage_address" not in user_data[chat_id]:
        await add_message(chat_id, message)
        user_data[chat_id]["step"] = "waiting_coverage_address"
        msg = await message.answer("Введіть адресу для перевірки покриття:", reply_markup=with_finish_button())
        await add_message(chat_id, msg)
        return

# Проверка покрытия — ввод адреса
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_coverage_address")
async def coverage_address_handler(message: types.Message):
    chat_id = message.chat.id
    address = message.text.strip()
    await add_message(chat_id, message)

    if len(address) >= 5:
        user_data[chat_id]["coverage_address"] = address
        await delete_all_messages(chat_id)

        # Тут можно добавить логику проверки адреса, например, запрос к БД или API
        # Пока просто отправим ответ
        await message.answer(f"Покриття по адресу '{address}' є. Дякуємо за запит!", reply_markup=get_main_menu())

        user_data[chat_id] = {"messages": [], "step": None, "promo": False}
    else:
        markup = with_finish_button()
        msg = await message.answer("❗ Адреса занадто коротка. Введіть коректну адресу.", reply_markup=markup)
        await add_message(chat_id, msg)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

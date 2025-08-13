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

# Тарифы для пользователей и для отправки админу
TARIFFS = {
    "Домашній інтернет -125грн/міс.\n(акція до 31.12.2026р., потім 250 грн/міс.)":
        "Домашній інтернет (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акція до 31.12.2026р., потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акція до 31.12.2026р., потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Max - 125грн/міс.\n(акція до 31.12.2026р., потім 375 грн/міс.)":
        "Домашній інтернет +TV Max (125грн/міс. до кінця 26 року)"
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
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 15

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

async def add_message(chat_id, message):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    user_data[chat_id]["messages"].append(message.message_id)

async def clear_all_except_start(chat_id: int):
    if chat_id not in user_data:
        return
    messages = user_data[chat_id].get("messages", [])
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass
    user_data[chat_id]["messages"] = []
    user_data[chat_id]["step"] = None

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення")
    return markup

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Назад")
    return markup

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None}

    msg_text = "👋 Вітаю! Я Ваш чат-бот Тарас!\n\nОберіть тариф та заповніть дані для підключення:"
    msg = await message.answer(msg_text, reply_markup=get_main_menu())
    await add_message(chat_id, msg)
    await add_message(chat_id, message)

@dp.message_handler(lambda m: m.text == "Замовити підключення")
async def order_start_handler(message: types.Message):
    chat_id = message.chat.id
    await clear_all_except_start(chat_id)
    await add_message(chat_id, message)

    user_data[chat_id]["step"] = "ask_promo_code"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Так", "Ні", "Назад")
    msg = await message.answer("Чи маєте ви промо-код?", reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo_code")
async def ask_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Назад":
        await clear_all_except_start(chat_id)
        await start(message)
        return
    if text == "Так":
        user_data[chat_id]["step"] = "waiting_for_promo_code"
        msg = await message.answer("Введіть промо-код:", reply_markup=get_back_keyboard())
        await add_message(chat_id, msg)
    elif text == "Ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть повністю ПІБ:", reply_markup=get_back_keyboard())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Так', 'Ні' або 'Назад'.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo_code")
async def waiting_for_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Назад":
        await clear_all_except_start(chat_id)
        await start(message)
        return

    if text.lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ:", reply_markup=get_back_keyboard())
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Назад")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Назад'.", reply_markup=markup)
        await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["waiting_for_name", "waiting_for_address", "waiting_for_phone"])
async def order_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Назад":
        await clear_all_except_start(chat_id)
        await start(message)
        return

    if step == "waiting_for_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери):", reply_markup=get_back_keyboard())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "waiting_for_address"
        msg = await message.answer("Введіть повну адресу на підключення (місто, вулиця, будинок, квартира):", reply_markup=get_back_keyboard())
        await add_message(chat_id, msg)

    elif step == "waiting_for_address":
        if not is_valid_address(text):
            msg = await message.answer("❗ Адреса занадто коротка або некоректна. Спробуйте ще раз:", reply_markup=get_back_keyboard())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "waiting_for_phone"
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX (без +):", reply_markup=get_back_keyboard())
        await add_message(chat_id, msg)

    elif step == "waiting_for_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:", reply_markup=get_back_keyboard())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text

        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        user_data[chat_id]["step"] = "confirm_order"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Підтвердити", "Почати заново")

        tariff_name = list(tariffs.keys())[0]
        order_summary = (
            f"Перевірте, будь ласка, введені дані:\n\n"
            f"👤 ПІБ: {user_data[chat_id]['name']}\n"
            f"🏠 Адреса: {user_data[chat_id]['address']}\n"
            f"📞 Телефон: {user_data[chat_id]['phone']}\n"
            f"💼 Тариф: {tariff_name}\n\n"
            f"Якщо все вірно, натисніть 'Підтвердити', або 'Почати заново' для зміни."
        )
        msg = await message.answer(order_summary, reply_markup=markup)
        await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "confirm_order")
async def confirm_order_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Почати заново":
        await clear_all_except_start(chat_id)
        await start(message)
        return

    if text == "Підтвердити":
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        tariff_name = list(tariffs.keys())[0]
        tariff_desc = tariffs[tariff_name]

        order_text = (
            f"👤 ПІБ: {user_data[chat_id]['name']}\n"
            f"🏠 Адреса: {user_data[chat_id]['address']}\n"
            f"📞 Телефон: {user_data[chat_id]['phone']}\n"
            f"💼 Тариф: {tariff_desc}\n"
            f"📥 *Нова заявка від користувача!*"
        )
        await bot.send_message(CHAT_ID, order_text, parse_mode="Markdown")

        await clear_all_except_start(chat_id)
        await message.answer("Дякуємо! Ваша заявка прийнята.", reply_markup=get_main_menu())
        return

    msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Почати заново'.")
    await add_message(chat_id, msg)

@dp.message_handler()
async def catch_all_handler(message: types.Message):
    if message.text == "Назад":
        chat_id = message.chat.id
        await clear_all_except_start(chat_id)
        await start(message)
    else:
        await message.answer("Будь ласка, користуйтеся меню.", reply_markup=get_main_menu())

if __name__ == "__main__":
    executor.start_polling(dp)

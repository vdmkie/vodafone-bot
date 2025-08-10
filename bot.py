import os
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Токен и ID чата для заявок из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Хранение данных по пользователям
user_data = {}

# Тарифы
TARIFFS = {
    "Домашній інтернет -125грн/міс.\n(акція до 01.01.2026р., потім 250 грн/міс.)": "Домашній інтернет (125грн/міс. до 01.01.2026)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акція до 01.01.2026р., потім 300 грн/міс.)": "Домашній інтернет +TV Start (125грн/міс. до 01.01.2026)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акція до 01.01.2026р., потім 325 грн/міс.)": "Домашній інтернет +TV Pro (125грн/міс. до 01.01.2026)",
    "Домашній інтернет +TV Max - 125грн/міс.\n(акція до 01.01.2026р., потім 375 грн/міс.)": "Домашній інтернет +TV Max (125грн/міс. до 01.01.2026)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.\n(6 місяців безкоштовно, потім 250 грн/міс.)": "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start - 0грн/6міс.\n(6 місяців безкоштовно, потім 300 грн/міс.)": "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro - 0грн/6міс.\n(6 місяців безкоштовно, потім 325 грн/міс.)": "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max - 0грн/6міс.\n(6 місяців безкоштовно, потім 375 грн/міс.)": "Домашній інтернет +TV Max (0грн/6міс.)"
}

def is_valid_name(name: str) -> bool:
    words = name.strip().split()
    if len(words) != 3:
        return False
    # Каждое слово: заглавная буква + строчные украинские буквы, без дефисов
    pattern = re.compile(r"^[А-ЯІЇЄҐ][а-яіїєґ]+$")
    return all(pattern.match(w) for w in words)

def is_valid_address(address: str) -> bool:
    return len(address.strip()) >= 10

def is_valid_phone(phone: str) -> bool:
    return re.fullmatch(r"380\d{9}", phone) is not None

async def delete_user_messages(chat_id: int):
    if chat_id in user_data:
        for msg_id in user_data[chat_id].get("messages", []):
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_data[chat_id]["messages"] = []

async def save_message(chat_id: int, message: types.Message):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    user_data[chat_id]["messages"].append(message.message_id)

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Замовити підключення", "Промо-код")
    kb.add("Перевірити покриття", "Замовити консультацію")
    return kb

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None}
    await delete_user_messages(chat_id)
    await save_message(chat_id, message)

    welcome_text = (
        "👋 Вітаємо у Vodafone 🇺🇦\n\n"
        "💪 Наші переваги:\n"
        "✅ Нова та якісна мережа\n"
        "✅ Сучасна технологія GPON\n"
        "✅ Швидкість до 1Гігабіт/сек\n"
        "✅ Безкоштовне підключення\n"
        "✅ Понад 72 години роботи без світла\n"
        "✅ Акційні тарифи\n\n"
        "Оберіть дію з меню нижче 👇"
    )
    msg = await message.answer(welcome_text, reply_markup=main_menu())
    await save_message(chat_id, msg)

@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Промо-код", "Перевірити покриття", "Замовити консультацію"])
async def menu_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text
    await delete_user_messages(chat_id)
    await save_message(chat_id, message)
    user_data[chat_id]["promo"] = False

    if text == "Замовити підключення":
        user_data[chat_id]["step"] = "get_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await save_message(chat_id, msg)

    elif text == "Промо-код":
        user_data[chat_id]["step"] = "get_promo"
        msg = await message.answer("Введіть промо-код:", reply_markup=types.ReplyKeyboardRemove())
        await save_message(chat_id, msg)

    elif text == "Перевірити покриття":
        url = "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257289%2C30.529932392320312&z=11"
        msg = await message.answer(f"Перевірте покриття за посиланням:\n{url}")
        await save_message(chat_id, msg)
        msg2 = await message.answer("Головне меню:", reply_markup=main_menu())
        await save_message(chat_id, msg2)
        user_data[chat_id]["step"] = None

    elif text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ для консультації (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await save_message(chat_id, msg)

@dp.message_handler()
async def general_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    step = user_data.get(chat_id, {}).get("step")

    await save_message(chat_id, message)

    if step == "get_promo":
        if text.lower() == "vdmkie":
            user_data[chat_id]["promo"] = True
            user_data[chat_id]["step"] = "get_name"
            msg = await message.answer("Промо-код прийнято! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович)")
            await save_message(chat_id, msg)
        else:
            msg = await message.answer("Невірний промо-код. Спробуйте ще раз або напишіть 'Завершити' для виходу.")
            await save_message(chat_id, msg)

    elif step == "get_name" or step == "consult_name":
        if not is_valid_name(text):
            msg = await message.answer("Помилка! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович).")
            await save_message(chat_id, msg)
            return

        user_data[chat_id]["name"] = text

        if step == "consult_name":
            # Для консультації просто отправляем заявку и возвращаем в меню
            await bot.send_message(CHAT_ID,
                f"Запит на консультацію:\nПІБ: {text}\nТелеграм ID: {chat_id}"
            )
            msg = await message.answer("Дякуємо! Наш оператор зв'яжеться з вами найближчим часом.", reply_markup=main_menu())
            await save_message(chat_id, msg)
            user_data[chat_id]["step"] = None
            return

        user_data[chat_id]["step"] = "get_address"
        msg = await message.answer("Введіть повну адресу у форматі (місто, вулиця, будинок, квартира):")
        await save_message(chat_id, msg)

    elif step == "get_address":
        if not is_valid_address(text):
            msg = await message.answer("Адреса занадто коротка. Спробуйте ще раз:")
            await save_message(chat_id, msg)
            return
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "get_phone"
        msg = await message.answer("Введіть телефон у форматі 380XXXXXXXXX (без +):")
        await save_message(chat_id, msg)

    elif step == "get_phone":
        if not is_valid_phone(text):
            msg = await message.answer("Невірний формат телефону. Введіть у форматі 380XXXXXXXXX (без +):")
            await save_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text

        tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key in tariffs.keys():
            kb.add(key)
        user_data[chat_id]["step"] = "get_tariff"
        msg = await message.answer("Оберіть тариф:", reply_markup=kb)
        await save_message(chat_id, msg)

    elif step == "get_tariff":
        tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
        if text not in tariffs:
            msg = await message.answer("Оберіть тариф із запропонованих.")
            await save_message(chat_id, msg)
            return

        user_data[chat_id]["tariff"] = tariffs[text]

        order_text = (
            f"Заявка на підключення - автор Вадим Рогальов:\n"
            f"ПІБ: {user_data[chat_id]['name']}\n"
            f"Адреса: {user_data[chat_id]['address']}\n"
            f"Телефон: {user_data[chat_id]['phone']}\n"
            f"Тариф: {user_data[chat_id]['tariff']}"
        )
        await bot.send_message(CHAT_ID, order_text)

        await delete_user_messages(chat_id)
        msg = await message.answer("✅ Ваша заявка прийнята! Скоро з вами зв'яжеться наш оператор.", reply_markup=main_menu())
        await save_message(chat_id, msg)
        user_data[chat_id]["step"] = None
        user_data[chat_id]["promo"] = False

    elif text.lower() == "завершити":
        await delete_user_messages(chat_id)
        msg = await message.answer("Головне меню:", reply_markup=main_menu())
        await save_message(chat_id, msg)
        user_data[chat_id]["step"] = None

    else:
        msg = await message.answer("Будь ласка, оберіть дію з меню або напишіть /start для початку.")
        await save_message(chat_id, msg)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

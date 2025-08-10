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

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None}

    photos = [
        "https://www.vodafone.ua/storage/editor/fotos/368x0/407fcc240bfc7dcd8eab213fcbd95c37_1680618586.png",
        "https://www.vodafone.ua/storage/editor/fotos/368x0/407fcc240bfc7dcd8eab213fcbd95c37_1685605369.png",
        "https://www.vodafone.ua/storage/editor/fotos/9052f72cee3116b913e90d2dcfa9aca4_1667919528.png",
        "https://www.vodafone.ua/storage/editor/fotos/9052f72cee3116b913e90d2dcfa9aca4_1667919528.png"
    ]

    for photo_url in photos:
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

# === Обработка выбора из главного меню ===
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Промо-код", "Замовити консультацію", "Перевірити покриття"])
async def menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}

    await add_message(chat_id, message)

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Промо-код":
        user_data[chat_id]["step"] = "waiting_for_promo"
        msg = await message.answer("Введіть промо-код:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Перевірити покриття":
        user_data[chat_id]["step"] = "check_coverage"
        await handle_coverage(message)

# === Обработка "Перевірити покриття" - отправка ссылки ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "check_coverage")
async def handle_coverage(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    coverage_url = "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257289%2C30.529932392320312&z=11"
    msg = await message.answer(
        f"Перевірте покриття за посиланням:\n{coverage_url}",
        disable_web_page_preview=True
    )
    await add_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Завершити")
    user_data[chat_id]["step"] = "completed"
    msg2 = await message.answer("Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)
    await add_message(chat_id, msg2)

# === Обработка "Промо-код" ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if message.text.strip().lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Завершити")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити' для виходу.", reply_markup=markup)
        await add_message(chat_id, msg)

# === Обработка "Замовити підключення" и связанной логики ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_name")
async def handle_name(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["name"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_address"
    msg = await message.answer("✅ Прийнято. Введіть адресу підключення (місто, вулиця, будинок, квартира):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_address")
async def handle_address(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if not is_valid_address(message.text):
        msg = await message.answer("❗ Невірний формат адреси. Спробуйте ще раз.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["address"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_phone")
async def handle_phone(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["phone"] = message.text.strip()
    user_data[chat_id]["step"] = "waiting_for_tariff"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    for tariff in tariffs:
        markup.add(tariff)
    await message.answer("Оберіть тариф:", reply_markup=markup)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def handle_tariff(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    if message.text not in tariffs:
        msg = await message.answer("❗ Невірний вибір тарифу. Виберіть зі списку.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["tariff"] = tariffs[message.text]
    user_data[chat_id]["step"] = "waiting_for_confirmation"

    summary = (
        f"ПІБ: {user_data[chat_id]['name']}\n"
        f"Адреса: {user_data[chat_id]['address']}\n"
        f"Телефон: {user_data[chat_id]['phone']}\n"
        f"Тариф: {user_data[chat_id]['tariff']}\n\n"
        "Ви підтверджуєте замовлення?"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Підтвердити", "Відмінити")
    msg = await message.answer(summary, reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_confirmation")
async def handle_confirmation(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if message.text == "Підтвердити":
        # Здесь можно добавить отправку заявки куда-либо
        msg = await message.answer("✅ Ваше замовлення прийнято! Дякуємо!", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["messages"].clear()
        await add_message(chat_id, msg)

    elif message.text == "Відмінити":
        msg = await message.answer("❗ Замовлення скасовано.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["messages"].clear()
        await add_message(chat_id, msg)

    else:
        msg = await message.answer("❗ Будь ласка, оберіть 'Підтвердити' або 'Відмінити'.")
        await add_message(chat_id, msg)

# === Обработка "Замовити консультацію" (аналогично заказу, но без тарифа) ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def consult_name_handler(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["consult_name"] = message.text.strip()
    user_data[chat_id]["step"] = "consult_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
async def consult_phone_handler(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["consult_phone"] = message.text.strip()
    user_data[chat_id]["step"] = "consult_confirmation"

    summary = (
        f"ПІБ: {user_data[chat_id]['consult_name']}\n"
        f"Телефон: {user_data[chat_id]['consult_phone']}\n\n"
        "Ви підтверджуєте замовлення консультації?"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Підтвердити", "Відмінити")
    msg = await message.answer(summary, reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_confirmation")
async def consult_confirmation_handler(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)

    if message.text == "Підтвердити":
        # Тут можна обработать заявку на консультацию
        msg = await message.answer("✅ Ваше замовлення на консультацію прийнято! Дякуємо!", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["messages"].clear()
        await add_message(chat_id, msg)

    elif message.text == "Відмінити":
        msg = await message.answer("❗ Замовлення консультації скасовано.", reply_markup=get_main_menu())
        user_data[chat_id]["step"] = None
        user_data[chat_id]["messages"].clear()
        await add_message(chat_id, msg)

    else:
        msg = await message.answer("❗ Будь ласка, оберіть 'Підтвердити' або 'Відмінити'.")
        await add_message(chat_id, msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

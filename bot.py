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
    # Проверка: три слова, каждое с заглавной буквы, украинские буквы
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 10  # Простая проверка длины

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
    user_data[chat_id] = {"messages": [], "step": None}

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

# === Обработка выбора из главного меню (обновленная) ===
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Перевірити покриття"])
async def menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}

    await add_message(chat_id, message)

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "ask_promo"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так", "Ні")
        msg = await message.answer("Чи маєте Ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Перевірити покриття":
        user_data[chat_id]["step"] = "check_coverage"
        await handle_coverage(message)

# Обработка ответа "Чи маєте Ви промо-код?"
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
        msg = await message.answer("Будь ласка, оберіть 'Так' або 'Ні'. Чи маєте Ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

# Обработка промо-кода
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text.lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):")
        await add_message(chat_id, msg)
    elif text.lower() == "завершити":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Завершити")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити' для виходу.", reply_markup=markup)
        await add_message(chat_id, msg)

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

# === Обработка "Замовити підключення" и связанной логики ===
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
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX (без +):")
        await add_message(chat_id, msg)

    elif step == "waiting_for_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:")
            await add_message(chat_id, msg)
            return

        user_data[chat_id]["phone"] = text

        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key in tariffs.keys():
            markup.add(key)
        markup.add("Завершити")

        user_data[chat_id]["step"] = "waiting_for_tariff"
        msg = await message.answer("Оберіть тариф:", reply_markup=markup)
        await add_message(chat_id, msg)

# === Выбор тарифа ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Завершити":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS

    if text not in tariffs:
        msg = await message.answer("❗ Будь ласка, оберіть тариф із запропонованого списку.")
        await add_message(chat_id, msg)
        return

    tariff = tariffs[text]
    name = user_data[chat_id].get("name", "Невідомо")
    address = user_data[chat_id].get("address", "Невідомо")
    phone = user_data[chat_id].get("phone", "Невідомо")
    promo_status = "Так" if promo else "Ні"

    order_text = (
        f"📝 *Заявка на підключення - автор Вадим Рогальов *\n"
        f"ПІБ: {name}\n"
        f"Адреса: {address}\n"
        f"Телефон: {phone}\n"
        f"Тариф: {tariff}\n"
        f"Промо-код: {promo_status}"
    )

    try:
        await bot.send_message(CHAT_ID, order_text, parse_mode="Markdown")
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("✅ Ваша заявка прийнята! Незабаром з вами зв'яжеться наш оператор.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    except Exception as e:
        msg = await message.answer(f"❗ Помилка надсилання заявки: {e}")
        await add_message(chat_id, msg)

# === Обработка "Замовити консультацію" ===
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["consult_name", "consult_phone"])
async def consult_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if step == "consult_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повне ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "consult_phone"
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX (без +):")
        await add_message(chat_id, msg)

    elif step == "consult_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text

        name = user_data[chat_id].get("name", "Невідомо")
        phone = user_data[chat_id].get("phone", "Невідомо")

        consult_text = (
            f"📝 *Нова заявка на консультацію*\n"
            f"ПІБ: {name}\n"
            f"Телефон: {phone}"
        )

        try:
            await bot.send_message(CHAT_ID, consult_text, parse_mode="Markdown")
            await delete_all_messages(chat_id)
            user_data[chat_id] = {"messages": [], "step": None}
            msg = await message.answer("✅ Ваша заявка на консультацію прийнята! Наш оператор зателефонує найближчим часом.", reply_markup=get_main_menu())
            await add_message(chat_id, msg)
        except Exception as e:
            msg = await message.answer(f"❗ Помилка надсилання заявки: {e}")
            await add_message(chat_id, msg)

# === Обработка "Завершити" - возвращение в меню ===
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}
    msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

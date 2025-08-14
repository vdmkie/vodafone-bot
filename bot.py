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

# --- Тарифы ---
TARIFFS = {
    "Домашній інтернет -125грн/міс.\n(акція до 31.12.2026р., потім 250 грн/міс.)": "Домашній інтернет (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акція до 31.12.2026р., потім 300 грн/міс.)": "Домашній інтернет +TV Start (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акція до 31.12.2026р., потім 325 грн/міс.)": "Домашній інтернет +TV Pro (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Max - 125грн/міс.\n(акція до 31.12.2026р., потім 375 грн/міс.)": "Домашній інтернет +TV Max (125грн/міс. до кінця 26 року)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.\n(6 місяців безкоштовно, потім 250 грн/міс.)": "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start - 0грн/6міс.\n(6 місяців безкоштовно, потім 300 грн/міс.)": "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro - 0грн/6міс.\n(6 місяців безкоштовно, потім 325 грн/міс.)": "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max - 0грн/6міс.\n(6 місяців безкоштовно, потім 375 грн/міс.)": "Домашній інтернет +TV Max (0грн/6міс.)"
}

user_data = {}

# --- Валидаторы ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 20

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Управление сообщениями ---
async def add_message(chat_id, message, static=False):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "static_messages": [], "step": None}
    if static:
        user_data[chat_id]["static_messages"].append(message.message_id)
    else:
        user_data[chat_id]["messages"].append(message.message_id)

async def delete_all_messages(chat_id):
    if chat_id in user_data:
        for msg_id in user_data[chat_id].get("messages", []):
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_data[chat_id]["messages"] = []

# --- Меню ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення","Замовити консультацію")
    markup.add("Які канали входять до TV ?")
    return markup

def get_main_menu_button_only():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Головне меню")
    return markup

# --- Возврат в главное меню ---
async def go_main_menu(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}
    msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

# --- Старт ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "static_messages": [], "step": None}

    photo_url = "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%B0%D0%BA%D1%86%D0%B8%D1%8F.png?raw=true"
    photo = await bot.send_photo(chat_id, photo_url)
    await add_message(chat_id, photo, static=True)

    msg = await message.answer(
        "👋 *Вітаю! Я Ваш чат-бот Тарас*\n\n"
        "💪 *Переваги нашого провайдера:*\n"
        "✅ Нова та якісна мережа\n"
        "✅ Cучасна технологія GPON\n"
        "✅ Швидкість до 1Гігабіт/сек\n"
        "✅ Безкоштовне підключення\n"
        "✅ Понад 72 години працює без світла\n"
        "✅ Акційні тарифи\n\n"
        "👉 *Домашній інтернет - 125грн/міс.*\n*акційна вартість тарифу до 31.12.2026р., далі 250 грн/міс.*\n\n"
        "👉 *Домашній інтернет + TV Start - 125грн/міс.*\n*акційна вартість тарифу до 31.12.2026р., далі 300 грн/міс.*\n\n"
        "👉 *Домашній інтернет + TV Pro - 125грн/міс.*\n*акційна вартість тарифу до 31.12.2026р., далі 325 грн/міс.*\n\n"
        "👉 *Домашній інтернет + TV Max - 125грн/міс.*\n*акційна вартість тарифу до 31.12.2026р., далі 375 грн/міс.*\n\n"
        "Оберіть дію з меню нижче 👇",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await add_message(chat_id, msg, static=True)
    await add_message(chat_id, message)

# --- Обработка главного меню ---
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Які канали входять до TV ?", "Головне меню"])
async def main_menu_handler(message: types.Message):
    chat_id = message.chat.id
    if message.text == "Головне меню":
        await go_main_menu(message)
        return

    await add_message(chat_id, message)
    user_data[chat_id]["step"] = None

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "ask_promo_code"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так", "Ні")
        markup.add("Головне меню")
        msg = await message.answer("Чи маєте Ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)
    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    elif message.text == "Які канали входять до TV ?":
        pdf_url = "https://github.com/vdmkie/vodafone-bot/blob/main/vf_tv.pdf?raw=true"
        msg = await bot.send_document(chat_id, pdf_url)
        await add_message(chat_id, msg)
        user_data[chat_id]["step"] = "tv_done"
        msg2 = await message.answer("Натисніть 'Головне меню', щоб повернутися в меню.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg2)

# --- Обработка промо-кода ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo_code")
async def ask_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return
    if text == "Так":
        user_data[chat_id]["step"] = "waiting_for_promo_code"
        msg = await message.answer("Введіть промо-код:", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    elif text == "Ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Прийнято! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Так', 'Ні' або 'Головне меню'.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

# --- Проверка промо-кода ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo_code")
async def waiting_for_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return
    if text.lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ:", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("❗ Невірний промо-код. Введіть ще раз або натисніть 'Головне меню'.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

# --- Обработка ввода ПІБ, адреса, телефона, тариф ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["waiting_for_name", "waiting_for_address", "waiting_for_phone"])
async def order_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return

    # --- ПІБ ---
    if step == "waiting_for_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "waiting_for_address"
        msg = await message.answer("✅ Прийнято!. Введіть повну адресу на підключення (місто, вулиця, будинок, квартира):", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

    # --- Адреса ---
    elif step == "waiting_for_address":
        if not is_valid_address(text):
            msg = await message.answer("❗ Адреса некоректна. Введіть ще раз у форматі (місто, вулиця, будинок, квартира):", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "waiting_for_phone"
        msg = await message.answer("✅ Прийнято! Введіть номер телефону у форматі 380XXXXXXXXX (без +):", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

    # --- Телефон ---
    elif step == "waiting_for_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        user_data[chat_id]["step"] = "waiting_for_tariff"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for t in tariffs.keys():
            markup.add(t)
        markup.add("Головне меню")
        summary = "Оберіть тариф:"
        msg = await message.answer(summary, reply_markup=markup)
        await add_message(chat_id, msg)

# --- Выбор тарифа ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_selection_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return

    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS
    if text not in tariffs:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for t in tariffs.keys():
            markup.add(t)
        markup.add("Головне меню")
        msg = await message.answer("✅ Прийнято! Будь ласка, оберіть тариф зі списку або натисніть 'Головне меню'.", reply_markup=markup)
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["selected_tariff"] = text
    user_data[chat_id]["step"] = "waiting_for_confirmation"

    summary = (
        f"Перевірте данні та підтвердіть заявку:\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"🏠 Адреса: {user_data[chat_id]['address']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}\n"
        f"📦 Тариф: {text}\n\n"
        "Якщо все правильно - натисніть 'Підтвердити'.\n"
        "Якщо ні - натисніть 'Головне меню'."
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Підтвердити")
    markup.add("Головне меню")
    msg = await message.answer(summary, reply_markup=markup)
    await add_message(chat_id, msg)

# --- Подтверждение заявки ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_confirmation")
async def confirmation_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return
    elif text == "Підтвердити":
        data = user_data[chat_id]
        promo = data.get("promo", False)
        tariffs_dict = PROMO_TARIFFS if promo else TARIFFS
        tariff_for_send = tariffs_dict.get(data["selected_tariff"], data["selected_tariff"])
        text_to_send = (
            f"✅ Заявка на підключення:\n\n"
            f"👤 ПІБ: {data['name']}\n"
            f"🏠 Адреса: {data['address']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📦 Тариф: {tariff_for_send}\n\n"
            f"✏️ автор Рогальов Вадим"
        )
        await bot.send_message(CHAT_ID, text_to_send)
        await delete_all_messages(chat_id)
        user_data.pop(chat_id, None)
        msg = await message.answer("Дякуємо! Ваша заявка прийнята ✅.\nНаш диспетчер зв'яжеться з Вами в найкоротший термін:", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Головне меню'.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

# --- Консультация ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["consult_name", "consult_phone", "consult_confirm"])
async def consult_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await go_main_menu(message)
        return

    if step == "consult_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери):", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "consult_phone"
        msg = await message.answer("✅ Прийнято! Введіть номер телефону у форматі 380XXXXXXXXX:", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)

    elif step == "consult_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "consult_confirm"
        summary = f"Перевірте дані для консультації:\n\n👤 ПІБ: {user_data[chat_id]['name']}\n📞 Телефон: {user_data[chat_id]['phone']}"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Підтвердити")
        markup.add("Головне меню")
        msg = await message.answer(summary, reply_markup=markup)
        await add_message(chat_id, msg)

    elif step == "consult_confirm":
        if text == "Підтвердити":
            data = user_data[chat_id]
            text_to_send = f"✅ Заявка на консультацію:\n\n👤 ПІБ: {data['name']}\n📞 Телефон: {data['phone']}\n\n✏️ автор Рогальов Вадим"
            await bot.send_message(CHAT_ID, text_to_send)
            await delete_all_messages(chat_id)
            user_data.pop(chat_id, None)
            msg = await message.answer("Дякуємо! Наш консультант зв'яжеться з Вами в найкоротший термін ✅", reply_markup=get_main_menu())
            await add_message(chat_id, msg)
        else:
            msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Головне меню'.", reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)

# --- Запуск ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

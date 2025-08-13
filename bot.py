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

CITIES_COVERAGE = {
    "Київ": "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257287%2C30.529932392320312&z=11",
    "Дніпро": "https://www.google.com/maps/d/u/0/viewer?mid=1JEKUJnE9XUTZPjd-f8jmXPcvLU4s-QhE&hl=uk&ll=48.47923374885031%2C34.92072785000002&z=15",
    "Луцьк": "https://www.google.com/maps/d/u/0/viewer?mid=1drkIR5NswXCAazpv5qmaf02lL9OfJAc&ll=50.75093726790353%2C25.32392972563127&z=12",
    "Кривий Ріг": "https://www.google.com/maps/d/u/0/viewer?mid=17kqq7EQadI5_o5bK1_lix-Qo2wbBaJY&ll=47.910800696984694%2C33.393370494687424&z=12",
    "Львів": "https://www.google.com/maps/d/u/0/viewer?mid=1CzE-aG4mdBTiu47Oj2u_lDDPDiNdwsAl&hl=uk&ll=49.78563613970314%2C24.064665899999994&z=17",
    "Миколаїв": "https://www.google.com/maps/d/u/0/viewer?mid=17YcaZFCt8EAnQ1oB8Dd-0xdOwLqWuMw&ll=46.97070266941583%2C31.969450300000013&z=13",
    "Одеса": "https://www.google.com/maps/d/u/0/viewer?mid=1WlFwsqR57hxtJvzWKHHpguYjw-Gvv6QU&ll=46.505228582262816%2C30.643495007229554&z=10",
    "Полтава": "https://www.google.com/maps/d/u/0/viewer?mid=1aGROaTa6OPOTsGvrzAbdiSPUvpZo1cA&ll=49.59354781387412%2C34.536843507594725&z=12",
    "Рівне": "https://www.google.com/maps/d/u/0/viewer?mid=1jqpYGCecy1zFXhfUz5zwTQr7aV4nXlU&ll=50.625776658980726%2C26.243116906868085&z=12",
    "Тернопіль": "https://www.google.com/maps/d/u/0/viewer?mid=1nM68n7nP6D1gRpVC3x2E-8wcq83QRDs&ll=49.560202454739375%2C25.59590906296999&z=12",
    "Харків": "https://www.google.com/maps/d/u/0/viewer?mid=19jXD4BddAs9_HAE4he7rWUUFKGEaNl3v&ll=49.95160510667597%2C36.370054685897266&z=14",
    "Чернігів": "https://www.google.com/maps/d/u/0/viewer?mid=1SR9EvlXEcIk3EeIJeJDHAPqlRYyWTvM&ll=51.50050200415294%2C31.283996303050923&z=12",
    "Чернівці": "https://www.google.com/maps/d/u/0/viewer?mid=1aedZnI80ccELyI3FWKY5xJeed9RotXA&ll=48.28432273335117%2C25.924519174020382&z=12"
}

# --- Валидаторы ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 10

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

# --- Главное меню ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття")
    markup.add("Які канали входять до TV ?")
    return markup

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
        "💪  *Переваги нашого провайдера це...*\n"
        "✅ *Нова та якісна мережа!*\n"
        "✅ *Cучасна технологія GPON!*\n"
        "✅ *Швидкість до 1Гігабіт/сек.!*\n"
        "✅ *Безкоштовне підключення!*\n"
        "✅ *Понад 72 години працює без світла!*\n"
        "✅ *Акційні тарифи!*\n\n" 
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


# Обработка главного меню
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Перевірити покриття"])
async def main_menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}

    await add_message(chat_id, message)

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "ask_promo_code"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так", "Ні", "Завершити")
        msg = await message.answer("Чи маєте Ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Перевірити покриття":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for city in CITIES_COVERAGE.keys():
            markup.add(city)
        markup.add("Назад")
        user_data[chat_id]["step"] = "choose_city"
        msg = await message.answer("Оберіть місто для перевірки покриття:", reply_markup=markup)
        await add_message(chat_id, msg)

# Обработка ответа на вопрос о промо-коде
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo_code")
async def ask_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Завершити":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    if text == "Так":
        user_data[chat_id]["step"] = "waiting_for_promo_code"
        msg = await message.answer("Введіть промо-код:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    elif text == "Ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Так', 'Ні' або 'Завершити'.")
        await add_message(chat_id, msg)

# Проверка промо-кода
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo_code")
async def waiting_for_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text.lower() == "vdmkie":  # правильный промо-код
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ:")
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Завершити")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити'.", reply_markup=markup)
        await add_message(chat_id, msg)

# Обработка ввода ФИО, адреса, телефона (для заказа подключения)
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
            msg = await message.answer("❗ Адреса некоректна. Введіть ще раз у форматі (місто, вулиця, будинок, квартира):")
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

        # Показать сводку данных и варианты подтвердить/начать заново
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        user_data[chat_id]["step"] = "waiting_for_tariff"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for t in tariffs.keys():
            markup.add(t)
        markup.add("Почати заново")
        summary = (
            f"Оберіть тариф:"
        )
        msg = await message.answer(summary, reply_markup=markup)
        await add_message(chat_id, msg)

# Выбор тарифа после ввода данных
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_selection_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS

    if text == "Почати заново":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Починаємо заново. Оберіть дію:", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    if text not in tariffs:
        msg = await message.answer("Будь ласка, оберіть тариф зі списку або натисніть 'Почати заново'.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["selected_tariff"] = text
    user_data[chat_id]["step"] = "waiting_for_confirmation"

    summary = (
        f"Перевірте данні та підтвердіть заявку:\n\n"
        f"ПІБ: {user_data[chat_id]['name']}\n"
        f"Адреса: {user_data[chat_id]['address']}\n"
        f"Телефон: {user_data[chat_id]['phone']}\n"
        f"Тариф: {text}\n\n"
        "Якщо все правильно - натисніть 'Підтвердити'.\n"
        "Якщо ні - 'Почати заново'."
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Підтвердити", "Почати заново")
    msg = await message.answer(summary, reply_markup=markup)
    await add_message(chat_id, msg)

# Подтверждение или перезапуск заказа
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_confirmation")
async def confirmation_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Почати заново":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Починаємо заново. Оберіть дію:", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
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
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Дякуємо! Ваша заявка прийнята.\nОберіть дію нижче:", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Почати заново'.")
        await add_message(chat_id, msg)

# Обработка заказа консультации: сбор ФИО и телефона, отправка в чат
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["consult_name", "consult_phone"])
async def consult_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if step == "consult_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["consult_name"] = text
        user_data[chat_id]["step"] = "consult_phone"
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX (без +):")
        await add_message(chat_id, msg)
    elif step == "consult_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["consult_phone"] = text
        # Отправка заявки консультанту
        data = user_data[chat_id]
        text_to_send = (
            f"⁉️ Заявка на консультацію:\n\n"
            f"👤 ПІБ: {data['consult_name']}\n"
            f"📞 Телефон: {data['consult_phone']}"
        )
        await bot.send_message(CHAT_ID, text_to_send)
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Дякуємо! Заявку на консультацію прийнято.\nОберіть дію нижче:", reply_markup=get_main_menu())
        await add_message(chat_id, msg)

# Обработка выбора города для покрытия
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "choose_city")
async def city_choice_handler(message: types.Message):
    chat_id = message.chat.id
    city = message.text.strip()
    await add_message(chat_id, message)

    if city == "Назад":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    if city not in CITIES_COVERAGE:
        msg = await message.answer("Будь ласка, оберіть місто зі списку.")
        await add_message(chat_id, msg)
        return

    link = CITIES_COVERAGE[city]
    await delete_all_messages(chat_id)
    msg = await message.answer(f"Покриття в місті *{city}*:\n{link}", parse_mode="Markdown", disable_web_page_preview=False)
    await add_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Назад")
    user_data[chat_id]["step"] = "coverage_done"
    msg2 = await message.answer("Натисніть 'Назад' щоб повернутися в меню.", reply_markup=markup)
    await add_message(chat_id, msg2)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "coverage_done")
async def coverage_done_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Назад":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Натисніть 'Назад' щоб повернутися в меню.")
        await add_message(chat_id, msg)

# Обработка кнопки "Завершити" в любом состоянии
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}
    msg = await message.answer("Обробка завершена. Оберіть дію з меню:", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: m.text == "Які канали входять до TV ?")
async def tv_channels_handler(message: types.Message):
    chat_id = message.chat.id
    await add_message(chat_id, message)
    
    pdf_url = "https://github.com/vdmkie/vodafone-bot/blob/main/vf_tv.pdf?raw=true"
    msg = await bot.send_document(chat_id, pdf_url)
    await add_message(chat_id, msg)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Назад")
    user_data[chat_id]["step"] = "tv_done"
    msg2 = await message.answer("Натисніть 'Назад', щоб повернутися в меню.", reply_markup=markup)
    await add_message(chat_id, msg2)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "tv_done")
async def tv_done_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Назад":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": None}
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Натисніть 'Назад' щоб повернутися в меню.")
        await add_message(chat_id, msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

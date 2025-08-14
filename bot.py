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

# --- Карта покрытия ---
COVERAGE_MAPS = {
    "Київ": "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257287%2C30.529932392320312&z=11",
    "Дніпро": "https://www.google.com/maps/d/u/0/viewer?mid=1JEKUJnE9XUTZPjd-f8jmXPcvLU4s-QhE&hl=uk&ll=48.47923374885031%2C34.92072785000002&z=15",
    "Луцьк": "https://www.google.com/maps/d/u/0/viewer?mid=1drkIR5NswXCAazpv5qmaf02lL9OfJAc&ll=50.75093726790353%2C25.32392972563127&z=12",
    "Кривий Ріг": "https://www.google.com/maps/d/u/0/viewer?mid=17kqq7EQadI5_o5bK1_lix-Qo2wbBaJY&ll=47.910800696984694%2C33.393370494687424&z=12",
    "Львів": "https://www.google.com/maps/d/u/0/viewer?mid=1CzE-aG4mdBTiu47Oj2u_lDDPDiNdwsAl&hl=uk&ll=49.785636139703115%2C24.064665899999994&z=17",
    "Миколаїв": "https://www.google.com/maps/d/u/0/viewer?mid=17YcaZFCt8EAnQ1oB8Dd-0xdOwLqWuMw&ll=46.97070266941583%2C31.969450300000013&z=13",
    "Одеса": "https://www.google.com/maps/d/u/0/viewer?mid=1WlFwsqR57hxtJvzWKHHpguYjw-Gvv6QU&ll=46.50522858226279%2C30.643495007229554&z=10",
    "Полтава": "https://www.google.com/maps/d/u/0/viewer?mid=1aGROaTa6OPOTsGvrzAbdiSPUvpZo1cA&ll=49.593547813874146%2C34.536843507594725&z=12",
    "Рівне": "https://www.google.com/maps/d/u/0/viewer?mid=1jqpYGCecy1zFXhfUz5zwTQr7aV4nXlU&ll=50.625776658980726%2C26.243116906868085&z=12",
    "Тернопіль": "https://www.google.com/maps/d/u/0/viewer?mid=1nM68n7nP6D1gRpVC3x2E-8wcq83QRDs&ll=49.560202454739375%2C25.59590906296999&z=12",
    "Харків": "https://www.google.com/maps/d/u/0/viewer?mid=19jXD4BddAs9_HAE4he7rWUUFKGEaNl3v&ll=49.95160510667597%2C36.370054685897266&z=14",
    "Чернігів": "https://www.google.com/maps/d/u/0/viewer?mid=1SR9EvlXEcIk3EeIJeJDHAPqlRYyWTvM&ll=51.50050200415294%2C31.283996303050923&z=12",
    "Житомир": "https://www.google.com/maps/d/u/0/viewer?mid=18I1hlGyULcjGR5iUnw83q90UVmsQ6z8&ll=50.26727655963132%2C28.665934083266755&z=12",
    "Запоріжжя": "https://www.google.com/maps/d/u/0/viewer?mid=1Ic-EHd0ktvKf-Xu9p-CxlEfPHDfxs0s9&ll=47.832492726471166%2C35.12242729999998&z=11",
    "Івано-Франківськ": "https://www.google.com/maps/d/u/0/viewer?mid=11nHiLJyFEDDx620KIxG17xguNgp3_GU&ll=48.92416121439265%2C24.70799684490465&z=11",
    "Чернівці": "https://www.google.com/maps/d/u/0/viewer?mid=1aedZnI80ccELyI3FWKY5xJeed9RotXA&ll=48.28432273335117%2C25.924519174020382&z=12"
}

user_data = {}

# --- Валидаторы ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 20
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
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Подивитись карту покриття")
    markup.add("Які канали входять до TV ?")
    return markup

def get_main_menu_button_only():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Головне меню")
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
        reply_markup=get_main_menu(), parse_mode="Markdown"
    )
    await add_message(chat_id, msg, static=True)
    await add_message(chat_id, message)
# --- Обработка главного меню ---
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Які канали входять до TV ?", "Подивитись карту покриття", "Головне меню"])
async def main_menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}
    await add_message(chat_id, message)

    if message.text == "Головне меню":
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    # --- Заказ подключения ---
    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("Введіть повністю ПІБ (Наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    # --- Консультация ---
    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("Введіть повністю ПІБ для консультації:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    # --- Каналы TV ---
    elif message.text == "Які канали входять до TV ?":
        pdf_url = "https://github.com/vdmkie/vodafone-bot/blob/main/vf_tv.pdf?raw=true"
        msg = await bot.send_document(chat_id, pdf_url)
        await add_message(chat_id, msg)
        msg2 = await message.answer("Натисніть 'Головне меню', щоб повернутися в меню.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg2)

    # --- Карта покрытия ---
    elif message.text == "Подивитись карту покриття":
        user_data[chat_id]["step"] = "choose_city"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for city in COVERAGE_MAPS.keys():
            markup.add(city)
        markup.add("Головне меню")
        msg = await message.answer("Оберіть місто для перегляду карти покриття:", reply_markup=markup)
        await add_message(chat_id, msg)

# --- Выбор города для карты покрытия ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "choose_city")
async def coverage_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await delete_all_messages(chat_id)
        user_data.pop(chat_id, None)
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    if text in COVERAGE_MAPS:
        map_url = COVERAGE_MAPS[text]
        await bot.send_message(chat_id, f"Карта покриття для {text}: {map_url}")
        msg = await message.answer("Натисніть 'Головне меню', щоб повернутися в меню.", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть місто зі списку або 'Головне меню'.")
        await add_message(chat_id, msg)

# --- Обработка ввода данных для заказа и консультации ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["waiting_for_name", "waiting_for_phone", "consult_name", "consult_phone"])
async def data_input_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if step in ["waiting_for_name", "consult_name"]:
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть ПІБ коректно (3 слова, кожне з великої літери):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        next_step = "waiting_for_phone" if step == "waiting_for_name" else "consult_phone"
        user_data[chat_id]["step"] = next_step
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif step in ["waiting_for_phone", "consult_phone"]:
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text

        if step == "waiting_for_phone":
            # --- Выбор тарифа ---
            user_data[chat_id]["step"] = "waiting_for_tariff"
            promo = user_data[chat_id].get("promo", False)
            tariffs = PROMO_TARIFFS if promo else TARIFFS
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for t in tariffs.keys():
                markup.add(t)
            markup.add("Головне меню")
            msg = await message.answer("Оберіть тариф:", reply_markup=markup)
            await add_message(chat_id, msg)
        else:
            # --- Консультация — проверка данных ---
            user_data[chat_id]["step"] = "consult_confirmation"
            summary = f"Перевірте данні для консультації:\n\n👤 ПІБ: {user_data[chat_id]['name']}\n📞 Телефон: {user_data[chat_id]['phone']}\n\nНатисніть 'Головне меню' для редагування або повернення в меню."
            msg = await message.answer(summary, reply_markup=get_main_menu_button_only())
            await add_message(chat_id, msg)

# --- Выбор тарифа ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_tariff")
async def tariff_selection_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await delete_all_messages(chat_id)
        user_data.pop(chat_id, None)
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    promo = user_data[chat_id].get("promo", False)
    tariffs = PROMO_TARIFFS if promo else TARIFFS
    if text not in tariffs:
        msg = await message.answer("Будь ласка, оберіть тариф зі списку або 'Головне меню'.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["selected_tariff"] = text
    user_data[chat_id]["step"] = "waiting_for_confirmation"
    summary = (
        f"Перевірте данні та підтвердіть заявку:\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}\n"
        f"📦 Тариф: {text}\n\n"
        "Натисніть 'підтвердити', щоб залишити заявку."
    )
    msg = await message.answer(summary, reply_markup=get_main_menu_button_only())
    await add_message(chat_id, msg)

# --- Подтверждение и отправка заявки и консультации ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["waiting_for_confirmation", "consult_confirmation"])
async def confirmation_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Головне меню":
        await delete_all_messages(chat_id)
        user_data.pop(chat_id, None)
        msg = await message.answer("Повернулись в головне меню.", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        return

    data = user_data[chat_id]
    if step == "waiting_for_confirmation":
        promo = data.get("promo", False)
        tariffs_dict = PROMO_TARIFFS if promo else TARIFFS
        tariff_for_send = tariffs_dict.get(data["selected_tariff"], data["selected_tariff"])
        text_to_send = (
            f"✅ Заявка на підключення:\n\n"
            f"👤 ПІБ: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📦 Тариф: {tariff_for_send}\n\n"
            f"✏️ автор Рогальов Вадим"
        )
    else:
        # Консультация
        text_to_send = (
            f"📌 Запит на консультацію:\n\n"
            f"👤 ПІБ: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
        )

    await bot.send_message(CHAT_ID, text_to_send)
    await delete_all_messages(chat_id)
    user_data.pop(chat_id, None)
    msg = await message.answer("Дякуємо! Ваш запит прийнято.\nОберіть дію нижче:", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

# --- Запуск бота ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

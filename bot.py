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
    markup.add("Карта покриття")
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
    markup.add("Карта покриття")
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
# --- Обработка выбора города карты покрытия ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "coverage")
async def coverage_city_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    coverage_dict = {
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

    if text == "Головне меню":
        await go_main_menu(message)
        return
    elif text in coverage_dict:
        msg = await message.answer(f"Ось карта покриття для міста {text}:\n{coverage_dict[text]}", reply_markup=get_main_menu_button_only())
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for city in coverage_dict.keys():
            markup.add(city)
        markup.add("Головне меню")
        msg = await message.answer("Будь ласка, оберіть місто зі списку або натисніть 'Головне меню'.", reply_markup=markup)
        await add_message(chat_id, msg)

# --- Обработка промо-кода ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo_code")
async def promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    if text == "головне меню":
        await go_main_menu(message)
        return
    elif text == "так":
        user_data[chat_id]["promo"] = True
    elif text == "ні":
        user_data[chat_id]["promo"] = False
    else:
        msg = await message.answer("Будь ласка, оберіть 'Так' або 'Ні' або 'Головне меню'.")
        await add_message(chat_id, msg)
        return

    user_data[chat_id]["step"] = "ask_name"
    msg = await message.answer("Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=get_main_menu_button_only())
    await add_message(chat_id, msg)

# --- Обработка ПІБ ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_name")
async def name_handler(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    if name.lower() == "головне меню":
        await go_main_menu(message)
        return
    if not is_valid_name(name):
        msg = await message.answer("Неправильний формат ПІБ. Введіть ще раз.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["name"] = name
    user_data[chat_id]["step"] = "ask_address"
    msg = await message.answer("Введіть повну адресу для підключення (не менше 20 символів):")
    await add_message(chat_id, msg)

# --- Обработка адреса ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_address")
async def address_handler(message: types.Message):
    chat_id = message.chat.id
    address = message.text.strip()
    if address.lower() == "головне меню":
        await go_main_menu(message)
        return
    if not is_valid_address(address):
        msg = await message.answer("Адреса занадто коротка або некоректна. Введіть ще раз.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["address"] = address
    user_data[chat_id]["step"] = "ask_phone"
    msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")
    await add_message(chat_id, msg)

# --- Обработка телефона ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_phone")
async def phone_handler(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    if phone.lower() == "головне меню":
        await go_main_menu(message)
        return
    if not is_valid_phone(phone):
        msg = await message.answer("Невірний формат номера. Введіть ще раз.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["phone"] = phone
    user_data[chat_id]["step"] = "choose_tariff"

    # --- Выбор тарифа ---
    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in tariffs.keys():
        markup.add(t)
    markup.add("Головне меню")
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    await add_message(chat_id, msg)

# --- Обработка выбора тарифа ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "choose_tariff")
async def tariff_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    if text.lower() == "головне меню":
        await go_main_menu(message)
        return
    tariffs = PROMO_TARIFFS if user_data[chat_id].get("promo") else TARIFFS
    if text not in tariffs:
        msg = await message.answer("Будь ласка, оберіть тариф зі списку.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["tariff"] = text
    user_data[chat_id]["step"] = "done"

    msg_text = (
        f"✅ Ваше замовлення успішно оформлено!\n\n"
        f"👤 ПІБ: {user_data[chat_id]['name']}\n"
        f"🏠 Адреса: {user_data[chat_id]['address']}\n"
        f"📞 Телефон: {user_data[chat_id]['phone']}\n"
        f"💰 Тариф: {user_data[chat_id]['tariff']}\n"
        f"🎉 Промо-код: {'так' if user_data[chat_id].get('promo') else 'ні'}"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Головне меню")
    msg = await message.answer(msg_text, reply_markup=markup)
    await add_message(chat_id, msg)

# --- Обработка консультации ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_name")
async def consult_name_handler(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()
    if name.lower() == "головне меню":
        await go_main_menu(message)
        return
    if not is_valid_name(name):
        msg = await message.answer("Неправильний формат ПІБ. Введіть ще раз.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["consult_name"] = name
    user_data[chat_id]["step"] = "consult_phone"
    msg = await message.answer("Введіть ваш номер телефону у форматі 380XXXXXXXXX:")
    await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "consult_phone")
async def consult_phone_handler(message: types.Message):
    chat_id = message.chat.id
    phone = message.text.strip()
    if phone.lower() == "головне меню":
        await go_main_menu(message)
        return
    if not is_valid_phone(phone):
        msg = await message.answer("Невірний формат номера. Введіть ще раз.")
        await add_message(chat_id, msg)
        return
    user_data[chat_id]["consult_phone"] = phone
    user_data[chat_id]["step"] = "consult_done"

    msg_text = (
        f"✅ Ваша заявка на консультацію прийнята!\n\n"
        f"👤 ПІБ: {user_data[chat_id]['consult_name']}\n"
        f"📞 Телефон: {user_data[chat_id]['consult_phone']}"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Головне меню")
    msg = await message.answer(msg_text, reply_markup=markup)
    await add_message(chat_id, msg)

# --- Запуск бота ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

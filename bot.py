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
    "Чернівці": "https://www.google.com/maps/d/u/0/viewer?mid=1RrUzn_Ngks5VRHkYphXZm9TXxP3x3I&ll=48.29207824870348%2C25.93555815000003&z=13"
}

# ---------------- Валидаторы ----------------
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 10

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# ---------------- Сообщения и меню ----------------
async def add_message(chat_id, message, static=False):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "static_messages": [], "step": None, "data": {}}
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

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття")
    markup.add("Які канали входять до TV ?")
    return markup

# ---------------- Старт ----------------
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "static_messages": [], "step": None, "data": {}}
    photo_url = "https://github.com/vdmkie/vodafone-bot/blob/main/%D0%B0%D0%BA%D1%86%D0%B8%D1%8F.png?raw=true"
    photo = await bot.send_photo(chat_id, photo_url)
    await add_message(chat_id, photo, static=True)
    msg = await message.answer(
        "👋 *Вітаю! Я Ваш чат-бот Тарас*\n\n"
        "💪 *Переваги нашого провайдера:*\n"
        "✅ *Нова та якісна мережа!*\n"
        "✅ *Cучасна технологія GPON!*\n"
        "✅ *Швидкість до 1Гігабіт/сек.!*\n"
        "✅ *Безкоштовне підключення!*\n"
        "✅ *Понад 72 години працює без світла!*\n"
        "✅ *Акційні тарифи!*\n\n"
        "Оберіть дію нижче 👇",
        reply_markup=get_main_menu(), parse_mode="Markdown"
    )
    await add_message(chat_id, msg, static=True)

# ---------------- Основные обработчики ----------------
@dp.message_handler(lambda message: message.text == "Перевірити покриття")
async def coverage(message: types.Message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in CITIES_COVERAGE.keys():
        markup.add(city)
    markup.add("Назад")
    msg = await message.answer("Оберіть місто:", reply_markup=markup)
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: message.text in CITIES_COVERAGE)
async def city_coverage(message: types.Message):
    chat_id = message.chat.id
    url = CITIES_COVERAGE[message.text]
    msg = await message.answer(f"Покриття для {message.text}: {url}", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: message.text == "Назад")
async def back_to_main(message: types.Message):
    chat_id = message.chat.id
    msg = await message.answer("Головне меню:", reply_markup=get_main_menu())
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: message.text == "Замовити підключення")
async def order_connection(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id]["step"] = "name"
    msg = await message.answer("Введіть ваше *ПІБ* (Напр. Іванов Іван Іванович):", parse_mode="Markdown")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "name")
async def get_name(message: types.Message):
    chat_id = message.chat.id
    if is_valid_name(message.text):
        user_data[chat_id]["data"]["name"] = message.text
        user_data[chat_id]["step"] = "address"
        msg = await message.answer("Введіть *адресу підключення*:", parse_mode="Markdown")
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Невірний формат ПІБ. Спробуйте ще раз.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "address")
async def get_address(message: types.Message):
    chat_id = message.chat.id
    if is_valid_address(message.text):
        user_data[chat_id]["data"]["address"] = message.text
        user_data[chat_id]["step"] = "phone"
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Адреса повинна містити мінімум 10 символів. Спробуйте ще раз.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "phone")
async def get_phone(message: types.Message):
    chat_id = message.chat.id
    if is_valid_phone(message.text):
        user_data[chat_id]["data"]["phone"] = message.text
        # Показ тарифів
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for t in TARIFFS.keys():
            markup.add(t)
        markup.add("Акційні тарифи", "Назад")
        user_data[chat_id]["step"] = "tariff"
        msg = await message.answer("Оберіть тариф:", reply_markup=markup)
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Невірний формат телефону. Спробуйте ще раз.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "tariff")
async def get_tariff(message: types.Message):
    chat_id = message.chat.id
    if message.text == "Акційні тарифи":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for t in PROMO_TARIFFS.keys():
            markup.add(t)
        markup.add("Назад")
        user_data[chat_id]["step"] = "promo"
        msg = await message.answer("Оберіть акційний тариф:", reply_markup=markup)
        await add_message(chat_id, msg)
    elif message.text in TARIFFS:
        user_data[chat_id]["data"]["tariff"] = TARIFFS[message.text]
        user_data[chat_id]["step"] = "confirm"
        msg = await message.answer(f"✅ Ви обрали тариф: {TARIFFS[message.text]}\n\n"
                                   f"Натисніть 'Підтвердити', щоб відправити заявку.",
                                   reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Назад"))
        await add_message(chat_id, msg)
    elif message.text == "Назад":
        await back_to_main(message)
    else:
        msg = await message.answer("Оберіть тариф з кнопок нижче.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "promo")
async def get_promo(message: types.Message):
    chat_id = message.chat.id
    if message.text in PROMO_TARIFFS:
        user_data[chat_id]["data"]["tariff"] = PROMO_TARIFFS[message.text]
        user_data[chat_id]["step"] = "confirm"
        msg = await message.answer(f"✅ Ви обрали акційний тариф: {PROMO_TARIFFS[message.text]}\n\n"
                                   f"Натисніть 'Підтвердити', щоб відправити заявку.",
                                   reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Назад"))
        await add_message(chat_id, msg)
    elif message.text == "Назад":
        await order_connection(message)
    else:
        msg = await message.answer("Оберіть тариф з кнопок нижче.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda message: message.text == "Підтвердити")
async def confirm_order(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]["data"]
    info = (
        f"✅ Нова заявка від {data['name']}!\n"
        f"📍 Адреса: {data['address']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"💻 Тариф: {data['tariff']}"
    )
    await bot.send_message(CHAT_ID, info)
    msg = await message.answer("✅ Ваша заявка відправлена! Очікуйте дзвінка від нашого менеджера.", reply_markup=get_main_menu())
    await add_message(chat_id, msg)
    user_data[chat_id]["step"] = None
    user_data[chat_id]["data"] = {}

@dp.message_handler(lambda message: message.text == "Які канали входять до TV ?")
async def tv_channels(message: types.Message):
    chat_id = message.chat.id
    msg = await message.answer_document("https://github.com/vdmkie/vodafone-bot/raw/main/tv_channels.pdf",
                                       caption="📺 Канали, що входять до TV пакету.")
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: message.text == "Замовити консультацію")
async def consultation(message: types.Message):
    chat_id = message.chat.id
    msg = await message.answer("📞 Наш менеджер зв’яжеться з вами найближчим часом.\n"
                               "Введіть ваш номер телефону (380XXXXXXXXX):")
    user_data[chat_id]["step"] = "consult_phone"
    await add_message(chat_id, msg)

@dp.message_handler(lambda message: chat_id in user_data and user_data[message.chat.id]["step"] == "consult_phone")
async def get_consult_phone(message: types.Message):
    chat_id = message.chat.id
    if is_valid_phone(message.text):
        await bot.send_message(CHAT_ID, f"📞 Запит на консультацію від {message.text}")
        msg = await message.answer("✅ Ваша заявка на консультацію відправлена!", reply_markup=get_main_menu())
        await add_message(chat_id, msg)
        user_data[chat_id]["step"] = None
    else:
        msg = await message.answer("Невірний формат телефону. Спробуйте ще раз.")
        await add_message(chat_id, msg)

# ---------------- Запуск ----------------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

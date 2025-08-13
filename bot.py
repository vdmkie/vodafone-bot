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
    "Домашній інтернет -125грн/міс.\n(акційна вартість тарифу до 31.12.2026р., потім 250 грн/міс.)":
        "Домашній інтернет (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Start - 125грн/міс.\n(акційна вартість тарифу до 31.12.2026р., потім 300 грн/міс.)":
        "Домашній інтернет +TV Start (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Pro - 125грн/міс.\n(акційна вартість тарифу до 31.12.2026р., потім 325 грн/міс.)":
        "Домашній інтернет +TV Pro (125грн/міс. до кінця 26 року)",
    "Домашній інтернет +TV Max - 125грн/міс.\n(акційна вартість тарифу до 31.12.2026р., потім 375 грн/міс.)":
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

# --- Валидация ---
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 15

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# --- Служебные ---
async def add_message(chat_id, message):
    if chat_id not in user_data:
        user_data[chat_id] = {"messages": [], "step": None}
    user_data[chat_id]["messages"].append(message.message_id)

async def clear_all_except_start(chat_id: int):
    if chat_id not in user_data:
        return
    messages = user_data[chat_id].get("messages", [])
    to_delete = messages[2:]
    for msg_id in to_delete:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass
    user_data[chat_id]["messages"] = messages[:2]
    user_data[chat_id]["step"] = None

# --- Клавиатуры ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття", "Які канали входять у тариф")
    return markup

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Назад")
    return markup

def get_finish_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Завершити")
    return markup
# --- Старт ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await clear_all_except_start(message.chat.id)
    user_data[message.chat.id] = {"messages": [], "step": None}
    photo = open("start.jpg", "rb")
    msg = await bot.send_photo(message.chat.id, photo,
        caption="Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())
    await add_message(message.chat.id, msg)

# --- Обработка главного меню ---
@dp.message_handler(lambda m: m.text == "Замовити підключення")
async def order_connect(message: types.Message):
    await add_message(message.chat.id, message)
    user_data[message.chat.id]["step"] = "name"
    msg = await message.answer("Введіть ПІБ:", reply_markup=get_back_keyboard())
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: m.text == "Назад")
async def go_back(message: types.Message):
    await send_welcome(message)

# --- Ввод данных ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "name")
async def enter_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("Невірний формат ПІБ. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["name"] = message.text
    user_data[message.chat.id]["step"] = "address"
    msg = await message.answer("Введіть адресу (мін. 15 символів):")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "address")
async def enter_address(message: types.Message):
    if not is_valid_address(message.text):
        msg = await message.answer("Занадто коротка адреса. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["address"] = message.text
    user_data[message.chat.id]["step"] = "phone"
    msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "phone")
async def enter_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("Невірний формат телефону. Спробуйте ще раз:")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["phone"] = message.text
    # Спрашиваем промокод
    user_data[message.chat.id]["step"] = "promo"
    msg = await message.answer("Якщо маєте промокод — введіть його, або напишіть 'Немає':")
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "promo")
async def enter_promo(message: types.Message):
    promo = message.text.strip().lower()
    if promo != "немає":
        user_data[message.chat.id]["tariffs"] = PROMO_TARIFFS
    else:
        user_data[message.chat.id]["tariffs"] = TARIFFS
    # Выбор тарифа
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in user_data[message.chat.id]["tariffs"].keys():
        markup.add(t)
    user_data[message.chat.id]["step"] = "tariff"
    msg = await message.answer("Оберіть тариф:", reply_markup=markup)
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "tariff")
async def choose_tariff(message: types.Message):
    tariffs = user_data[message.chat.id]["tariffs"]
    if message.text not in tariffs:
        msg = await message.answer("Оберіть тариф з кнопок нижче.")
        await add_message(message.chat.id, msg)
        return
    user_data[message.chat.id]["tariff"] = tariffs[message.text]
    # Подтверждение заявки
    name = user_data[message.chat.id]["name"]
    address = user_data[message.chat.id]["address"]
    phone = user_data[message.chat.id]["phone"]
    tariff = user_data[message.chat.id]["tariff"]
    text = (f"✅ Заявка на підключення:\n\n"
            f"👤 {name}\n🏠 {address}\n📞 {phone}\n📦 {tariff}")
    await bot.send_message(CHAT_ID, text)
    msg = await message.answer("Ваша заявка прийнята! Очікуйте дзвінка оператора.",
                               reply_markup=get_finish_keyboard())
    await add_message(message.chat.id, msg)
    user_data[message.chat.id]["step"] = "finish"

# --- Завершение ---
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_dialog(message: types.Message):
    await clear_all_except_start(message.chat.id)
    msg = await message.answer("Вітаємо! Оберіть потрібну дію:", reply_markup=get_main_menu())
    await add_message(message.chat.id, msg)

# --- Остальные команды (пример проверки покрытия) ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in CITIES_COVERAGE.keys():
        markup.add(city)
    markup.add("Назад")
    user_data[message.chat.id]["step"] = "coverage_city"
    msg = await message.answer("Оберіть місто:", reply_markup=markup)
    await add_message(message.chat.id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "coverage_city")
async def coverage_city(message: types.Message):
    city = message.text
    if city in CITIES_COVERAGE:
        link = CITIES_COVERAGE[city]
        await message.answer(f"📍 Покриття у місті {city}: {link}", reply_markup=get_finish_keyboard())
        user_data[message.chat.id]["step"] = "finish"
    elif city == "Назад":
        await send_welcome(message)
    else:
        msg = await message.answer("Оберіть місто з кнопок.")
        await add_message(message.chat.id, msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

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

# Тарифы
TARIFFS = {
    "Домашній інтернет -125грн/міс.": "Домашній інтернет (125грн/міс.)",
    "Домашній інтернет +TV Start - 125грн/міс.": "Домашній інтернет +TV Start (125грн/міс.)",
    "Домашній інтернет +TV Pro - 125грн/міс.": "Домашній інтернет +TV Pro (125грн/міс.)",
    "Домашній інтернет +TV Max - 125грн/міс.": "Домашній інтернет +TV Max (125грн/міс.)"
}

PROMO_TARIFFS = {
    "Домашній інтернет -0грн/6міс.": "Домашній інтернет (0грн/6міс.)",
    "Домашній інтернет +TV Start - 0грн/6міс.": "Домашній інтернет +TV Start (0грн/6міс.)",
    "Домашній інтернет +TV Pro - 0грн/6міс.": "Домашній інтернет +TV Pro (0грн/6міс.)",
    "Домашній інтернет +TV Max - 0грн/6міс.": "Домашній інтернет +TV Max (0грн/6міс.)"
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

# Валидация данных
def is_valid_name(name):
    return bool(re.match(r"^[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+\s[А-ЩЬЮЯІЇЄҐ][а-щьюяіїєґ]+$", name.strip()))

def is_valid_address(address):
    return len(address.strip()) >= 20

def is_valid_phone(phone):
    return bool(re.match(r"^380\d{9}$", phone.strip()))

# Работа с сообщениями пользователя
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

async def go_to_main_menu(chat_id):
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Замовити підключення", "Замовити консультацію")
    markup.add("Перевірити покриття")
    msg = await bot.send_message(chat_id, "👋 Вітаю! Оберіть дію нижче:", reply_markup=markup)
    await add_message(chat_id, msg)

def get_step_markup(options, add_back=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for opt in options:
        markup.add(opt)
    if add_back:
        markup.add("Назад")
    return markup

# Старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"messages": [], "step": None}
    await go_to_main_menu(chat_id)

# Главное меню
@dp.message_handler(lambda m: m.text in ["Замовити підключення", "Замовити консультацію", "Перевірити покриття"])
async def main_menu_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": None}

    if message.text == "Замовити підключення":
        user_data[chat_id]["step"] = "ask_promo_code"
        markup = get_step_markup(["Так", "Ні", "Завершити"], add_back=False)
        msg = await message.answer("Чи маєте ви промо-код?", reply_markup=markup)
        await add_message(chat_id, msg)

    elif message.text == "Замовити консультацію":
        user_data[chat_id]["step"] = "consult_name"
        msg = await message.answer("✅ Прийнято! Введіть повністю ПІБ (наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)

    elif message.text == "Перевірити покриття":
        user_data[chat_id]["step"] = "choose_city"
        markup = get_step_markup(list(CITIES_COVERAGE.keys()))
        msg = await message.answer("Оберіть місто для перевірки покриття:", reply_markup=markup)
        await add_message(chat_id, msg)

# Промо-код
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "ask_promo_code")
async def ask_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Завершити":
        await go_to_main_menu(chat_id)
        return
    if text == "Так":
        user_data[chat_id]["step"] = "waiting_for_promo_code"
        msg = await message.answer("Введіть промо-код:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    elif text == "Ні":
        user_data[chat_id]["promo"] = False
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Прийнято!Введіть повністю ПІБ:", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Так', 'Ні' або 'Завершити'.")
        await add_message(chat_id, msg)

@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "waiting_for_promo_code")
async def waiting_for_promo_code_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text.lower() == "vdmkie":
        user_data[chat_id]["promo"] = True
        user_data[chat_id]["step"] = "waiting_for_name"
        msg = await message.answer("✅ Промо-код прийнято! Введіть повністю ПІБ:")
        await add_message(chat_id, msg)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Завершити")
        msg = await message.answer("❗ Невірний промо-код. Спробуйте ще раз або натисніть 'Завершити'.", reply_markup=markup)
        await add_message(chat_id, msg)

# Универсальный обработчик шагов: ФИО, адрес, телефон, тариф, подтверждение
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in [
    "waiting_for_name", "waiting_for_address", "waiting_for_phone", "waiting_for_tariff", "waiting_for_confirmation"
])
async def order_steps_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    # ФИО
    if step == "waiting_for_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова, кожне з великої літери):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "waiting_for_address"
        msg = await message.answer("✅ Прийнято! Введіть повну адресу для підключення:")
        await add_message(chat_id, msg)
        return

    # Адрес
    if step == "waiting_for_address":
        if not is_valid_address(text):
            msg = await message.answer("❗ Адреса невірна. (введіть у форматі: місто, вулиця, будінок, квартира):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "waiting_for_phone"
        msg = await message.answer("✅ Прийнято! Введіть номер телефону у форматі 380XXXXXXXXX:")
        await add_message(chat_id, msg)
        return

    # Телефон
    if step == "waiting_for_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону. Введіть у форматі 380XXXXXXXXX:")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["phone"] = text
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        user_data[chat_id]["step"] = "waiting_for_tariff"
        markup = get_step_markup(list(tariffs.keys()) + ["Почати заново"], add_back=False)
        summary = (
        "Оберіть тариф:"
        )
        msg = await message.answer(summary, reply_markup=markup)
        await add_message(chat_id, msg)
        return

    # Выбор тарифа
    if step == "waiting_for_tariff":
        promo = user_data[chat_id].get("promo", False)
        tariffs = PROMO_TARIFFS if promo else TARIFFS
        if text == "Почати заново":
            await go_to_main_menu(chat_id)
            return
        if text not in tariffs:
            msg = await message.answer("✅ Прийнято! Будь ласка, оберіть тариф зі списку або натисніть 'Почати заново'.")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["selected_tariff"] = text
        user_data[chat_id]["step"] = "waiting_for_confirmation"
        summary = (
            f"Перевірте введені данні та підтвердіть заявку:\n\n"
            f"ПІБ: {user_data[chat_id]['name']}\n"
            f"Адреса: {user_data[chat_id]['address']}\n"
            f"Телефон: {user_data[chat_id]['phone']}\n"
            f"Тариф: {text}\n\n"
            "Якщо все правильно - натисніть 'Підтвердити'.\n"
            "Якщо ні - 'Почати заново'."
        )
        markup = get_step_markup(["Підтвердити", "Почати заново"], add_back=False)
        msg = await message.answer(summary, reply_markup=markup)
        await add_message(chat_id, msg)
        return

    # Подтверждение
    if step == "waiting_for_confirmation":
        if text == "Почати заново":
            await go_to_main_menu(chat_id)
            return
        elif text == "Підтвердити":
            data = user_data[chat_id]
            promo = data.get("promo", False)
            tariffs_dict = PROMO_TARIFFS if promo else TARIFFS
            tariff_for_send = tariffs_dict.get(data["selected_tariff"], data["selected_tariff"])
            text_to_send = (
                f"Заявка на підключення:\n\n"
                f"ПІБ: {data['name']}\n"
                f"Адреса: {data['address']}\n"
                f"Телефон: {data['phone']}\n"
                f"Тариф: {tariff_for_send}\n"
                f"Тариф: {tariff_for_send}\n\n"
                f"автор Рогальов Вадим:"
            )
            await bot.send_message(CHAT_ID, text_to_send)
            await go_to_main_menu(chat_id)
            return
        else:
            msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Почати заново'.")
            await add_message(chat_id, msg)
            return

# Консультация
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["consult_name", "consult_phone"])
async def consult_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    text = message.text.strip()
    await add_message(chat_id, message)

    if step == "consult_name":
        if not is_valid_name(text):
            msg = await message.answer("❗ Введіть повністю ПІБ (3 слова з великох літери - наприклад: Тарасов Тарас Тарасович):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["consult_name"] = text
        user_data[chat_id]["step"] = "consult_phone"
        msg = await message.answer("Введіть номер телефону у форматі 380XXXXXXXXX:")
        await add_message(chat_id, msg)
    elif step == "consult_phone":
        if not is_valid_phone(text):
            msg = await message.answer("❗ Некоректний номер телефону (введіть номер починаючи с 380__________):")
            await add_message(chat_id, msg)
            return
        user_data[chat_id]["consult_phone"] = text
        data = user_data[chat_id]
        text_to_send = (
            f"Заявка на консультацію:\n\n"
            f"ПІБ: {data['consult_name']}\n"
            f"Телефон: {data['consult_phone']}"
        )
        await bot.send_message(CHAT_ID, text_to_send)
        await go_to_main_menu(chat_id)

# Проверка покрытия
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") in ["choose_city", "coverage_done"])
async def coverage_handler(message: types.Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]
    city = message.text.strip()
    await add_message(chat_id, message)

    if city == "Назад":
        await go_to_main_menu(chat_id)
        return

    if step == "choose_city":
        if city not in CITIES_COVERAGE:
            msg = await message.answer("Будь ласка, оберіть місто зі списку.")
            await add_message(chat_id, msg)
            return
        link = CITIES_COVERAGE[city]
        await delete_all_messages(chat_id)
        msg = await message.answer(f"Покриття в місті *{city}*:\n{link}", parse_mode="Markdown")
        await add_message(chat_id, msg)
        markup = get_step_markup(["Назад"], add_back=False)
        user_data[chat_id]["step"] = "coverage_done"
        msg2 = await message.answer("Натисніть 'Назад' щоб повернутися в меню.", reply_markup=markup)
        await add_message(chat_id, msg2)
        return

    if step == "coverage_done":
        msg = await message.answer("Натисніть 'Назад' щоб повернутися в меню.")
        await add_message(chat_id, msg)
        return

# Завершити
@dp.message_handler(lambda m: m.text == "Завершити")
async def finish_handler(message: types.Message):
    await go_to_main_menu(message.chat.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

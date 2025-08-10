# --- Старт ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_data[message.chat.id] = {"messages": [], "step": None}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Залишити заявку", "Замовити консультацію")
    markup.add("Перевірити покриття")

    photo = await bot.send_photo(
        message.chat.id,
        "https://www.vodafone.ua/storage/editor/fotos/7f387e69a10a3da04355e7cf885e59c5_1741849417.jpg"
    )
    user_data[message.chat.id]["messages"].append(photo.message_id)

    msg = await message.answer(
        "👋 *Вітаємо у Vodafone 🇺🇦*\n\n"
        "👻 *Я Ваш бот Тарас*\n"
        "💪  *Переваги домашнього інтернету від Vodafone це...*\n"
        "✅ *Нова та якісна мережа!*\n"
        "✅ *Cучасна технологія GPON!*\n"
        "✅ *Швидкість 1Гігабіт/сек.!*\n"
        "✅ *Безкоштовне та швидке підключення!*\n"
        "✅ *Понад 72 години працює без світла!*\n"
        "✅ *Акційні тарифи!*\n\n"
        "Оберіть дію з меню нижче 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    user_data[message.chat.id]["messages"].append(msg.message_id)


# --- Початок консультації ---
@dp.message_handler(lambda message: message.text == "Замовити консультацію")
async def request_consult_name(message: types.Message):
    user_data[message.chat.id] = {"step": "consult_name", "messages": []}
    msg = await message.answer("Введіть ПІБ (наприклад: Тарасов Тарас Тарасович):")
    user_data[message.chat.id]["messages"].append(msg.message_id)


# --- Обробка ПІБ для консультації ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consult_name")
async def handle_consult_name(message: types.Message):
    if not is_valid_name(message.text):
        msg = await message.answer("❗ Невірний формат ПІБ. Приклад: Тарасов Тарас Тарасович")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return
    user_data[message.chat.id]["name"] = message.text.strip()
    user_data[message.chat.id]["step"] = "consult_phone"
    msg = await message.answer("✅ Прийнято. Введіть номер телефону (починаючи з 380...):")
    user_data[message.chat.id]["messages"].append(msg.message_id)


# --- Обробка телефону для консультації ---
@dp.message_handler(lambda message: user_data.get(message.chat.id, {}).get("step") == "consult_phone")
async def handle_consult_phone(message: types.Message):
    if not is_valid_phone(message.text):
        msg = await message.answer("❗ Невірний формат телефону. Спробуйте ще раз.")
        user_data[message.chat.id]["messages"].append(msg.message_id)
        return

    user_data[message.chat.id]["phone"] = message.text.strip()

    # Отправка в твой чат
    text = (
        "📞 Запит на консультацію:\n\n"
        f"👤 ПІБ: {user_data[message.chat.id]['name']}\n"
        f"📞 Телефон: {user_data[message.chat.id]['phone']}"
    )
    await bot.send_message(CHAT_ID, text)

    await message.answer("✅ Ваш запит на консультацію надіслано! Ми зателефонуємо найближчим часом.")
    await reset_user_state(message)


# --- Перевірити покриття ---
@dp.message_handler(lambda message: message.text == "Перевірити покриття")
async def check_coverage(message: types.Message):
    await message.answer("🔍 Перевірте покриття за посиланням:\nhttps://vodafone.ua/uk/internet-home/coverage")

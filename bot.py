# ... предыдущие импорты и настройки остаются без изменений ...

# Добавим в user_data тарифы по ключу (названию кнопки), чтобы показывать пользователю именно его выбор
# И внутри handler'ов поправим логику.

# --- В обработчике выбора тарифа ---
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

    # Сохраняем ключ (название тарифа из кнопки) для показа пользователю
    user_data[chat_id]["tariff_key"] = text
    # Для оператора — расшифровка
    user_data[chat_id]["tariff_desc"] = tariffs[text]
    user_data[chat_id]["step"] = "confirm_order"

    name = user_data[chat_id].get("name", "Невідомо")
    address = user_data[chat_id].get("address", "Невідомо")
    phone = user_data[chat_id].get("phone", "Невідомо")
    tariff_key = user_data[chat_id].get("tariff_key", "Невідомо")
    promo_status = "Так" if promo else "Ні"

    summary_text = (
        "Будь ласка, перевірте Ваші дані:\n\n"
        f"ПІБ: {name}\n"
        f"Адреса: {address}\n"
        f"Телефон: {phone}\n"
        f"Тариф: {tariff_key}\n"  # Показываем пользователю именно название тарифа из кнопки
        f"Промо-код: {promo_status}\n\n"
        "Якщо все вірно, натисніть «Підтвердити» або «Почати заново» для повторного вводу."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Підтвердити", "Почати заново")
    msg = await message.answer(summary_text, reply_markup=markup)
    await add_message(chat_id, msg)

# --- В подтверждении заявки ---
@dp.message_handler(lambda m: user_data.get(m.chat.id, {}).get("step") == "confirm_order")
async def confirm_order_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    await add_message(chat_id, message)

    if text == "Підтвердити":
        name = user_data[chat_id].get("name", "Невідомо")
        address = user_data[chat_id].get("address", "Невідомо")
        phone = user_data[chat_id].get("phone", "Невідомо")
        tariff_desc = user_data[chat_id].get("tariff_desc", "Невідомо")  # отправляем описание тарифa
        promo = user_data[chat_id].get("promo", False)
        promo_status = "Так" if promo else "Ні"

        order_text = (
            f"📝 *Заявка на підключення*\n"
            f"ПІБ: {name}\n"
            f"Адреса: {address}\n"
            f"Телефон: {phone}\n"
            f"Тариф: {tariff_desc}\n"  # отправляем оператору расшифровку тарифа
            f"Промо-код: {promo_status}"
        )

        try:
            await bot.send_message(CHAT_ID, order_text, parse_mode="Markdown")
            await delete_all_messages(chat_id)
            user_data[chat_id] = {"messages": [], "step": None}
            msg = await message.answer("✅ Ваша заявка прийнята! Наш оператор зателефонує найближчим часом.", reply_markup=get_main_menu())
            await add_message(chat_id, msg)
        except Exception as e:
            msg = await message.answer(f"❗ Помилка надсилання заявки: {e}")
            await add_message(chat_id, msg)

    elif text == "Почати заново":
        await delete_all_messages(chat_id)
        user_data[chat_id] = {"messages": [], "step": "waiting_for_name"}
        msg = await message.answer("Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
        await add_message(chat_id, msg)
    else:
        msg = await message.answer("Будь ласка, оберіть 'Підтвердити' або 'Почати заново'.")
        await add_message(chat_id, msg)

# --- Обработка кнопки "Замовити консультацію" ---
@dp.message_handler(lambda m: m.text == "Замовити консультацію")
async def consult_start_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    user_data[chat_id] = {"messages": [], "step": "consult_name"}
    msg = await message.answer("Введіть повністю ПІБ (3 слова, кожне з великої літери, наприклад: Тарасов Тарас Тарасович):", reply_markup=types.ReplyKeyboardRemove())
    await add_message(chat_id, msg)

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
            msg = await message.answer("✅ Ваша заявка на консультацію прийнята! Незабаром з вами зв'яжеться наш консультант.", reply_markup=get_main_menu())
            await add_message(chat_id, msg)
        except Exception as e:
            msg = await message.answer(f"❗ Помилка надсилання заявки: {e}")
            await add_message(chat_id, msg)

# --- Обработка кнопки "Перевірити покриття" ---
@dp.message_handler(lambda m: m.text == "Перевірити покриття")
async def coverage_handler(message: types.Message):
    chat_id = message.chat.id
    await delete_all_messages(chat_id)
    coverage_url = "https://www.google.com/maps/d/u/0/viewer?mid=1T0wyMmx7jf99vNKMX9qBkqxPnefPbnY&ll=50.45869537257289%2C30.529932392320312&z=11"
    msg = await message.answer(f"Перевірте покриття за посиланням:\n{coverage_url}", disable_web_page_preview=True)
    await add_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Завершити")
    user_data[chat_id]["step"] = "completed"
    msg2 = await message.answer("Натисніть 'Завершити' щоб повернутися до меню.", reply_markup=markup)
    await add_message(chat_id, msg2)

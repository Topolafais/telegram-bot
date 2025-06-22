import telebot
import os

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

BAN_FILE = "ban_reasons.txt"
WARN_FILE = "warns.txt"

ROONYA = 599492177
DARLIN = 1603464587
ADMIN_LIST = [ROONYA, DARLIN, 5771401595]

def is_admin(message):
    return message.from_user.id in ADMIN_LIST

def is_owner(user_id):
    return user_id in [ROONYA, DARLIN]

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав добавлять админов.")
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Используй: /addadmin <id>")
        return

    new_admin_id = int(parts[1])
    if new_admin_id in ADMIN_LIST:
        bot.send_message(message.chat.id, "ℹ️ Этот пользователь уже админ.")
    else:
        ADMIN_LIST.append(new_admin_id)
        bot.send_message(message.chat.id, f"✅ Добавлен новый админ: {new_admin_id}")

@bot.message_handler(commands=['deladmin'])
def del_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав удалять админов.")
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Используй: /deladmin <id>")
        return

    del_id = int(parts[1])
    if del_id in [ROONYA, DARLIN]:
        bot.send_message(message.chat.id, "🚫 Нельзя удалить владельцев.")
        return

    if del_id in ADMIN_LIST:
        ADMIN_LIST.remove(del_id)
        bot.send_message(message.chat.id, f"✅ Админ {del_id} удалён.")
    else:
        bot.send_message(message.chat.id, "❌ Этот пользователь не является админом.")

# /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
        "👋 Привет! Я технический бот логова кролика.\n\n"
        "Я могу:\n"
        "• Узнать причину бана\n"
        "• Узнать предупреждения\n"
        "• Подать апелляцию\n"
        "• Связаться с админом\n\n"
        "📋 Все команды: /commandlist"
    )

@bot.message_handler(commands=['adminlist'])
def admin_list(message):
    admins_text = "👑 Список админов:\n"
    for admin_id in ADMIN_LIST:
        admins_text += f"- {admin_id}\n"
    bot.send_message(message.chat.id, admins_text)

# /commandlist
@bot.message_handler(commands=['commandlist'])
def command_list(message):
    bot.send_message(message.chat.id,
        "📌 Список команд:\n"
        "/id — показать свой ID\n"
        "/banReason — узнать причину блокировки\n"
        "/saveBanReason — сохранить причину бана (только админ)\n"
        "/deleteBanReason — удалить причину бана\n"
        "/banlist — список всех банов\n"
        "/addWarn <ID> <причина> — добавить предупреждение\n"
        "/getWarns <ID> — получить предупреждения\n"
        "/deleteWarn <ID> — удалить одно предупреждение\n"
        "/clearWarns <ID> — удалить все предупреждения\n"
        "/listWarns — список всех предупреждений"
        "/addadmin — добавить админа"
        "/deladmin — удалить админа"
    )

# /id
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"🆔 Твой ID: {message.from_user.id}")

# /saveBanReason
@bot.message_handler(commands=['saveBanReason'])
def save_ban_reason(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🚫 У тебя нет прав на эту команду.")
        return
    bot.send_message(message.chat.id, "✏️ Введи ID и причину (пример: 1234567890 спам):")
    bot.register_next_step_handler(message, write_ban_reason)

def write_ban_reason(message):
    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Неверный формат. Пример: 1234567890 спам")
            return
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{parts[0]} - {parts[1]}\n")
        bot.send_message(message.chat.id, "✅ Причина бана сохранена.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

# /banReason
@bot.message_handler(commands=['banReason'])
def get_ban_reason(message):
    bot.send_message(message.chat.id, "🔍 Введи ID пользователя:")
    bot.register_next_step_handler(message, find_ban_reason)

def find_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            matches = [line.strip() for line in f if line.startswith(f"{user_id} ")]
        if matches:
            bot.send_message(message.chat.id, f"📄 Найдено:\n" + "\n".join(matches))
        else:
            bot.send_message(message.chat.id, "❌ Причина не найдена.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

# /deleteBanReason
@bot.message_handler(commands=['deleteBanReason'])
def delete_ban_reason(message):
    bot.send_message(message.chat.id, "🗑 Введи ID для удаления причины бана:")
    bot.register_next_step_handler(message, remove_ban_reason)

def remove_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} ")]
        if len(new_lines) == len(lines):
            bot.send_message(message.chat.id, "ℹ️ Причина не найдена.")
            return
        with open(BAN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, f"✅ Причина для {user_id} удалена.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

# /banlist
@bot.message_handler(commands=['banlist'])
def list_bans(message):
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        if not text:
            bot.send_message(message.chat.id, "📭 Список банов пуст.")
            return
        for i in range(0, len(text), 4096):
            bot.send_message(message.chat.id, text[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

# /addWarn
@bot.message_handler(commands=['addWarn'])
def add_warn(message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "⚠️ Формат: /addWarn <ID> <причина>")
            return
        user_id, reason = parts[1], parts[2]
        with open(WARN_FILE, "a+", encoding="utf-8") as f:
            f.seek(0)
            warns = [line for line in f if line.startswith(f"{user_id} -")]
            if len(warns) >= 3:
                bot.send_message(message.chat.id, f"🚫 У {user_id} уже 3 предупреждения.")
                return
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, f"✅ Предупреждение добавлено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# /getWarns
@bot.message_handler(commands=['getWarns'])
def get_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Формат: /getWarns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            warns = [line.strip() for line in f if line.startswith(f"{user_id} -")]
        if warns:
            bot.send_message(message.chat.id, f"📋 Предупреждения:\n" + "\n".join(warns))
        else:
            bot.send_message(message.chat.id, "✅ Нет предупреждений.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# /deleteWarn
@bot.message_handler(commands=['deleteWarn'])
def delete_warn(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Формат: /deleteWarn <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        removed = False
        new_lines = []
        for line in reversed(lines):
            if not removed and line.startswith(f"{user_id} -"):
                removed = True
                continue
            new_lines.insert(0, line)
        if removed:
            with open(WARN_FILE, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            bot.send_message(message.chat.id, f"✅ Предупреждение удалено.")
        else:
            bot.send_message(message.chat.id, "ℹ️ Предупреждений не найдено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# /clearWarns
@bot.message_handler(commands=['clearWarns'])
def clear_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Формат: /clearWarns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} -")]
        with open(WARN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, f"✅ Все предупреждения удалены.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# /listWarns
@bot.message_handler(commands=['listWarns'])
def list_warns(message):
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        if not text:
            bot.send_message(message.chat.id, "📭 Нет предупреждений.")
            return
        for i in range(0, len(text), 4096):
            bot.send_message(message.chat.id, text[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# Запуск бота
bot.polling()

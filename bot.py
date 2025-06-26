# ========= Импорты и настройки =========
import telebot
import os

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

BAN_FILE = "ban_reasons.txt"
WARN_FILE = "warns.txt"
ADMIN_CHAT_FILE = "admin_group.txt"
user_chat_sessions = {}

ROONYA = 599492177
DARLIN = 1603464587
ADMIN_LIST = [ROONYA, DARLIN, 5771401595]

# ========= Проверки доступа =========
def is_admin(message):
    return message.from_user.id in ADMIN_LIST

def is_owner(user_id):
    return user_id in [ROONYA, DARLIN]

# ========= Основные команды пользователя =========
@bot.message_handler(commands=['начать'])
def start_message(message):
    bot.send_message(message.chat.id,
        "👋 Привет! Я технический бот логова кролика.\n\n"
        "Я могу:\n"
        "• Узнать причину бана\n"
        "• Узнать предупреждения\n"
        "• Подать апелляцию\n"
        "• Связаться с админом\n\n"
        "📋 Все команды: /команды"
    )

@bot.message_handler(commands=['команды'])
def command_list_user(message):
    bot.send_message(message.chat.id,
        "📋 Доступные команды:\n"
        "/айди — показать свой ID\n"
        "/бан_причина — узнать причину блокировки\n"
        "/пред_пользователя <ID> — посмотреть предупреждения\n"
        "/обращение_к_администратору — начать диалог с админом\n"
        "/остановить_разговор_с_админом — завершить диалог"
    )

@bot.message_handler(commands=['айди'])
def get_id(message):
    bot.send_message(message.chat.id, f"🆔 Твой ID: {message.from_user.id}")

# ========= Админские команды =========
@bot.message_handler(commands=['команды_адм'])
def command_list_admin(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    bot.send_message(message.chat.id,
        "📌 Админ-команды:\n"
        "/айди — показать свой ID\n"
        "/сохранить_бан_причину — записать причину бана\n"
        "/бан_причина — узнать причину бана по ID\n"
        "/удалить_бан_причину — удалить причину бана по ID\n"
        "/бан_лист — список всех банов\n"
        "/добавить_пред <ID> <причина> — добавить предупреждение\n"
        "/пред_пользователя <ID> — получить предупреждения\n"
        "/удалить_пред <ID> — удалить последнее предупреждение\n"
        "/удались_все_пред <ID> — удалить все предупреждения\n"
        "/пред_лист — список всех предупреждений\n"
        "/добавить_админа <ID> — добавить админа\n"
        "/удалить_админа <ID> — удалить админа\n"
        "/бан <ID> <причина> — забанить пользователя"
    )

# ========= Админ-лист =========
@bot.message_handler(commands=['админ_лист'])
def admin_list(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    admins_text = "👑 Список админов:\n"
    for admin_id in ADMIN_LIST:
        admins_text += f"- {admin_id}\n"
    bot.send_message(message.chat.id, admins_text)

# ========= Управление админами =========
@bot.message_handler(commands=['добавить_админа'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав добавлять админов.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Используй: /добавить_админа <id>")
        return
    new_admin_id = int(parts[1])
    if new_admin_id in ADMIN_LIST:
        bot.send_message(message.chat.id, "ℹ️ Этот пользователь уже админ.")
    else:
        ADMIN_LIST.append(new_admin_id)
        bot.send_message(message.chat.id, f"✅ Добавлен новый админ: {new_admin_id}")

@bot.message_handler(commands=['удалить_админа'])
def del_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав удалять админов.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Используй: /удалить_админа <id>")
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

# ========= Переписка с админами =========
@bot.message_handler(commands=['группа_админов'])
def set_admin_group(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав добавлять админов.")
        return
    if message.chat.type in ['group', 'supergroup']:
        with open(ADMIN_CHAT_FILE, "w") as f:
            f.write(str(message.chat.id))
        bot.reply_to(message, "✅ Эта группа установлена как группа админов.")
    else:
        bot.reply_to(message, "❗ Эту команду нужно использовать в группе, где бот добавлен.")

@bot.message_handler(commands=['обращение_к_администратору'])
def start_admin_chat(message):
    try:
        with open(ADMIN_CHAT_FILE, "r") as f:
            group_id = int(f.read().strip())
    except:
        bot.reply_to(message, "❌ Группа админов не установлена.")
        return
    user_chat_sessions[message.from_user.id] = group_id
    bot.send_message(message.chat.id, "📨 Вы начали диалог с админом. Все ваши сообщения будут пересылаться в админскую группу. Напишите /остановить_разговор_с_админом для завершения.")

@bot.message_handler(commands=['остановить_разговор_с_админом'])
def stop_admin_chat(message):
    if message.from_user.id in user_chat_sessions:
        del user_chat_sessions[message.from_user.id]
        bot.send_message(message.chat.id, "✅ Диалог с админом завершён.")
    else:
        bot.send_message(message.chat.id, "ℹ️ У вас нет активного диалога.")

@bot.message_handler(func=lambda message: message.from_user.id in user_chat_sessions)
def forward_message_to_admin(message):
    group_id = user_chat_sessions.get(message.from_user.id)
    if group_id:
        user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
        forward_text = f"✉️ Сообщение от {user_info}:\n{message.text}"
        bot.send_message(group_id, forward_text)

# ========= Команда бана =========
@bot.message_handler(commands=['бан'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "⚠️ Формат: /бан <ID> <причина>")
        return
    user_id, reason = parts[1], parts[2]
    try:
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} забанен. Причина: {reason}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при бане: {e}")

# Запуск бота
bot.polling()
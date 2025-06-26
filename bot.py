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
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
        "👋 Welcome! I'm the Rabbit Den technical bot.\n\n"
        "I can help you:\n"
        "• Find out the reason for your ban\n"
        "• Check warnings\n"
        "• Submit an appeal\n"
        "• Contact an admin\n\n"
        "📋 Use /commands to see all options."
    )

@bot.message_handler(commands=['commands'])
def command_list_user(message):
    bot.send_message(message.chat.id,
        "📋 Available commands:\n"
        "/id — show your Telegram ID\n"
        "/ban_reason — find out why you were banned\n"
        "/get_warns <ID> — view warnings for a user\n"
        "/contact_admin — start a conversation with admin\n"
        "/stop_admin_chat — stop the conversation"
    )

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"🆔 Your ID: {message.from_user.id}")

# ========= Команды админа =========
@bot.message_handler(commands=['admin_commands'])
def admin_commands(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ You don't have permission.")
        return
    bot.send_message(message.chat.id,
        "🔧 Admin commands:\n"
        "/add_admin <ID> — add a new admin\n"
        "/remove_admin <ID> — remove an admin\n"
        "/admin_list — show all admins\n"
        "/ban <ID> <reason> — ban a user\n"
        "/save_ban_reason — manually save a ban reason\n"
        "/ban_reason — get ban reason by ID\n"
        "/delete_ban_reason — delete ban reason by ID\n"
        "/ban_list — list all bans\n"
        "/add_warn <ID> <reason> — add a warning\n"
        "/get_warns <ID> — view user warnings\n"
        "/delete_warn <ID> — delete one warning\n"
        "/clear_warns <ID> — clear all warnings\n"
        "/warn_list — list all warnings\n"
        "/set_admin_group — assign current group as admin chat"
    )

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You don't have permission to add admins.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Usage: /add_admin <id>")
        return
    new_admin_id = int(parts[1])
    if new_admin_id in ADMIN_LIST:
        bot.send_message(message.chat.id, "ℹ️ This user is already an admin.")
    else:
        ADMIN_LIST.append(new_admin_id)
        bot.send_message(message.chat.id, f"✅ New admin added: {new_admin_id}")

@bot.message_handler(commands=['remove_admin'])
def remove_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ You don't have permission to remove admins.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Usage: /remove_admin <id>")
        return
    del_id = int(parts[1])
    if del_id in [ROONYA, DARLIN]:
        bot.send_message(message.chat.id, "🚫 Cannot remove owners.")
        return
    if del_id in ADMIN_LIST:
        ADMIN_LIST.remove(del_id)
        bot.send_message(message.chat.id, f"✅ Admin {del_id} removed.")
    else:
        bot.send_message(message.chat.id, "❌ This user is not an admin.")

@bot.message_handler(commands=['admin_list'])
def list_admins(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ You don't have permission.")
        return
    text = "👑 Admin list:\n" + "\n".join([f"- {admin_id}" for admin_id in ADMIN_LIST])
    bot.send_message(message.chat.id, text)

# ========= Ban and Warn System =========
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ You don't have permission.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "⚠️ Usage: /ban <ID> <reason>")
        return
    user_id, reason = parts[1], parts[2]
    try:
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, f"✅ User {user_id} has been banned. Reason: {reason}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error while banning: {e}")

@bot.message_handler(commands=['save_ban_reason'])
def save_ban_reason(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ You don't have permission.")
        return
    msg = bot.send_message(message.chat.id, "✏️ Enter user ID and reason (e.g., 123456789 spamming):")
    bot.register_next_step_handler(msg, lambda m: write_ban_reason(m))

def write_ban_reason(message):
    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Invalid format. Use: 123456789 reason")
            return
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{parts[0]} - {parts[1]}\n")
        bot.send_message(message.chat.id, "✅ Ban reason saved.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['ban_reason'])
def get_ban_reason(message):
    msg = bot.send_message(message.chat.id, "🔍 Enter user ID:")
    bot.register_next_step_handler(msg, lambda m: find_ban_reason(m))

def find_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            matches = [line.strip() for line in f if line.startswith(f"{user_id} ")]
        if matches:
            bot.send_message(message.chat.id, "📄 Found:\n" + "\n".join(matches))
        else:
            bot.send_message(message.chat.id, "❌ No reason found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['delete_ban_reason'])
def delete_ban_reason(message):
    msg = bot.send_message(message.chat.id, "🗑 Enter user ID to remove ban reason:")
    bot.register_next_step_handler(msg, lambda m: remove_ban_reason(m))

def remove_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} ")]
        if len(new_lines) == len(lines):
            bot.send_message(message.chat.id, "ℹ️ No reason found.")
            return
        with open(BAN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, f"✅ Reason for {user_id} removed.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['ban_list'])
def list_bans(message):
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if not content:
            bot.send_message(message.chat.id, "📭 No bans recorded.")
            return
        for i in range(0, len(content), 4096):
            bot.send_message(message.chat.id, content[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['add_warn'])
def add_warn(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ You don't have permission.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "⚠️ Usage: /add_warn <ID> <reason>")
        return
    user_id, reason = parts[1], parts[2]
    try:
        with open(WARN_FILE, "a+", encoding="utf-8") as f:
            f.seek(0)
            warns = [line for line in f if line.startswith(f"{user_id} -")]
            if len(warns) >= 3:
                bot.send_message(message.chat.id, f"🚫 User {user_id} already has 3 warnings.")
                return
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, "✅ Warning added.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['get_warns'])
def get_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Usage: /get_warns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            warns = [line.strip() for line in f if line.startswith(f"{user_id} -")]
        if warns:
            bot.send_message(message.chat.id, "📋 Warnings:\n" + "\n".join(warns))
        else:
            bot.send_message(message.chat.id, "✅ No warnings found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['delete_warn'])
def delete_warn(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Usage: /delete_warn <ID>")
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
            bot.send_message(message.chat.id, "✅ Warning removed.")
        else:
            bot.send_message(message.chat.id, "ℹ️ No warnings found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['clear_warns'])
def clear_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Usage: /clear_warns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} -")]
        with open(WARN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, "✅ All warnings cleared.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['warn_list'])
def list_warns(message):
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if not content:
            bot.send_message(message.chat.id, "📭 No warnings recorded.")
            return
        for i in range(0, len(content), 4096):
            bot.send_message(message.chat.id, content[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# Запуск бота
bot.polling()
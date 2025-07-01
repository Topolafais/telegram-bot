import telebot
import os

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

BAN_FILE = "ban_reasons.txt"
WARN_FILE = "warns.txt"
ADMIN_CHAT_FILE = "admin_group.txt"
user_chat_sessions = {}
active_user_id = None

ROONYA = 599492177
DARLIN = 1603464587
ADMIN_LIST = [ROONYA, DARLIN, 5771401595]

def is_admin(message):
    return message.from_user.id in ADMIN_LIST

def is_owner(user_id):
    return user_id in [ROONYA, DARLIN]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
        "👋 Добро пожаловать! Я технический бот логова кролика.\n\n"
        "Я могу помочь вам:\n"
        "• Узнать причину вашего бана\n"
        "• Проверить предупреждения\n"
        "• Подать апелляцию\n"
        "• Связаться с администратором\n\n"
        "📋 Используйте /commands, чтобы увидеть все возможности."
    )

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.send_message(message.chat.id,
        "📋 Правила \n \n"
        "[1] — Без рекламы (в том числе и ссылок. Ссылки на лайк,тик-ток,ютуб шорт - РАЗРЕШЕНЫ. Писать со своего канала в чате - ЗАПРЕЩЕНО). \n"
        "[2] — Без оскорблений. \n"
        "[3] — Без выдачи себя за другого человека ( ники актëров и Руни). \n" 
        "[4] — Без ссор. \n" 
        "[5] — Без флуда и спама. \n" 
        "[6] — Без 18+ контента (Видео, картинки, слова). \n"
        "[7] — Без дезинформации и введения участников чата в заблуждение. \n" 
        "[8] — Без громких шумов в гс, кружочках и видео. \n"
        "[9] — Без скримеров. (Пугающие страшные картинки и видео) \n" 
        "[10] — Без обсуждения политики. \n"
        "[11] — Не говорить про Пуфа. \n"
        "[12] — Не тегать актёров и админов без причины. \n"
        "[13] — Неадекватное поведение - запрещено. \n"
        "[14] — Без шокирующих кадров (крови, ран, порезов). \n" 
        "[15] - Без слива информации. (Различные данные о человеке без его на то согласия, удалённые посты Руни.) \n" 
        "[16] - Без распространения видосов Руни в каналы, в лс и тд. Смотрим только на ютубе. \n \n" 

        "Наказание за нарушение - бан (НАВСЕГДА). Выдаëтся от 3-х предупреждений ( сокращение: предов). Обход бана карается баном. \n \n" 

        "2. Дополнительные правила: \n"
        "2.1 P.s: не зли админов..(будет плохо..). \n"
        "2.2 P.s: не обзывай ж/м пол.(будет очень плохо..). \n" 
        "3.2 P.s: не обзывай голоса участников..(будет слишком плохо..). \n"
        "4.2 P.s: админов есть нельзя^^... \n"
        "5.2 P.s: только админы могут женить и разводить людей. \n"
    )

@bot.message_handler(commands=['commands'])
def command_list_user(message):
    bot.send_message(message.chat.id,
        "📋 Доступные команды:\n"
        "/id - показать ваш Telegram ID\n"
        "/ban_reason - узнать, почему вы были забанены\n"
        "/get_warns <ID> - просмотреть предупреждения для пользователя\n"
        "/contact_admin - начать разговор с администратором\n"
        "/stop_admin_chat - остановить разговор"
    )

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"🆔 Your ID: {message.from_user.id}")

# ========= Команды админа =========
@bot.message_handler(commands=['admin_commands'])
def admin_commands(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    bot.send_message(message.chat.id,
        "🔧 Команды администратора: \n"
        "/add_admin <ID> - добавить нового администратора\n"
        "/remove_admin <ID> - удалить администратора\n"
        "/admin_list - показать всех администраторов\n"
        "/ban <ID> <причина> - забанить пользователя\n"
        "/save_ban_reason - вручную сохранить причину бана\n"
        "/ban_reason - получить причину бана по ID\n"
        "/delete_ban_reason - удалить причину бана по ID\n"
        "/ban_list - список всех банов\n"
        "/add_warn <ID> <причина> - добавить предупреждение\n"
        "/get_warns <ID> - просмотреть предупреждения пользователя\n"
        "/delete_warn <ID> - удалить одно предупреждение\n"
        "/clear_warns <ID> - очистить все предупреждения\n"
        "/warn_list - список всех предупреждений\n"
        "/set_admin_group - назначить текущую группу администратором чата"
    )

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Пример: /add_admin <id>")
        return
    new_admin_id = int(parts[1])
    if new_admin_id in ADMIN_LIST:
        bot.send_message(message.chat.id, "ℹ️ Этот пользователь уже является админом.")
    else:
        ADMIN_LIST.append(new_admin_id)
        bot.send_message(message.chat.id, f"✅ Новый админ добавлен: {new_admin_id}")

@bot.message_handler(commands=['remove_admin'])
def remove_admin(message):
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Пример: /remove_admin <id>")
        return
    del_id = int(parts[1])
    if del_id in [ROONYA, DARLIN]:
        bot.send_message(message.chat.id, "🚫 Нельзя убрать владельца.")
        return
    if del_id in ADMIN_LIST:
        ADMIN_LIST.remove(del_id)
        bot.send_message(message.chat.id, f"✅ Админ {del_id} убран.")
    else:
        bot.send_message(message.chat.id, "❌ Этот пользователь не админ.")

@bot.message_handler(commands=['admin_list'])
def list_admins(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    text = "👑 Admin list:\n" + "\n".join([f"- {admin_id}" for admin_id in ADMIN_LIST])
    bot.send_message(message.chat.id, text)

# ========= Ban and Warn System =========
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "⚠️ Пример: /ban <ID> <reason>")
        return
    user_id, reason = parts[1], parts[2]
    try:
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} был заблокирован. Причина: {reason}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['save_ban_reason'])
def save_ban_reason(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    msg = bot.send_message(message.chat.id, "✏️ Введите ID и причину (123456789 спам):")
    bot.register_next_step_handler(msg, lambda m: write_ban_reason(m))

def write_ban_reason(message):
    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Не верный формат. Пример: 123456789 причина")
            return
        with open(BAN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{parts[0]} - {parts[1]}\n")
        bot.send_message(message.chat.id, "✅ Причина блокировки сохраненеа.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['ban_reason'])
def get_ban_reason(message):
    msg = bot.send_message(message.chat.id, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, lambda m: find_ban_reason(m))

def find_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            matches = [line.strip() for line in f if line.startswith(f"{user_id} ")]
        if matches:
            bot.send_message(message.chat.id, "📄 Найдено:\n" + "\n".join(matches))
        else:
            bot.send_message(message.chat.id, "❌ У вас нет доступа.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['delete_ban_reason'])
def delete_ban_reason(message):
    msg = bot.send_message(message.chat.id, "🗑 Введите ID:")
    bot.register_next_step_handler(msg, lambda m: remove_ban_reason(m))

def remove_ban_reason(message):
    user_id = message.text.strip()
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} ")]
        if len(new_lines) == len(lines):
            bot.send_message(message.chat.id, "ℹ️ Причины не найдено.")
            return
        with open(BAN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, f"✅ Причина {user_id} убрана.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['ban_list'])
def list_bans(message):
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if not content:
            bot.send_message(message.chat.id, "📭 Список пуст.")
            return
        for i in range(0, len(content), 4096):
            bot.send_message(message.chat.id, content[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['add_warn'])
def add_warn(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ У вас нет доступа.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "⚠️ Пример: /add_warn <ID> <reason>")
        return
    user_id, reason = parts[1], parts[2]
    try:
        with open(WARN_FILE, "a+", encoding="utf-8") as f:
            f.seek(0)
            warns = [line for line in f if line.startswith(f"{user_id} -")]
            if len(warns) >= 3:
                bot.send_message(message.chat.id, f"🚫 Пользователь {user_id} уже имеет 3 предупреждения.")
                return
            f.write(f"{user_id} - {reason}\n")
        bot.send_message(message.chat.id, "✅ Предупреждение выдано.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['get_warns'])
def get_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Пример: /get_warns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            warns = [line.strip() for line in f if line.startswith(f"{user_id} -")]
        if warns:
            bot.send_message(message.chat.id, "📋 Предупреждения:\n" + "\n".join(warns))
        else:
            bot.send_message(message.chat.id, "✅ Предупреждений не найдено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['delete_warn'])
def delete_warn(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Пример: /delete_warn <ID>")
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
            bot.send_message(message.chat.id, "✅ Предупреждение убрано.")
        else:
            bot.send_message(message.chat.id, "ℹ️ Предупреждений не найдено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['clear_warns'])
def clear_warns(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Пример: /clear_warns <ID>")
        return
    user_id = parts[1]
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if not line.startswith(f"{user_id} -")]
        with open(WARN_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        bot.send_message(message.chat.id, "✅ Все предупреждения убраны.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['warn_list'])
def list_warns(message):
    try:
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if not content:
            bot.send_message(message.chat.id, "📭 Список пуст.")
            return
        for i in range(0, len(content), 4096):
            bot.send_message(message.chat.id, content[i:i+4096])
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Проблема: {e}")

@bot.message_handler(commands=['set_admin_group'])
def set_admin_group(message):
    if message.chat.type in ['group', 'supergroup']:
        with open(ADMIN_CHAT_FILE, "w") as f:
            f.write(str(message.chat.id))
        bot.reply_to(message, "✅ Эта группа установлена как группа админов.")
    else:
        bot.reply_to(message, "❗ Эту команду нужно использовать в группе, где бот добавлен.")

@bot.message_handler(commands=['contact_admin'])
def start_admin_chat(message):
    try:
        with open(ADMIN_CHAT_FILE, "r") as f:
            group_id = int(f.read().strip())
    except:
        bot.reply_to(message, "❌ Группа админов не установлена.")
        return

    user_chat_sessions[message.from_user.id] = group_id
    bot.send_message(message.chat.id, "📨 Вы начали диалог с админом. Все ваши сообщения будут пересылаться в админскую группу. Напишите /остановить_разговор_с_админом для завершения.")

@bot.message_handler(commands=['stop_admin_chat'])
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

bot.polling()
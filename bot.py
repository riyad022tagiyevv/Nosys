import telebot
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from datetime import datetime
import pytz
import config
import re
from soyus import bad_words

bot = telebot.TeleBot(config.TOKEN, parse_mode="HTML")


def get_main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(
            "➕ Məni Qrupuna Əlavə et ➕",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )
    kb.row(
        InlineKeyboardButton("📚 Bot Əmrləri", callback_data="commands"),
        InlineKeyboardButton("🧑‍🔧 Bot Dəstək", url=config.SUPPORT_URL)
    )
    kb.row(
        InlineKeyboardButton("🧑‍💻 Bot Sahibi", url=config.OWNER_URL)
    )
    return kb


# ===================== START =====================
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user = message.from_user

    # Qrup üçün
    if message.chat.type in ["group", "supergroup"]:
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "🇦🇿 Bota Daxil ol 🇦🇿",
                url=f"https://t.me/{bot.get_me().username}?start=private"
            )
        )
        bot.send_message(
            chat_id,
            f"Salam {user.first_name} 🙋\n"
            f"Funksiyalarımı görmək üçün şəxsi mesajıma daxil ol 🧑‍🔧",
            reply_markup=kb
        )
        return

    # Şəxsi mesaj üçün sadə start
    bot.send_photo(
        chat_id,
        config.START_IMAGE,
        caption=(
            f"🙋 Salam {user.first_name}\n"
            f"🇦🇿 Mən Azərbaycan dil dəstəkli botam\n"
            f"🛡️ Qrupunuza əlavə edərək söyüşlü cümlələrdən azad ola bilərsiniz"
        ),
        reply_markup=get_main_keyboard()
    )


# ===================== ID =====================
@bot.message_handler(commands=['id'])
def get_id(message):
    if message.reply_to_message:
        bot.reply_to(
            message,
            f"🗣️ İstifadəçi ID nömrəsi - <code>{message.reply_to_message.from_user.id}</code>\n"
            f"💁 Chat ID - <code>{message.chat.id}</code>"
        )
    else:
        bot.reply_to(
            message,
            f"🗣️ Sənin ID nömrən - <code>{message.from_user.id}</code>\n"
            f"💁 Chat ID - <code>{message.chat.id}</code>"
        )


# ===================== ADMINS =====================
@bot.message_handler(commands=['admins'])
def list_admins(message):
    if message.chat.type in ["group", "supergroup"]:
        admins = bot.get_chat_administrators(message.chat.id)
        admin_list = ""
        i = 1
        for admin in admins:
            if not admin.user.is_bot:
                admin_list += f"{i}. {admin.user.first_name}\n"
                i += 1

        if admin_list:
            bot.reply_to(
                message,
                f"💁 {message.chat.title} Qrupundakı adminlər 🥷\n\n{admin_list}"
            )
        else:
            bot.reply_to(message, "❌ Qrupda insan admin tapılmadı.")
    else:
        bot.reply_to(message, "Bu əmri yalnız qrupda istifadə edə bilərsiniz!")


# ===================== INFO =====================
@bot.message_handler(commands=['info'])
def user_info(message):
    chat_id = message.chat.id
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user

    try:
        member = bot.get_chat_member(chat_id, user.id)
        banned_status = "Bəli" if member.status in ["kicked", "restricted"] else "Xeyr"
    except:
        banned_status = "Naməlum"

    baku_tz = pytz.timezone("Asia/Baku")
    current_time = datetime.now(baku_tz).strftime("%Y-%m-%d %H:%M:%S")

    photos = bot.get_user_profile_photos(user.id, limit=1)
    text = (
        f"💁 İstifadəçi: {user.first_name}\n"
        f"🗣️ ID: {user.id}\n"
        f"🏡 Chat: {message.chat.title}\n"
        f"⏰ Time: {current_time}\n"
        f"⛔ Qadağan: {banned_status}"
    )

    if photos.total_count > 0:
        bot.send_photo(chat_id, photos.photos[0][-1].file_id, caption=text)
    else:
        bot.send_message(chat_id, text)


# ===================== CALLBACK =====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = call.from_user

    if call.data == "commands":
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("◀️ Geri", callback_data="back"))
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=(
                f"👀 Salam {user.first_name}\n\n"
                f"/id - istifadəçi ID 🛠️\n"
                f"/admins - admin siyahısı 🥷\n"
                f"/info - istifadəçi məlumatı 📝"
            ),
            reply_markup=kb
        )

    elif call.data == "back":
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(
                config.START_IMAGE,
                caption=(
                    f"🙋 Salam {user.first_name}\n"
                    f"🇦🇿 Mən Azərbaycan dil dəstəkli botam\n"
                    f"🛡️ Qrupunuza əlavə edərək söyüşlü cümlələrdən azad ola bilərsiniz"
                )
            ),
            reply_markup=get_main_keyboard()
        )


# ===================== SÖYÜŞ FİLTRİ =====================
@bot.message_handler(func=lambda message: True)
def filter_bad_words(message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    if message.from_user.is_bot:
        return

    text = (message.text or "").lower()
    caption = (message.caption or "").lower()
    if text.startswith("/"):
        return

    pattern = r"\b(" + "|".join(re.escape(w.lower()) for w in bad_words) + r")\b"

    if re.search(pattern, text) or re.search(pattern, caption):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(
                message.chat.id,
                f"🛡️ {message.from_user.first_name}, qrupda söyüş qadağandır ⛔"
            )
        except:
            pass


print("Bot işə düşdü...")
bot.infinity_polling()

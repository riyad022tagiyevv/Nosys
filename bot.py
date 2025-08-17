import telebot
import time
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from datetime import datetime
import pytz
import config
from soyus import bad_words

bot = telebot.TeleBot(config.TOKEN, parse_mode="HTML")


def get_main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("➕ Məni Qrupuna Əlavə et ➕",
                             url=f"https://t.me/{bot.get_me().username}?startgroup=true")
    )
    kb.row(
        InlineKeyboardButton("📚 Bot Əmrləri", callback_data="commands"),
        InlineKeyboardButton("🧑‍🔧 Bot Dəstək", url=config.SUPPORT_URL)
    )
    kb.row(
        InlineKeyboardButton("🧑‍💻 Bot Sahibi", url=config.OWNER_URL)
    )
    return kb


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user = message.from_user

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
            f"Salam {user.first_name} 🙋\nMənim funksiyalarımı görmək üçün zəhmət olmasa şəxsi pm mesajıma daxil ol 🧑‍🔧",
            reply_markup=kb
        )
        return

    msg = bot.send_message(chat_id, "🔞")
    time.sleep(2)
    bot.delete_message(chat_id, msg.message_id)

    def animate():
        anim_text = "𝘕𝘰 𝘚𝘰̈𝘺𝘶̈𝘴 𝘣𝘢𝘴𝘭𝘢𝘵𝘪𝘭𝘪𝘳"
        anim_msg = bot.send_message(chat_id, anim_text)
        for i in range(6):
            try:
                bot.edit_message_text(anim_text + "." * (i % 4), chat_id, anim_msg.message_id)
            except:
                pass
            time.sleep(0.5)
        try:
            bot.delete_message(chat_id, anim_msg.message_id)
        except:
            pass

        bot.send_photo(
            chat_id,
            config.START_IMAGE,
            caption=f"🙋 Salam {user.first_name}\n🇦🇿 Mən Azərbaycan dil dəstəkli botam\n🛡️ Qrupunuza əlavə edərək söyüşlü cümlələrdən azad ola bilərsiniz",
            reply_markup=get_main_keyboard()
        )

    threading.Thread(target=animate).start()


@bot.message_handler(commands=['id'])
def get_id(message):
    if message.reply_to_message:
        bot.reply_to(message,
                     f"🗣️ İstifadəçi ID nömrəsi - <code>{message.reply_to_message.from_user.id}</code>\n"
                     f"💁 Chat ID - <code>{message.chat.id}</code>")
    else:
        bot.reply_to(message,
                     f"🗣️ Sənin ID nömrən - <code>{message.from_user.id}</code>\n"
                     f"💁 Chat ID - <code>{message.chat.id}</code>")

# ========================== /admins
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
            bot.reply_to(message,
                         f"💁 {message.chat.title} Qrupundakı adminlər 🥷\n\n{admin_list}")
        else:
            bot.reply_to(message, "❌ Qrupda insan admin tapılmadı.")
    else:
        bot.reply_to(message, "Bu əmri yalnız qrupda istifadə edə bilərsiniz!")


@bot.message_handler(commands=['info'])
def user_info(message):
    chat_id = message.chat.id
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    try:
        member = bot.get_chat_member(chat_id, user.id)
        banned_status = "Bəli" if member.status in ["kicked", "restricted"] else "Xeyr"
    except:
        banned_status = "Naməlum"

    baku_tz = pytz.timezone("Asia/Baku")
    now = datetime.now(baku_tz)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    photos = bot.get_user_profile_photos(user.id, limit=1)
    if photos.total_count > 0:
        file_id = photos.photos[0][-1].file_id
        bot.send_photo(
            chat_id,
            file_id,
            caption=f"💁 İstifadəçi: {user.first_name}\n"
                    f"🗣️ ID: {user.id}\n"
                    f"🏡 Chat: {message.chat.title}\n"
                    f"⏰ Time: {current_time}\n"
                    f"⛔ Qadağan: {banned_status}"
        )
    else:
        bot.send_message(
            chat_id,
            f"💁 İstifadəçi: {user.first_name}\n"
            f"🗣️ ID: {user.id}\n"
            f"🏡 Chat: {message.chat.title}\n"
            f"⏰ Time: {current_time}\n"
            f"⛔ Qadağan: {banned_status}"
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = call.from_user

    if call.data == "commands":
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("◀️ Geri", callback_data="back"))
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=f"👀 Salam {user.first_name}\n\n🙋 Mən Azərbaycan 🇦🇿 dil dəstəkli Söyüşləri silə bilən botam 🛡️\n"
                    f"Mənim funksiyalarım aşağıdakılardır 💁\n\n"
                    f"/id - istifadəçinin ID nömrəsini göstərir 🛠️\n"
                    f"/admins - adminlərin siyahısını göstərir 🥷\n"
                    f"/info - istifadəçi haqqında məlumat göstərir 📝",
            reply_markup=kb
        )

    elif call.data == "back":
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(
                config.START_IMAGE,
                caption=f"🙋 Salam {user.first_name}\n🇦🇿 Mən Azərbaycan dil dəstəkli botam\n🛡️ Qrupunuza əlavə edərək söyüşlü cümlələrdən azad ola bilərsiniz"
            ),
            reply_markup=get_main_keyboard()
        )


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

    if any(word.lower() in text for word in bad_words) or any(word.lower() in caption for word in bad_words):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(
                message.chat.id,
                f"🛡️ {message.from_user.first_name}, qrupumuzda söyüş daxili cümlələr və etik verici kəlmələr işlətmək qadağandır ⛔"
            )
            bot.send_message(
                config.LOG_CHANNEL,
                f"💁 Söyüş (argo) daxili mesaj silindi 🗑️\n"
                f"👤 Adı: {message.from_user.first_name}\n"
                f"🏡 Qrup: {message.chat.title}\n"
                f"👁️ Mesaj: {text or caption}"
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "message can't be deleted" in str(e):
                bot.send_message(
                    message.chat.id,
                    "🗣️ Görünür ki, mesajları silmək səlahiyyətlərim yoxdur. "
                    "Səlahiyyətlərimi artırmağı düşün. Təşəkkürlər!🙋"
                )
            else:
                print(e)


print("Bot işə düşdü...")
bot.infinity_polling()

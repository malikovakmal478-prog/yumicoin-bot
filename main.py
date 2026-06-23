import telebot
import json
import os
from datetime import date, datetime, timedelta

TOKEN = "8127924861:AAE1hR4heMcsYm3cbCs-tfmpp1p0k7MNGMk"
ADMIN_ID = 123456789  # @8127924861
KANAL = "@arzon_almazbor"

bot = telebot.TeleBot(TOKEN)
users = {}
auksion = {
    "faol": False,
    "mahsulot": "",
    "ishtirokchilar": {},
    "tugash": ""
}

def saqlash():
    with open("users.json", "w") as f:
        json.dump(users, f)

def yuklash():
    global users
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)

yuklash()

def profil(uid):
    if str(uid) not in users:
        users[str(uid)] = {
            "almaz": 0,
            "coin": 0,
            "referal": 0,
            "bonus_kun": "",
            "vazifa_bajarildi": False
        }
        saqlash()

def obuna_tekshir(uid):
    try:
        a = bot.get_chat_member(KANAL, uid)
        return a.status in ["member", "administrator", "creator"]
    except:
        return False

def bosh_menyu():
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("💎 Balans", "🎁 Kunlik bonus")
    m.row("👥 Referal", "✅ Vazifalar")
    m.row("🎰 Auktsion", "📊 Reyting")
    m.row("ℹ️ Ma'lumot")
    return m

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    profil(uid)
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(uid) and str(ref_id) in users:
            if not users[str(uid)].get("ref_olindi"):
                users[str(ref_id)]["almaz"] += 3
                users[str(ref_id)]["referal"] += 1
                users[str(uid)]["ref_olindi"] = True
                saqlash()
                try:
                    bot.send_message(int(ref_id), "🎉 Yangi do'st! +3 💎")
                except:
                    pass
    if not obuna_tekshir(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            "📢 Kanalga obuna", url="https://t.me/arzon_almazbor"))
        markup.add(telebot.types.InlineKeyboardButton(
            "✅ Tekshirish", callback_data="obuna_tekshir"))
        bot.send_message(uid,
            "👋 Xush kelibsiz!\n\n"
            "⚠️ Avval kanalga obuna bo'ling!\n"
            "📢 @arzon_almazbor", reply_markup=markup)
        return
    bot.send_message(uid,
        f"👋 Xush kelibsiz, {message.from_user.first_name}!\n\n"
        f"💎 Almaz: {users[str(uid)]['almaz']}\n"
        f"🪙 Coin: {users[str(uid)]['coin']}",
        reply_markup=bosh_menyu())

@bot.callback_query_handler(func=lambda c: c.data == "obuna_tekshir")
def obuna_callback(call):
    uid = call.from_user.id
    profil(uid)
    if obuna_tekshir(uid):
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
        bot.send_message(uid,
            f"✅ Xush kelibsiz, {call.from_user.first_name}!\n"
            f"💎 Almaz: {users[str(uid)]['almaz']}",
            reply_markup=bosh_menyu())
    else:
        bot.answer_callback_query(call.id, "❌ Avval obuna bo'ling!")

@bot.message_handler(func=lambda m: m.text == "💎 Balans")
def balans(message):
    uid = str(message.from_user.id)
    profil(message.from_user.id)
    bot.send_message(message.chat.id,
        f"💰 Hisobingiz:\n\n"
        f"💎 Almaz: {users[uid]['almaz']}\n"
        f"🪙 Coin: {users[uid]['coin']}\n"
        f"👥 Referallar: {users[uid]['referal']}")

@bot.message_handler(func=lambda m: m.text == "🎁 Kunlik bonus")
def kunlik_bonus(message):
    uid = str(message.from_user.id)
    profil(message.from_user.id)
    bugun = str(date.today())
    if users[uid]["bonus_kun"] == bugun:
        bot.send_message(message.chat.id,
            "⏰ Bugun bonus oldingiz!\nErtaga keling! 😊")
    else:
        users[uid]["almaz"] += 5
        users[uid]["bonus_kun"] = bugun
        saqlash()
        bot.send_message(message.chat.id,
            f"🎁 +5 💎 Kunlik bonus!\n"
            f"Jami: {users[uid]['almaz']} 💎")

@bot.message_handler(func=lambda m: m.text == "👥 Referal")
def referal(message):
    uid = message.from_user.id
    profil(uid)
    havola = f"https://t.me/Yumicoin_bot_bot?start={uid}"
    bot.send_message(message.chat.id,
        f"👥 Referal:\n\n"
        f"Har do'st uchun: +3 💎\n"
        f"Referallaringiz: {users[str(uid)]['referal']}\n\n"
        f"🔗 Havola:\n{havola}")

@bot.message_handler(func=lambda m: m.text == "✅ Vazifalar")
def vazifalar(message):
    uid = message.from_user.id
    profil(uid)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        "📢 Kanalga obuna +3 💎", url="https://t.me/arzon_almazbor"))
    markup.add(telebot.types.InlineKeyboardButton(
        "✅ Tekshirish", callback_data="vazifa_tekshir"))
    bot.send_message(message.chat.id,
        "✅ Vazifalar:\n\nObuna bo'ling +3 💎 oling!",
        reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "vazifa_tekshir")
def vazifa_tekshir(call):
    uid = call.from_user.id
    profil(uid)
    if obuna_tekshir(uid):
        if users[str(uid)].get("vazifa_bajarildi"):
            bot.answer_callback_query(call.id, "✅ Allaqachon oldingiz!")
        else:
            users[str(uid)]["almaz"] += 3
            users[str(uid)]["vazifa_bajarildi"] = True
            saqlash()
            bot.answer_callback_query(call.id, "✅ +3 💎!")
            bot.send_message(uid,
                f"✅ +3 💎 Oldingiz!\n"
                f"Jami: {users[str(uid)]['almaz']} 💎")
    else:
        bot.answer_callback_query(call.id, "❌ Avval obuna bo'ling!")

@bot.message_handler(func=lambda m: m.text == "🎰 Auktsion")
def auksion_kor(message):
    if not auksion["faol"]:
        bot.send_message(message.chat.id,
            "🎰 Hozircha faol auktsion yo'q!\nKuting... 😊")
        return
    eng_kop = max(auksion["ishtirokchilar"].values()) if auksion["ishtirokchilar"] else 0
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        "💎 Tikish", callback_data="auks_tikla"))
    bot.send_message(message.chat.id,
        f"🎰 Faol Auktsion!\n\n"
        f"🎁 Mahsulot: {auksion['mahsulot']}\n"
        f"💎 Eng yuqori: {eng_kop}\n"
        f"👥 Ishtirokchilar: {len(auksion['ishtirokchilar'])}\n"
        f"⏰ Tugaydi: {auksion['tugash']}",
        reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "auks_tikla")
def auks_tikla_callback(call):
    uid = str(call.from_user.id)
    profil(call.from_user.id)
    eng_kop = max(auksion["ishtirokchilar"].values()) if auksion["ishtirokchilar"] else 0
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        f"💎 Necha almaz tikasiz?\n"
        f"Sizda: {users[uid]['almaz']} 💎\n"
        f"Eng yuqori: {eng_kop} 💎\n\n"
        f"Raqam yozing:")
    bot.register_next_step_handler(msg, auks_tikla_son, uid)

def auks_tikla_son(message, uid):
    try:
        miqdor = int(message.text)
        if miqdor <= 0:
            bot.send_message(message.chat.id, "❌ Noto'g'ri!")
            return
        if users[uid]["almaz"] < miqdor:
            bot.send_message(message.chat.id, "❌ Almaz yetarli emas!")
            return
        eng_kop = max(auksion["ishtirokchilar"].values()) if auksion["ishtirokchilar"] else 0
        if miqdor <= eng_kop:
            bot.send_message(message.chat.id,
                f"❌ {eng_kop} dan ko'p bo'lishi kerak!")
            return
        if uid in auksion["ishtirokchilar"]:
            users[uid]["almaz"] += auksion["ishtirokchilar"][uid]
        auksion["ishtirokchilar"][uid] = miqdor
        users[uid]["almaz"] -= miqdor
        saqlash()
        bot.send_message(message.chat.id,
            f"✅ Tiklandingiz!\n"
            f"💎 Tiklov: {miqdor}\n"
            f"Qoldi: {users[uid]['almaz']} 💎")
    except:
        bot.send_message(message.chat.id, "❌ Faqat raqam!")

@bot.message_handler(commands=['auks_boshlat'])
def auks_boshlat(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "Mahsulot nomini yozing:")
    bot.register_next_step_handler(msg, auks_mahsulot)

def auks_mahsulot(message):
    auksion["mahsulot"] = message.text
    msg = bot.send_message(message.chat.id, "Necha soat davom etadi?")
    bot.register_next_step_handler(msg, auks_vaqt)

def auks_vaqt(message):
    try:
        soat = int(message.text)
        tugash = datetime.now() + timedelta(hours=soat)
        auksion["tugash"] = tugash.strftime("%H:%M")
        auksion["faol"] = True
        auksion["ishtirokchilar"] = {}
        bot.send_message(message.chat.id,
            f"✅ Auktsion boshlandi!\n"
            f"🎁 {auksion['mahsulot']}\n"
            f"⏰ {soat} soat")
    except:
        bot.send_message(message.chat.id, "❌ Raqam yozing!")

@bot.message_handler(commands=['auks_tugat'])
def auks_tugat(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not auksion["ishtirokchilar"]:
        auksion["faol"] = False
        bot.send_message(message.chat.id, "❌ Ishtirokchi yo'q!")
        return
    glib_id = max(auksion["ishtirokchilar"], key=auksion["ishtirokchilar"].get)
    glib_miqd = auksion["ishtirokchilar"][glib_id]
    auksion["faol"] = False
    bot.send_message(message.chat.id,
        f"🏆 Auktsion tugadi!\n"
        f"G'olib ID: {glib_id}\n"
        f"💎 Tiklov: {glib_miqd}")
    try:
        bot.send_message(int(glib_id),
            f"🎉 Tabriklaymiz! Yutdingiz!\n"
            f"🎁 {auksion['mahsulot']}")
    except:
        pass

@bot.message_handler(func=lambda m: m.text == "📊 Reyting")
def reyting(message):
    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1].get("almaz", 0),
        reverse=True)[:10]
    text = "🏆 Top 10:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. {data.get('almaz', 0)} 💎\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Ma'lumot")
def malumot(message):
    bot.send_message(message.chat.id,
        "ℹ️ Bot haqida:\n\n"
        "💎 Almaz yig'ing\n"
        "👥 Do'st taklif qiling +3 💎\n"
        "🎁 Kunlik bonus +5 💎\n"
        "🎰 Auktsion o'ynang\n\n"
        "📢 @arzon_almazbor")

print("✅ Bot ishga tushdi!")
bot.polling(none_stop=True)

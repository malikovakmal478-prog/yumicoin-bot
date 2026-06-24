from flask import Flask
import threading
import telebot
import json
import os
from datetime import date, datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

TOKEN = "8915795946:AAFmSilXgG9ucarv6tmHCoMaHhbWkTMA98k"
ADMIN_ID = 7849637859
KANAL = "@arzon_almazbor"

bot = telebot.TeleBot(TOKEN)
users = {}
auksion = {"faol": False, "mahsulot": "", "ishtirokchilar": {}, "tugash": ""}
bozor_lots = {}

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
        users[str(uid)] = {"almaz": 0, "coin": 0, "referal": 0, "bonus_kun": "", "vazifa_bajarildi": False}
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
    m.row("💸 Almaz yuborish", "🛒 Bozor")
    m.row("💳 Pul kiritish", "ℹ️ Ma'lumot")
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
        markup.add(telebot.types.InlineKeyboardButton("📢 Kanalga obuna", url="https://t.me/arzon_almazbor"))
        markup.add(telebot.types.InlineKeyboardButton("✅ Tekshirish", callback_data="obuna_tekshir"))
        bot.send_message(uid, "👋 Xush kelibsiz!\n\n⚠️ Avval kanalga obuna bo'ling!\n📢 @arzon_almazbor", reply_markup=markup)
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
        bot.send_message(uid, f"✅ Xush kelibsiz!\n💎 Almaz: {users[str(uid)]['almaz']}", reply_markup=bosh_menyu())
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
        bot.send_message(message.chat.id, "⏰ Bugun bonus oldingiz!\nErtaga keling!")
    else:
        users[uid]["almaz"] += 5
        users[uid]["bonus_kun"] = bugun
        saqlash()
        bot.send_message(message.chat.id, f"🎁 +5 💎 Kunlik bonus!\nJami: {users[uid]['almaz']} 💎")

@bot.message_handler(func=lambda m: m.text == "👥 Referal")
def referal(message):
    uid = message.from_user.id
    profil(uid)
    havola = f"https://t.me/Yumicoin_bot_bot?start={uid}"
    bot.send_message(message.chat.id,
        f"👥 Referal:\n\nHar do'st uchun: +3 💎\n"
        f"Referallaringiz: {users[str(uid)]['referal']}\n\n"
        f"🔗 Havola:\n{havola}")

@bot.message_handler(func=lambda m: m.text == "✅ Vazifalar")
def vazifalar(message):
    uid = message.from_user.id
    profil(uid)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 Kanalga obuna +3 💎", url="https://t.me/arzon_almazbor"))
    markup.add(telebot.types.InlineKeyboardButton("✅ Tekshirish", callback_data="vazifa_tekshir"))
    bot.send_message(message.chat.id, "✅ Vazifalar:\n\nObuna bo'ling +3 💎 oling!", reply_markup=markup)

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
            bot.send_message(uid, f"✅ +3 💎 Oldingiz!\nJami: {users[str(uid)]['almaz']} 💎")
    else:
        bot.answer_callback_query(call.id, "❌ Avval obuna bo'ling!")

@bot.message_handler(func=lambda m: m.text == "💸 Almaz yuborish")
def almaz_yuborish(message):
    uid = str(message.from_user.id)
    profil(message.from_user.id)
    msg = bot.send_message(message.chat.id,
        f"💸 Almaz yuborish\n\nSizda: {users[uid]['almaz']} 💎\n\nQabul qiluvchining ID sini yozing:")
    bot.register_next_step_handler(msg, almaz_yuborish_id, uid)

def almaz_yuborish_id(message, yuboruvchi):
    try:
        qabul_id = str(int(message.text))
        if qabul_id not in users:
            bot.send_message(message.chat.id, "❌ Bu foydalanuvchi botda yo'q!")
            return
        if qabul_id == yuboruvchi:
            bot.send_message(message.chat.id, "❌ O'zingizga yubora olmaysiz!")
            return
        msg = bot.send_message(message.chat.id, f"Necha almaz?\nSizda: {users[yuboruvchi]['almaz']} 💎")
        bot.register_next_step_handler(msg, almaz_yuborish_miqdor, yuboruvchi, qabul_id)
    except:
        bot.send_message(message.chat.id, "❌ Faqat raqam!")

def almaz_yuborish_miqdor(message, yuboruvchi, qabul_id):
    try:
        miqdor = int(message.text)
        if miqdor <= 0 or users[yuboruvchi]["almaz"] < miqdor:
            bot.send_message(message.chat.id, "❌ Yetarli almaz yo'q!")
            return
        users[yuboruvchi]["almaz"] -= miqdor
        users[qabul_id]["almaz"] += miqdor
        saqlash()
        bot.send_message(message.chat.id, f"✅ {miqdor} 💎 yuborildi!\nQoldi: {users[yuboruvchi]['almaz']} 💎")
        try:
            bot.send_message(int(qabul_id), f"🎁 Sizga {miqdor} 💎 almaz yuborildi!")
        except:
            pass
    except:
        bot.send_message(message.chat.id, "❌ Faqat raqam!")

@bot.message_handler(func=lambda m: m.text == "🛒 Bozor")
def bozor(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📋 Lotlarni ko'rish", callback_data="bozor_kor"))
    markup.add(telebot.types.InlineKeyboardButton("➕ Lot qo'yish", callback_data="bozor_qoy"))
    bot.send_message(message.chat.id, "🛒 Bozor\n\nAlmaz sotib oling yoki soting!", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "bozor_kor")
def bozor_kor(call):
    if not bozor_lots:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🛒 Hozircha lot yo'q!")
        return
    bot.answer_callback_query(call.id)
    text = "🛒 Mavjud lotlar:\n\n"
    markup = telebot.types.InlineKeyboardMarkup()
    for lot_id, lot in bozor_lots.items():
        text += f"#{lot_id} — {lot['miqdor']} 💎 = {lot['narx']} coin\n"
        markup.add(telebot.types.InlineKeyboardButton(f"#{lot_id} sotib olish", callback_data=f"sotib_ol_{lot_id}"))
    bot.send_message(call.message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "bozor_qoy")
def bozor_qoy(call):
    uid = str(call.from_user.id)
    profil(call.from_user.id)
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"Necha almaz sotmoqchisiz?\nSizda: {users[uid]['almaz']} 💎")
    bot.register_next_step_handler(msg, bozor_miqdor, uid)

def bozor_miqdor(message, uid):
    try:
        miqdor = int(message.text)
        if miqdor <= 0 or users[uid]["almaz"] < miqdor:
            bot.send_message(message.chat.id, "❌ Yetarli almaz yo'q!")
            return
        msg = bot.send_message(message.chat.id, "Narxini yozing (coin da):")
        bot.register_next_step_handler(msg, bozor_narx, uid, miqdor)
    except:
        bot.send_message(message.chat.id, "❌ Faqat raqam!")

def bozor_narx(message, uid, miqdor):
    try:
        narx = int(message.text)
        lot_id = str(len(bozor_lots) + 1)
        bozor_lots[lot_id] = {"egasi": uid, "miqdor": miqdor, "narx": narx}
        users[uid]["almaz"] -= miqdor
        saqlash()
        bot.send_message(message.chat.id, f"✅ Lot #{lot_id} qo'yildi!\n💎 {miqdor} almaz = {narx} coin")
    except:
        bot.send_message(message.chat.id, "❌ Faqat raqam!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("sotib_ol_"))
def sotib_ol(call):
    uid = str(call.from_user.id)
    profil(call.from_user.id)
    lot_id = call.data.replace("sotib_ol_", "")
    if lot_id not in bozor_lots:
        bot.answer_callback_query(call.id, "❌ Lot topilmadi!")
        return
    lot = bozor_lots[lot_id]
    if lot["egasi"] == uid:
        bot.answer_callback_query(call.id, "❌ O'z lotingizni sotib ololmaysiz!")
        return
    if users[uid]["coin"] < lot["narx"]:
        bot.answer_callback_query(call.id, "❌ Yetarli coin yo'q!")
        return
    users[uid]["coin"] -= lot["narx"]
    users[uid]["almaz"] += lot["miqdor"]
    users[lot["egasi"]]["coin"] += lot["narx"]
    del bozor_lots[lot_id]
    saqlash()
    bot.answer_callback_query(call.id, "✅ Sotib olindi!")
    bot.send_message(call.message.chat.id, f"✅ Sotib olindi!\n+{lot['miqdor']} 💎")

@bot.message_handler(func=lambda m: m.text == "💳 Pul kiritish")
def pul_kiritish(message):
    uid = str(message.from_user.id)
    bot.send_message(message.chat.id,
        f"💳 Pul kiritish\n\n"
        f"1000 so'm = 100 coin\n\n"
        f"Click: +998901234567\n"
        f"Payme: +998901234567\n\n"
        f"Pul o'tkazib, chekni @admin ga yuboring!\n"
        f"Sizning ID: {uid}")

@bot.message_handler(func=lambda m: m.text == "🎰 Auktsion")
def auksion_kor(message):
    if not auksion["faol"]:
        bot.send_message(message.chat.id, "🎰 Hozircha faol auktsion yo'q!")
        return
    eng_kop = max(auksion["ishtirokchilar"].values()) if auksion["ishtirokchilar"] else 0
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💎 Tikish", callback_data="auks_tikla"))
    bot.send_message(message.chat.id,
        f"🎰 Faol Auktsion!\n\n"
        f"🎁 {auksion['mahsulot']}\n"
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
        f"💎 Necha almaz tikasiz?\nSizda: {users[uid]['almaz']} 💎\nEng yuqori: {eng_kop} 💎\nRaqam yozing:")
    bot.register_next_step_handler(msg, auks_tikla_son, uid)

def auks_tikla_son(message, uid):
    try:
        miqdor = int(message.text)
        if miqdor <= 0 or users[uid]["almaz"] < miqdor:
            bot.send_message(message.chat.id, "❌ Yetarli almaz yo'q!")
            return
        eng_kop = max(auksion["ishtirokchilar"].values()) if auksion["ishtirokchilar"] else 0
        if miqdor <= eng_kop:
            bot.send_message(message.chat.id, f"❌ {eng_kop} dan ko'p bo'lishi kerak!")
            return
        if uid in auksion["ishtirokchilar"]:
            users[uid]["almaz"] += auksion["ishtirokchilar"][uid]
        auksion["ishtirokchilar"][uid] = miqdor
        users[uid]["almaz"] -= miqdor
        saqlash()
        bot.send_message(message.chat.id, f"✅ Tiklandingiz!\n💎 {miqdor}\nQoldi: {users[uid]['almaz']} 💎")
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
    msg = bot.send_message(message.chat.id, "Necha soat?")
    bot.register_next_step_handler(msg, auks_vaqt)

def auks_vaqt(message):
    try:
        soat = int(message.text)
        tugash = datetime.now() + timedelta(hours=soat)
        auksion["tugash"] = tugash.strftime("%H:%M")
        auksion["faol"] = True
        auksion["ishtirokchilar"] = {}
        bot.send_message(message.chat.id, f"✅ Auktsion boshlandi!\n🎁 {auksion['mahsulot']}\n⏰ {soat} soat")
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
    bot.send_message(message.chat.id, f"🏆 Tugadi!\nG'olib: {glib_id}\n💎 {glib_miqd}")
    try:
        bot.send_message(int(glib_id), f"🎉 Yutdingiz!\n🎁 {auksion['mahsulot']}")
    except:
        pass

@bot.message_handler(commands=['coin_ber'])
def coin_ber(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        uid = parts[1]
        miqdor = int(parts[2])
        profil(int(uid))
        users[uid]["coin"] += miqdor
        saqlash()
        bot.send_message(message.chat.id, f"✅ {uid} ga {miqdor} coin berildi!")
        bot.send_message(int(uid), f"✅ Hisobingizga {miqdor} coin qo'shildi!")
    except:
        bot.send_message(message.chat.id, "❌ Format: /coin_ber ID MIQDOR")

@bot.message_handler(func=lambda m: m.text == "📊 Reyting")
def reyting(message):
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("almaz", 0), reverse=True)[:10]
    text = "🏆 Top 10:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. {data.get('almaz', 0)} 💎\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Ma'lumot")
def malumot(message):
    bot.send_message(message.chat.id,
        "ℹ️ Bot haqida:\n\n"
        "💎 Almaz yig'ing\n"
        "👥 Do'st taklif +3 💎\n"
        "🎁 Kunlik bonus +5 💎\n"
        "🎰 Auktsion o'ynang\n"
        "💸 Almaz yuboring\n"
        "🛒 Bozorda soting\n"
        "💳 Pul kiritib coin oling\n\n"
        "📢 @arzon_almazbor")

print("✅ Bot ishga tushdi!")
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.polling(none_stop=True)

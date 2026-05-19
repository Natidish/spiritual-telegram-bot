import sqlite3
import os
import threading
import http.server
import socketserver
import datetime
from telegram import Update, ReplyKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Render ላይ BOT_TOKEN መኖሩን ያረጋግጣል
MY_TOKEN = os.getenv("BOT_TOKEN")

# የስድብ እና የባለጌ ቃላት ዝርዝር
BANNED_WORDS = [
    "ውሻ", "ደደብ", "ደንቆሮ", "ባለጌ", "ውሸታም", "ሰነፍ", "ሌባ", 
    "ሴክስ", "sex", "በዳ", "ብዳ", "ቂንጥር", "ቁላ", "ጡት", "እርቃን"
] 

# የዳታቤዝ ፋይል መንገድ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")

# --- የቅጣት ሰንጠረዥ በራስ-ሰር መፍጠሪያ ---
def init_warnings_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_warnings (
            user_id INTEGER PRIMARY KEY, 
            warn_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# --- Render ፖርት እንዳይዘጋ የውሸት ሰርቨር መክፈቻ ---
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"የRender ፖርት ማታለያ ሰርቨር በፖርት {port} ላይ ተከፍቷል...")
            httpd.serve_forever()
    except Exception as e:
        print(f"Fake Server Error: {e}")

# --- Database የትምህርት ፍለጋ ---
def get_doctrine_from_db(title):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        clean_title = title.strip()
        
        cursor.execute("SELECT content FROM doctrines WHERE title = ?", (clean_title,))
        result = cursor.fetchone()
        
        if not result:
            search_term = clean_title.replace("?", "").replace("*", "").replace("(", "").replace(")", "")
            cursor.execute("SELECT content FROM doctrines WHERE title LIKE ?", (f"%{search_term}%",))
            result = cursor.fetchone()
            
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Database Error: {e}")
        return None

# --- ተጠቃሚን የማስጠንቀቅ እና የመቅጣት ሲስተም (ከቻናል የሚመጡትን የሚጠብቅ) ---
async def add_warning_and_check(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    chat = update.effective_chat
    
    # ቦቱ በግሩፕ ውስጥ ካልሆነ ዝም ይላል
    if chat.type == "private":
        return

    # 1. መልዕክቱ ከታሰረ ቻናል (Linked Channel) በራስ-ሰር የመጣ ከሆነ ቦቱ በፍጹም አይንካው!
    if update.message.sender_chat and getattr(chat, 'linked_chat_id', None) and update.message.sender_chat.id == chat.linked_chat_id:
        return

    # 2. መልዕክቱ ከማንኛውም ቻናል Forward የተደረገ (is_automatic_forward) ከሆነም አይንካው
    if update.message.forward_from_chat or getattr(update.message, 'is_automatic_forward', False):
        return

    user = update.effective_user

    # 3. መልዕክቱ የመጣው ከግሩፑ አስተዳዳሪዎች (Admins) ከሆነ ቦቱ አይንካቸውም
    if user:
        try:
            member = await context.bot.get_chat_member(chat_id=chat.id, user_id=user.id)
            if member.status in ['administrator', 'creator']:
                return
        except Exception:
            pass
    else:
        # የአንዳንድ አውቶማቲክ መልዕክቶች ተጠቃሚ (user) ስለሌላቸው እንዳይጠፉ ዝም ይበል
        return

    # ከላይ ያሉትን ህጎች በሙሉ ካለፈ ተራ ተጠቃሚ ጥፋት አጥፍቷል ማለት ነው፤ መልዕክቱ ይጠፋል
    try:
        await update.message.delete()
    except Exception:
        pass

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT warn_count FROM user_warnings WHERE user_id = ?", (user.id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute("INSERT INTO user_warnings (user_id, warn_count) VALUES (?, 1)", (user.id,))
        warn_count = 1
    else:
        warn_count = row[0] + 1
        cursor.execute("UPDATE user_warnings SET warn_count = ? WHERE user_id = ?", (warn_count, user.id))
    
    conn.commit()
    conn.close()

    if warn_count >= 3:
        # ለ1 ሳምንት መቅጣት (Restrict/Mute)
        until_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
        try:
            await context.bot.restrict_chat_member(chat_id=chat.id, user_id=user.id, permissions=permissions, until_date=until_date)
            # የቅጣት ታሪኩን መልሰን 0 እናደርገዋለን
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE user_warnings SET warn_count = 0 WHERE user_id = ?", (user.id,))
            conn.commit()
            conn.close()
            await context.bot.send_message(chat_id=chat.id, text=f"🚨 <b>{user.first_name}</b> ህግ 3 ጊዜ በመጣሱ ምክንያት ለ 1 ሳምንት ከግሩፑ ታግዷል (Muted)!", parse_mode="HTML")
        except Exception as e:
            print(f"Banning Error: {e}")
    else:
        try:
            await context.bot.send_message(
                chat_id=chat.id, 
                text=f"⚠️ <b>{user.first_name}</b> {reason} ማውጣት ወይም መላክ የተከለከለ ነው!\n❌ <b>ማስጠንቀቂያ፦ {warn_count}/3</b> (3 ሲሞላ ለ1 ሳምንት ይታገዳሉ)", 
                parse_mode="HTML"
            )
        except Exception:
            pass

# --- አዲስ ሰው ሲገባ ሰላምታ መስጫ (Welcome) ---
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        welcome_text = (
            f"ሰላም {member.first_name} 👋 ወደ መንፈሳዊ ግሩፓችን በደህና መጡ! ቃለ ህይወትን ይማሩ።\n\n"
            "⚠️ <b>የግሩፑ ህግጋት፦</b>\n"
            "1. ስድብ እና ባለጌ ቃላት ፈጽሞ አይፈቀዱም።\n"
            "2. ማንኛውንም ሊንክ፣ እርቃን ፎቶ ወይም ቪዲዮ መላክ ክልክል ነው።\n"
            "👉 ህግ የሚጥስ 3 ጊዜ ከተገሰጸ በኋላ ለ1 ሳምንት ይታገዳል!"
        )
        await update.message.reply_text(welcome_text, parse_mode="HTML")

# --- ዋና ዋና Functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"ሰላም {user_name}! 👋\n\n"
        "ወደ መንፈሳዊ የእውቀት ቦት እንኳን ደህና መጡ። "
        "ከታች ያሉትን አማራጮች በመጫን መማር ትችላላችሁ。"
    )
    kb = [
        ['ስለ ሥላሴ*', 'ኢየሱስ ማነው?*'], 
        ['ድኅነት(መዳን)', 'ትንሣኤው'], 
        ['የሃይማኖት መግለጫዎች', 'ኢየሱስ አብ ነውን?'],
        ['የመጽሐፍ ቅዱስ ግጭቶች 1?', 'የመጽሐፍ ቅዱስ ግጭቶች 2?'],
        ['መልስ ለሰባልዮሳውያን'],
        ['ወንጌል ምድነው?']
    ]
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # --- Sub-menus ---
    if text == "ስለ ሥላሴ*":
        kb = [['እግዚአብሔር ያሕዌ!'], ['ኢየሱስ ያሕዌ', 'መንፈስ ቅዱስ ያሕዌ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("🔎 **ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "ኢየሱስ ማነው?*":
        kb = [['የኢየሱስ ሰውነቱ', 'የኢየሱስ አምላክነቱ'], ['መሲህ መሆኑ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("👑 **ስለ ጌታ ኢየሱስ ክርስቶስ ማንነት**\n\nኢየሱስ ክርስቶስ እውነተኛ አምላክና እውነተኛ ሰው ነው።",  reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "ኢየሱስ አብ ነውን?":
        kb = [['ክፍል አንድ 1'], ['ክፍል ሁለት 2'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("❓ **ኢየሱስ አብ ነውን?**\n\nእግዚአብሔር አብ ነው፣ ኢየሱስ ወልድ ነው፣ መንፈስ ቅዱስ ነው።", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "ድኅነት(መዳን)":
        kb = [['የደህንነትን ማረጋገጫ 1'], ['የደህንነትን ማረጋገጫ 2'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("🛡 **ድኅነት (መዳን)**\n\nድኅነት ማለት ከኃጢአት እና ከሞት የሚያዳን ጥምረት ነው።", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "የሃይማኖት መግለጫዎች":
        kb = [['የኒቅያ የሃይማኖት መግለጫ'], ['የአትናቴዎስ የሃይማኖት መግለጫ'], ['የሐዋርያት የእምነት መግለጫ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📚 **የሃይማኖት መግለጫዎች**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return 

    if text == "መልስ ለሰባልዮሳውያን":
        kb = [['ሰው የኾነው አምላክ'], ['ጌታችን ኢየሱስ “ከፍጥረት በፊት በኩር” ተብሎ መጠራቱ ምንን ያሳያል?'], ['ኢሳይያስ 9፥6 እና የኦንሊ ጂሰስ (Oneness) አስተምህሮ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **መልስ ለሰባልዮሳውያን**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "የመጽሐፍ ቅዱስ ግጭቶች 1?":
        kb = [['የይሁዳ አሟሟት እንዴት ነበር?'], ['ኢየሱስ አጥምቋል ወይንስ አላጠመቀም?'], ['እግዚአብሔር ሰዎችን ይፈትናል ወይስ አይፈትንም?'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **የመጽሐፍ ቅዱስ ግጭቶች 1**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return

    if text == "የመጽሐፍ ቅዱስ ግጭቶች 2?":
        kb = [['የእግዚአብሔር የበኵር ልጅ ማነው?'], ['ዳዊት የገደለው ሠራዊት ብዛት ስንት ነው?'], ['እግዚአብሔር ይጸጸታል ወይንስ አይጸጸትም?'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **የመጽሐፍ ቅዱስ ግጭቶች 2**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return

    if text == "ወንጌል ምድነው?":
        kb = [['ወንጌል ምድነው?'], ['ትንሣኤው'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **ስለ ወንጌል እና ትንሣኤ**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return
     
    # --- Database ፍለጋ ---
    content = get_doctrine_from_db(text)
    if content:
        await update.message.reply_text(content, parse_mode="Markdown")
    elif "ወደ ዋናው" in text:
        await start(update, context)
    else:
        # በግሩፕ ውስጥ ከሆነና ርዕስ ካልሆነ ዝም እንዲል (ስህተት እንዳይልክ)
        if update.effective_chat.type == "private":
            await update.message.reply_text(f"❌ '{text}' በሚል ርዕስ መረጃ አልተገኘም።")

# --- ፎቶ እና ቪዲዮ መከላከያ ---
async def filter_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_warning_and_check(update, context, "በዚህ ግሩፕ ውስጥ ፎቶ ወይም ቪዲዮ መላክ")

# --- የጽሑፍ፣ የስድብ እና የሊንክ ጥበቃ ---
async def content_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: 
        return
    
    text = update.message.text.lower()
    
    # 1. የሊንክ መከላከያ (Telegram link, http, https, .com)
    if "http://" in text or "https://" in text or "t.me/" in text or ".com" in text:
        await add_warning_and_check(update, context, "ማንኛውንም አይነት ሊንክ መላክ")
        return

    # 2. የስድብ እና የወሲብ ቃላት መከላከያ
    for word in BANNED_WORDS:
        if word in text:
            await add_warning_and_check(update, context, "የስድብ ወይም የብልግና ቃል")
            return
            
    # ሁሉም ነገር ሰላም ከሆነ መልዕክቱን ያስተናግዳል
    await handle_message(update, context)

if __name__ == '__main__':
    if not MY_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        # የቅጣት ዳታቤዝ ሰንጠረዥን ማስጀመር
        init_warnings_db()
        
        # Render ፖርት እንዳይዘጋ የጀርባ ሰርቨር ማስጀመር
        threading.Thread(target=run_fake_server, daemon=True).start()
        
        app = ApplicationBuilder().token(MY_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        # አዲስ ሰው ሲገባ መያዣ
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
        
        # ሚዲያ (ፎቶ፣ ቪዲዮ፣ ሰነድ) መከላከያ
        app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.ANIMATION, filter_media))
        
        # የጽሑፍ መቆጣጠሪያ
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), content_guard))
        
        print("ቦቱ ስራ ጀምሯል...")
        app.run_polling()

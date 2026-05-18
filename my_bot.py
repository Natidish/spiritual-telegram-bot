import sqlite3
import os
import threading
import http.server
import socketserver
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Render ላይ BOT_TOKEN መኖሩን ያረጋግጣል
MY_TOKEN = os.getenv("BOT_TOKEN")

# ስድቦችን መከላከያ
BANNED_WORDS = ["ውሻ", "ደደብ", "ደንቆሮ", "ባለጌ", "ውሸታም", "ሰነፍ", "ሌባ"] 

# የዳታቤዝ ፋይል መንገድ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")

# --- Render ፖርት እንዳይዘጋ የውሸት ሰርቨር መክፈቻ (በነፃ ለመጠቀም ወሳኝ ነው) ---
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"የRender ፖርት ማታለያ ሰርቨር በፖርት {port} ላይ ተከፍቷል...")
            httpd.serve_forever()
    except Exception as e:
        print(f"Fake Server Error: {e}")

# --- Database ስራዎች ---
def get_doctrine_from_db(title):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. ጽሑፉን ከባዶ ቦታዎች ማጽዳት
        clean_title = title.strip()
        
        # 2. በመጀመሪያ ቀጥታ ፍለጋ
        cursor.execute("SELECT content FROM doctrines WHERE title = ?", (clean_title,))
        result = cursor.fetchone()
        
        # 3. ካልተገኘ በከፊል ተመሳሳይነት (LIKE) መፈለግ
        if not result:
            # ምልክቶችን (እንደ ? ወይም *) አጥፍቶ መፈለግ
            search_term = clean_title.replace("?", "").replace("*", "").replace("(", "").replace(")", "")
            cursor.execute("SELECT content FROM doctrines WHERE title LIKE ?", (f"%{search_term}%",))
            result = cursor.fetchone()
            
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Database Error: {e}")
        return None

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
        # እዚህ ጋር ርዕሱን ከግጭቶች ወደ ወንጌል አስተካክዬዋለሁ
        await update.message.reply_text("📖 **ስለ ወንጌል እና ትንሣኤ**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return
     
    # --- Database ፍለጋ ---
    content = get_doctrine_from_db(text)
    if content:
        await update.message.reply_text(content, parse_mode="Markdown")
    elif "ወደ ዋናው" in text:
        await start(update, context)
    else:
        await update.message.reply_text(f"❌ '{text}' በሚል ርዕስ መረጃ አልተገኘም።")

async def filter_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
        await update.message.reply_text(f"⚠️ ምስል መላክ አይፈቀድም።")
    except Exception:
        pass

async def content_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    text = update.message.text.lower()
    for word in BANNED_WORDS:
        if word in text:
            try:
                await update.message.delete()
                await update.message.reply_text("❗️ ስድብ አይፈቀድም።")
            except Exception:
                pass
            return
    await handle_message(update, context)

if __name__ == '__main__':
    if not MY_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        # Render ፖርት ስካን እንዳይሰናከል ከጀርባ ሰርቨር ማስጀመር
        threading.Thread(target=run_fake_server, daemon=True).start()
        
        app = ApplicationBuilder().token(MY_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, filter_media))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), content_guard))
        print("ቦቱ ስራ ጀምሯል...")
        app.run_polling()

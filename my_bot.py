import sqlite3
import os
# from dotenv import load_dotenv  # Render ላይ አያስፈልግም
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# .env ፋይልን ይጭናል (Render ላይ በ Environment Variables ስለሚተካ እንዲህ እናድርገው)
# load_dotenv() 
MY_TOKEN = os.getenv("BOT_TOKEN")

# --- አዳዲስ መከላከያዎች ---
BANNED_WORDS = ["ውሻ", "ደደብ", "ደንቆሮ", "ባለጌ", "ውሸታም", "ሰነፍ", "ሌባ"] 

# የዳታቤዝ ፋይል መንገድ በቋሚነት እንዲገኝ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")

# --- Database ስራዎች ---
def get_doctrine_from_db(title):
    try:
        conn = sqlite3.connect(DB_PATH) # እዚህ ጋር DB_PATH ተጠቀምን
        cursor = conn.cursor()
        # ርዕሱን በትክክል እንዲያገኝ LIKE እና strip እንጠቀማለን
        search_term = f"%{title.strip()}%"
        cursor.execute("SELECT content FROM doctrines WHERE title LIKE ?", (search_term,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None

# --- ዋና ዋና Functions (እነዚህ አልተቀየሩም) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"ሰላም {user_name}! 👋\n\n"
        "ወደ መንፈሳዊ የእውቀት ቦት እንኳን ደህና መጡ። "
        "ከታች ያሉትን አማራጮች በመጫን መማር ትችላላችሁ።"
    )
    kb = [
        ['ስለ ሥላሴ', 'ኢየሱስ ማነው?'], 
        ['ድኅነት(መዳን)', 'ትንሣኤው'], 
        ['የሃይማኖት መግለጫዎች', 'ኢየሱስ አብ ነውን?'],
        ['የመጽሐፍ ቅዱስ ግጭቶች 1?', 'የመጽሐፍ ቅዱስ ግጭቶች 2?'],
        ['መልስ ለሰባልዮሳውያን']
    ]
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # ለተወሰኑ ርዕሶች Sub-menu ካለህ እዚህ ይቀጥላል
    if text == "ስለ ሥላሴ":
        kb = [['እግዚአብሔር ያሕዌ'], ['ኢየሱስ ያሕዌ', 'መንፈስ ቅዱስ ያሕዌ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("🔎 **ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    # ከ Database ፈልጎ ያመጣል
    content = get_doctrine_from_db(text)
    if content:
        await update.message.reply_text(content, parse_mode="Markdown")
    elif "ወደ ዋናው" in text:
        await start(update, context)
    else:
        await update.message.reply_text(f"❌ '{text}' በሚል ርዕስ መረጃ አልተገኘም።")

async def filter_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.message.reply_text(f"⚠️ ምስል መላክ አይፈቀድም።")

async def content_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for word in BANNED_WORDS:
        if word in text:
            await update.message.delete()
            await update.message.reply_text("❗️ ስድብ አይፈቀድም።")
            return
    await handle_message(update, context)

if __name__ == '__main__':
    if not MY_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(MY_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, filter_media))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), content_guard))
        print("ቦቱ ስራ ጀምሯል...")
        app.run_polling()

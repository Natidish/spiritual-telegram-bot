import sqlite3
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# .env ፋይልን ይጭናል
load_dotenv()
MY_TOKEN = os.getenv("BOT_TOKEN")

# --- አዳዲስ መከላከያዎች ---
BANNED_WORDS = ["ውሻ", "ደደብ", "ደንቆሮ", "ባለጌ", "ውሸታም", "ሰነፍ", "ሌባ"] 

async def filter_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.message.reply_text(f"⚠️ @{update.effective_user.username} በዚህ ቦት ውስጥ ምስል፣ ቪዲዮ ወይም ፋይል መላክ የተከለከለ ነው።")

async def content_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "http" in text or "t.me/" in text or "www." in text:
        await update.message.delete()
        await update.message.reply_text("🚫 ሊንክ መላክ የተከለከለ ነው!")
        return

    for word in BANNED_WORDS:
        if word in text:
            await update.message.delete()
            await update.message.reply_text("❗️ ህግ ጥሰሃል! ስድብ እና መጥፎ ቃላት አይፈቀዱም።")
            return

    await handle_message(update, context)

# --- Database ስራዎች ---
def get_doctrine_from_db(title):
    try:
        conn = sqlite3.connect('spiritual_bot.db')
        cursor = conn.cursor()
        clean_title = title.replace('!', '').replace('?', '').strip()
        cursor.execute("SELECT content FROM doctrines WHERE title LIKE ?", ('%' + clean_title + '%',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None

# --- ዋና ዋና Functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"ሰላም {user_name}! 👋\n\n"
        "ወደ መንፈሳዊ የእውቀት ቦት እንኳን ደህና መጡ። "
        "ስለ ክርስትና እምነት፣ ስለ መጽሐፍ ቅዱስ ወይንም ስለ መሠረታዊ ትምህርቶች **መንፈሳዊ ጥያቄ ካላችሁ** "
        "ከታች ያሉትን አማራጮች በመጫን መማር ትችላላችሁ።"
    )
    
    kb = [
        ['ስለ ሥላሴ', 'ኢየሱስ ማነው?'], 
        ['ድኅነት(መዳን)', 'ትንሣኤው'], # ትንሣኤው እዚህ ተጨምሯል
        ['የሃይማኖት መግለጫዎች', 'ኢየሱስ አብ ነውን?'],
        ['የመጽሐፍ ቅዱስ ግጭቶች 1?', 'የመጽሐፍ ቅዱስ ግጭቶች 2?'],
        ['መልስ ለሰባልዮሳውያን']
    ]
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == "ስለ ሥላሴ":
        kb = [['እግዚአብሔር ያሕዌ'], ['ኢየሱስ ያሕዌ', 'መንፈስ ቅዱስ ያሕዌ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("🔎 **ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ**\n\nእግዚአብሔር በአካል ሦስት (አብ፣ ወልድ፣ መንፈስ ቅዱስ) በመለኮት ደግሞ አንድ ነው።", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "ኢየሱስ ማነው?":
        kb = [['የኢየሱስ ሰውነቱ', 'የኢየሱስ አምላክነቱ'], ['መሲህ መሆኑ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("👑 **ስለ ጌታ ኢየሱስ ክርስቶስ ማንነት**\n\nኢየሱስ ክርስቶስ እውነተኛ አምላክና እውነተኛ ሰው ነው።", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return
    
    if text == "ኢየሱስ አብ ነውን?":
        kb = [['ክፍል አንድ 1'], ['ክፍል ሁለት 2'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("❓ **ኢየሱስ አብ ነውን?**\n\nእግዚአብሔር አብ ነው፣ ኢየሱስ ወልድ ነው፣ መንፈስ ቅዱስ ነው።", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return
    
    if text == "ድኅነት(መዳን)":
        kb = [['የደህንነትን ማረጋገጫ 1'], ['የደህንነትን ማረጋገጫ 2'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("🛡️ **ድኅነት (መዳን)**\n\nድኅነት ማለት ከኃጢአት እና ከሞት የሚያዳን ጥምረት ነው።", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return

    if text == "የሃይማኖት መግለጫዎች":
        kb = [['የኒቅያ የሃይማኖት መግለጫ'], ['የአትናቴዎስ የሃይማኖት መግለጫ'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📚 **የሃይማኖት መግለጫዎች**\n\n", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        return
    
    if text == "መልስ ለሰባልዮሳውያን":
        kb = [['ሰው የኾነው አምላክ' ], ['ጌታችን ኢየሱስ “ከፍጥረት በፊት በኩር” ተብሎ መጠራቱ ምንን ያሳያል?'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **መልስ ለሰባልዮሳውያን**\n\n", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")
        
        return
    
    if text == "የመጽሐፍ ቅዱስ ግጭቶች 1?":
        kb = [['የይሁዳ አሟሟት እንዴት ነበር?'], ['ኢየሱስ አጥምቋል ወይንስ አላጠመቀም?'], ['እግዚአብሔር ሰዎችን ይፈትናል ወይንስ አይፈትንም?'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **የመጽሐፍ ቅዱስ ግጭቶች**\n\n", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return
    

    if text == "የመጽሐፍ ቅዱስ ግጭቶች 2?":
        kb = [['የእግዚአብሔር የበኵር ልጅ ማነው?'], ['ዳዊት የገደለው ሠራዊት ብዛት ስንት ነው?'], ['እግዚአብሔር ይጸጸታል ወይንስ አይጸጸትም?'], ['🏠 ወደ ዋናው ዝርዝር ተመለስ']]
        await update.message.reply_text("📖 **የመጽሐፍ ቅዱስ ግጭቶች**\n\n", 
                                       reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")  
        return

    
    if text == "ትንሣኤው":
        resurrection_text = (
            "🌅 **የጌታችን የኢየሱስ ክርስቶስ ትንሣኤ**\n\n"
            "ትንሣኤ የክርስትና እምነት መሠረት ነው። (1 ቆሮ 15:14)\n\n"
            "• **የድል አዋጅ፦** ሞትን ድል አድርጎ ተነስቷል።\n"
            "• **የእኛ ተስፋ፦** በእርሱ የሚያምኑ ሁሉ የዘላለም ሕይወት ይኖራቸዋል።\n"
            "• **ታሪካዊ እውነት፦** መቃብሩ ባዶ መሆኑ ትንሣኤው እውነት መሆኑን ያረጋግጣል።"

        )
        await update.message.reply_text(resurrection_text, parse_mode="Markdown")
        return

    if "ወደ ዋናው" in text:
        await start(update, context)
        return

    # ከ Database ፈልጎ ያመጣል
    content = get_doctrine_from_db(text)
    if content:
        await update.message.reply_text(content, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ '{text}' በሚል ርዕስ በዳታቤዙ ውስጥ መረጃ አልተገኘም።")

if __name__ == '__main__':
    app = ApplicationBuilder().token().build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, filter_media))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), content_guard))
    
    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()
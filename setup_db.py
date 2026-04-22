import sqlite3
import os

def setup():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS doctrines")
    cursor.execute('''CREATE TABLE doctrines (title TEXT PRIMARY KEY, content TEXT)''')

    data = [
        ("ኢየሱስ ማነው?*", "👑 ጌታ ኢየሱስ ክርስቶስ ማነው?..."),
        ("ስለ ሥላሴ ", "🙏 ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ..."),
        ("ድኅነት(መዳን)", "🛡️ ድኅነት (መዳን) ማብራሪያ..."),
        ("የኢየሱስ አምላክነቱ", "📖 የኢየሱስ አምላክነቱ ጥቅሶች..."),
        ("የኢየሱስ ሰውነቱ", "👤 የኢየሱስ ሰውነቱ ማብራሪያ..."),
        ("መሲህ መሆኑ", "📜 መሲህ መሆኑን የሚያሳዩ ትንቢቶች..."),
        ("የእግዚአብሔር የበኵር ልጅ ማነው?", "📖 ስለ በኩርነት ማብራሪያ..."),
        ("የመጽሐፍ ቅዱስ ግጭቶች 1?"), ("የመጽሐፍ ቅዱስ ግጭቶች 2?"), 
        # ... ሌሎችንም እስከ 33 ድረስ እዚህ ጋር ጨምር ...
        ("ትንሣኤው", "🌅 የጌታችን የኢየሱስ ክርስቶስ ትንሣኤ..."),
        ("መልስ ለሰባልዮሳውያን"),
        ("ኢየሱስ አብ ነውን?") 
    ]

    # ከዚህ በታች ያለው መስመር በትክክል ከአራተኛው ፊደል (Indentation) ጀምሮ መጻፉን አረጋግጥ
    cursor.executemany("INSERT INTO doctrines VALUES (?, ?)", data)
    conn.commit()
    conn.close()
    print("ዳታቤዙ በአዲስ መረጃ ተሞልቷል!")

if __name__ == "__main__":
    setup()

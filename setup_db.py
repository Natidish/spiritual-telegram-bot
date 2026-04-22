import sqlite3
import os

def setup():
    # በ Render ላይ ፋይሉ እንዲገኝ ትክክለኛውን ቦታ መፈለጊያ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ሰንጠረዡን መፍጠር (ካለ አጥፍቶ በአዲስ ይተካዋል)
    cursor.execute("DROP TABLE IF EXISTS doctrines")
    cursor.execute('''CREATE TABLE doctrines (title TEXT PRIMARY KEY, content TEXT)''')

    # እያንዳንዱ መረጃ (ርዕስ, ይዘት) መሆኑን አረጋግጥ
    data = [
        ("ኢየሱስ ማነው?*", "👑 ጌታ ኢየሱስ ክርስቶስ ማነው?..."),
        ("ስለ ሥላሴ ", "🙏 ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ..."),
        ("ድኅነት(መዳን)", "🛡️ ድኅነት (መዳን) ማብራሪያ..."),
        ("የኢየሱስ አምላክነቱ", "📖 የኢየሱስ አምላክነቱ ጥቅሶች..."),
        ("የኢየሱስ ሰውነቱ", "👤 የኢየሱስ ሰውነቱ ማብራሪያ..."),
        ("መሲህ መሆኑ", "📜 መሲህ መሆኑን የሚያሳዩ ትንቢቶች..."),
        ("የእግዚአብሔር የበኵር ልጅ ማነው?", "📖 ስለ በኩርነት ማብራሪያ..."),
        ("የመጽሐፍ ቅዱስ ግጭቶች 1?", "ስለ መጽሐፍ ቅዱስ ግጭቶች ክፍል 1 ዝርዝር መረጃ እዚህ ይገባል።"), 
        ("የመጽሐፍ ቅዱስ ግጭቶች 2?", "ስለ መጽሐፍ ቅዱስ ግጭቶች ክፍል 2 ዝርዝር መረጃ እዚህ ይገባል።"), 
        ("ትንሣኤው", "🌅 የጌታችን የኢየሱስ ክርስቶስ ትንሣኤ..."),
        ("መልስ ለሰባልዮሳውያን", "ለሰባልዮሳውያን የተሰጠ መልስ ማብራሪያ እዚህ ይገባል።"),
        ("ኢየሱስ አብ ነውን?", "ኢየሱስ አብ ነውን? ለሚለው ጥያቄ መልስ እዚህ ይገባል።")
    ]

    # ዳታውን ማስገባት
    cursor.executemany("INSERT INTO doctrines VALUES (?, ?)", data)
    conn.commit()
    conn.close()
    print(f"ዳታቤዙ በ {len(data)} መረጃዎች በአዲስ ተሞልቷል!")

if __name__ == "__main__":
    setup()

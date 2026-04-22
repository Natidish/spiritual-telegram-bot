import sqlite3
import os

def setup():
    # በ Render ላይ ፋይሉ እንዲገኝ ትክክለኛውን ቦታ መፈለጊያ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ሰንጠረዡን መፍጠር
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctrines (
            title TEXT PRIMARY KEY,
            content TEXT
        )
    ''')

    # እዚህ ጋር ሁሉንም 33 መረጃዎች አንድ በአንድ አስገባቸው
    # (ርዕሱ በ DB Browser ላይ ካለው ጋር አንድ አይነት መሆኑን አረጋግጥ)
    data = [
        ("ኢየሱስ ማነው?", "👑 ጌታ ኢየሱስ ክርስቶስ ማነው?..."),
        ("ስለ ሥላሴ", "🙏 ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ..."),
        ("ድኅነት (መዳን)", "🛡️ ድኅነት (መዳን) ማብራሪያ..."),
        ("የኢየሱስ አምላክነቱ", "📖 የኢየሱስ አምላክነቱ ጥቅሶች..."),
        ("የኢየሱስ ሰውነቱ", "👤 የኢየሱስ ሰውነቱ ማብራሪያ..."),
        ("መሲህ መሆኑ", "📜 መሲህ መሆኑን የሚያሳዩ ትንቢቶች..."),
        ("የእግዚአብሔር የበኵር ልጅ ማነው?", "📖 ስለ በኩርነት ማብራሪያ..."),
        # ... ሌሎችንም እስከ 33 ድረስ እዚህ ጋር ጨምር ...
        ("ትንሣኤው", "🌅 የጌታችን የኢየሱስ ክርስቶስ ትንሣኤ...")
    ]

    # መረጃውን ወደ ሰርቨሩ ዳታቤዝ ማስገባት
    cursor.executemany("INSERT OR REPLACE INTO doctrines VALUES (?, ?)", data)
    
    conn.commit()
    conn.close()
    print(f"በተሳካ ሁኔታ {len(data)} መረጃዎች ወደ ዳታቤዝ ገብተዋል!")

if __name__ == "__main__":
    setup()

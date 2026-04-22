import os

def setup():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "spiritual_bot.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS doctrines") # አሮጌውን ዳታ አጥፍቶ በአዲስ እንዲተካ
    cursor.execute('''CREATE TABLE doctrines (title TEXT PRIMARY KEY, content TEXT)''')

    # እዚህ ጋር ሁሉንም 33 መረጃዎች አንድ በአንድ አስገባቸው
    # (ርዕሱ በ DB Browser ላይ ካለው ጋር አንድ አይነት መሆኑን አረጋግጥ)
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

    # መረጃውን ወደ ሰርቨሩ ዳታቤዝ ማስገባት
  cursor.executemany("INSERT INTO doctrines VALUES (?, ?)", data)
    conn.commit()
    conn.close()
    print("ዳታቤዙ በአዲስ መረጃ ተሞልቷል!")

if __name__ == "__main__":
    setup()

if __name__ == "__main__":
    setup()

import sqlite3

def setup():
    # 1. መጀመሪያ ግንኙነቱን መፍጠር
    conn = sqlite3.connect('spiritual_bot.db')
    # 2. ከዚያ cursor መፍጠር (ይህ ነው ስህተት ያመጣብህ)
    cursor = conn.cursor()

    # ሰንጠረዥ መፍጠር
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctrines (
            title TEXT PRIMARY KEY,
            content TEXT
        )
    ''')

    # ዳታው ዝርዝር (List of Tuples) መሆኑን እርግጠኛ ሁን
    # በየመሃሉ ኮማ (,) መኖሩን አስተውል
    data = [
        ("ኢየሱስ ማነው?", "👑 ጌታ ኢየሱስ ክርስቶስ ማነው?\n\nኢየሱስ ክርስቶስ የክርስትና እምነት ማዕከልና ብቸኛው አዳኝ ነው።"),
        ("ስለ ሥላሴ", "🙏 ስለ ቅድስት ሥላሴ ዝርዝር ማብራሪያ\n\nመጽሐፍ ቅዱስ እግዚአብሔር 'አንድ' መሆኑን ያስተምራል።"),
        ("ትንሣኤው", "🌅 የጌታችን የኢየሱስ ክርስቶስ ትንሣኤ\n\nትንሣኤ የክርስትና እምነት መሠረት ነው።")
    ]

    # ዳታውን ወደ database ማስገባት
    cursor.executemany("INSERT OR REPLACE INTO doctrines VALUES (?, ?)", data)
    
    conn.commit()
    conn.close()
    print("ዳታቤዙ በተሳካ ሁኔታ ተፈጥሮ ዳታ ተሞልቷል!")

if __name__ == "__main__":
    setup()
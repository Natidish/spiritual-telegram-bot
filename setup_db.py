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
    data = [['ስለ ሥላሴ', 'ኢየሱስ ማነው?'], 
        ['ድኅነት(መዳን)', 'ትንሣኤው'], # ትንሣኤው እዚህ ተጨምሯል
        ['የሃይማኖት መግለጫዎች', 'ኢየሱስ አብ ነውን?'],
        ['የመጽሐፍ ቅዱስ ግጭቶች 1?', 'የመጽሐፍ ቅዱስ ግጭቶች 2?'],
        ['መልስ ለሰባልዮሳውያን']
    ]

    # ዳታውን ወደ database ማስገባት
    cursor.executemany("INSERT OR REPLACE INTO doctrines VALUES (?, ?)", data)
    
    conn.commit()
    conn.close()
    print("ዳታቤዙ በተሳካ ሁኔታ ተፈጥሮ ዳታ ተሞልቷል!")

if __name__ == "__main__":
    setup()

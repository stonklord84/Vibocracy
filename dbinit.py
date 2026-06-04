import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'appdata', 'data.db')

conn = sqlite3.connect(DB_DIR)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chatrooms(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               room_name TEXT NOT NULL,
               vibe_rule TEXT NOT NULL,
               owner_id INTEGER NOT NULL,
               FOREIGN KEY (owner_id) REFERENCES users(id)
               )
""")

query = "INSERT INTO chatrooms (room_name, vibe_rule, owner_id) VALUES (?, ?, ?);"
#cursor.execute(query, ("testroom", "sql-related discussions only", 1))
#cursor.execute(query, ("testroom2", "flask-related discussions only", 1))
#cursor.execute(query, ("testroom3", "frontend-related discussions only", 2))

cursor.execute("""
CREATE TABLE IF NOT EXISTS room_members(
               room_id INTEGER NOT NULL,
               user_id INTEGER NOT NULL,
               FOREIGN KEY (room_id) REFERENCES chatrooms(id),
               FOREIGN KEY (user_id) REFERENCES users(id),
               PRIMARY KEY (room_id, user_id)
               );
""")

# cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?);", (1, 1))
# cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?);", (3, 1))
# cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?);", (4, 1))
# cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?);", (4, 2))

#cursor.execute("ALTER TABLE room_members ADD COLUMN invite_status TEXT DEFAULT 'pending'")
#cursor.execute("UPDATE room_members SET invite_status = 'accepted';")

#cursor.execute("UPDATE room_members SET invite_status = 'accepted' WHERE room_id = 8 AND user_id = 1")

conn.commit()
conn.close()


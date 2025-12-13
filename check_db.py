import sqlite3

conn = sqlite3.connect("journal.db")
c = conn.cursor()
c.execute("SELECT book, author, note, tags FROM notes")
for row in c.fetchall():
    print(row)
conn.close()

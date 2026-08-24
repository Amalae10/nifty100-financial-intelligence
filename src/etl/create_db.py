import sqlite3
conn=sqlite3.connect("nifty100.db")
conn.execute("PRAGMA foreign_keys = ON")
with open("db/schema.sql","r") as file:
    conn.executescript(file.read())
conn.commit()
conn.close()

print("Database Created")
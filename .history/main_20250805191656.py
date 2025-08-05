from etl_utils import load_csv_to_sqlite

load_csv_to_sqlite("data/movies.csv", archive=False)

import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(movies);")
print(cursor.fetchall())
conn.close()

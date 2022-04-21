import sqlite3

def file_query(path: str, cursor: sqlite3.Cursor):
    with open(path, encoding="utf-8") as f:
        cursor.execute(f.read())

class DbHandler:
    def __init__(self, dbname: str):
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()
        file_query("schema.sql", self.cursor)
    def __enter__(self):
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.connection.commit()



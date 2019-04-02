import sqlite3


class DB:
    def __init__(self):
        conn = sqlite3.connect('dialog.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                      (user_name, password_hash) 
                      VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = {}".format(str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def delete(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = {}'''.format(str(user_id)))
        cursor.close()
        self.connection.commit()


class LettersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS letters 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             content VARCHAR(100000),
                             user_id1 INTEGER,
                             user_id2 INTEGER,
                             dialog_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, c, uid1, uid2, did):

        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO letters 
                          (content, user_id1, user_id2, dialog_id) 
                          VALUES (?,{},{},{})'''.format(str(uid1), str(uid2), str(did)), c)
        cursor.close()
        self.connection.commit()

    def get(self, letter_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM letters WHERE id = {}".format(str(letter_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, dial_id=None):
        cursor = self.connection.cursor()
        if dial_id:
            cursor.execute("SELECT * FROM letters WHERE dialog_id = {}".format(str(dial_id)))
        else:
            cursor.execute("SELECT * FROM letters")
        rows = cursor.fetchall()
        return rows

    def delete(self, letter_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM letters WHERE id = ?''', (str(letter_id)))
        cursor.close()
        self.connection.commit()

    def put(self, letter_id, content=None):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE letters SET content = ?
                        WHERE id = ? ''',
                       (content, str(letter_id)))
        cursor.close()
        self.connection.commit()


class DialogModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS dialog 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_id_t INTEGER, 
                             user_id_f INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_id1, user_id2):

        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO dialog 
                          (user_id_t, user_id_f) 
                          VALUES ({}, {})'''.format(str(user_id1), str(user_id2)))
        cursor.close()
        self.connection.commit()

    def get(self, dialog_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM dialog WHERE id = {}".format(str(dialog_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM dialog WHERE user_id_t = {} OR user_id_f = {}".
                           format(str(user_id), str(user_id)))
        else:
            cursor.execute("SELECT * FROM dialog")
        rows = cursor.fetchall()
        return rows

    def delete(self, dialog_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM dialog WHERE id = {}'''.format(str(dialog_id)))
        cursor.close()
        self.connection.commit()

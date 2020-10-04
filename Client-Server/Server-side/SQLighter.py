import sqlite3 as sl


class SQLighter:

    def __init__(self):
        self.connection = sl.connect('chat_database.db')
        self.cursor = self.connection.cursor()

        try:
            self.cursor.execute("""CREATE TABLE users
                            (id_user integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                             name text NOT NULL,
                             password text NOT NULL,
                             email text NOT NULL)
                             """)
            self.cursor.execute("""CREATE TABLE messages
                            (id_msg integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                             id_user integer NOT NULL,
                             text text NOT NULL,
                             datetime timestamp NOT NULL,
                             FOREIGN KEY (id_user) REFERENCES users(id_user))
                            """)
        except sl.OperationalError:
            pass

    def select_all(self, table):
        """ Get all lines """

        with self.connection:
            return self.cursor.execute(f'SELECT * FROM {table}').fetchall()

    def add_new_user(self, row):
        with self.connection:
            return self.cursor.execute(f'INSERT INTO users (name, password, email) VALUES(?, ?, ?)', row)

    def add_new_message(self, msg_info):
        with self.connection:
            return self.cursor.execute(f'INSERT INTO messages (id_user, text, datetime) VALUES(?, ?, ?)',
                                       msg_info)

    def select_single(self, table, rownum):
        """ Get one row with number rownum from table"""

        with self.connection:
            return self.cursor.execute(f'SELECT * FROM {table} WHERE id = ?',
                                       (rownum,)).fetchall()[0]

    def check_uniqueness(self, json_rqst, email, pw):
        """ Checking the uniqueness of mail and password (or others) """
        try:
            answer = self.cursor.execute(f'SELECT id_user, name FROM users WHERE {email}=? AND {pw}=?',
                                        (json_rqst[email], json_rqst[pw],)).fetchall()[0]
            return answer
        except IndexError:
            return None

    def close(self):
        self.connection.close()


if __name__ == '__main__':

    sq = SQLighter()
    sq.add_new_user(('Mars', '1357', 'qwerty@mail.ru'))

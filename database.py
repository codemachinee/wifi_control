import sqlite3

create_cash_table = "CREATE TABLE IF NOT EXISTS cash (mac TEXT, name TEXT);"
create_users_table = "CREATE TABLE IF NOT EXISTS users (mac TEXT, name TEXT);"
create_main_table = "CREATE TABLE IF NOT EXISTS main (mac TEXT, name TEXT);"


class database:
    def __init__(self):
        self.base = sqlite3.connect('users.db')
        self.cur = self.base.cursor()
        self.base.execute(create_cash_table)
        self.base.execute(create_users_table)
        self.base.execute(create_main_table)

    def search_in_table(self, table, search_mac):
        # result = self.cur.execute(f"SELECT * FROM {table} WHERE mac = '{search_mac}';").fetchall()
        result = self.cur.execute(f"SELECT * FROM {table} WHERE mac == ?", (search_mac,)).fetchall()
        if result:
            return [True, result[0][1]]
        else:
            return [False, 'неизвестное устройство']

    def update_table(self, table, update_mac, update_name='неизвестное устройство'):
        # self.cur.execute(f"INSERT INTO {table} (mac, name) VALUES ('{update_mac}', '{update_name}');")
        self.cur.execute(f"INSERT INTO {table} (mac, name) VALUES (?, ?);", (update_mac, update_name))
        self.base.commit()

    def return_all(self, table):
        return self.cur.execute(f"SELECT * FROM {table};").fetchall()

    def delete_user(self, table, mac):
        # self.cur.execute(f"DELETE FROM {table} WHERE mac = '{mac}';")
        self.cur.execute(f"DELETE FROM {table} WHERE mac = ?;", (mac,))
        self.base.commit()
        print(f'мак адрес {mac} удален из таблицы {table}')

    def delete_all(self, table):
        self.cur.execute(f"DELETE FROM {table};")
        self.base.commit()
        print(f'таблица {table} очищена')



# print(database().search_in_table(table='cash', search_mac='a1:b1'))
# print(database().search_in_table(table='main', search_mac='06:af:55:ab:28:40'))
# print(database().search_in_table(table='users', search_mac='a3:b3'))

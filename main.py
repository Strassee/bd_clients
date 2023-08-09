import psycopg2

def create_db():
    cursor.execute("""
        DROP TABLE clients_phones;
        DROP TABLE clients;           
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id_client SERIAL PRIMARY KEY,
            soname VARCHAR(40),
            name VARCHAR(40),
            email VARCHAR(40) UNIQUE CHECK (email ~ '(.+)(@){1}(.+)(\.){1}(.+)'));
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients_phones(
            id_client INTEGER NOT NULL REFERENCES clients(id_client),
            phone VARCHAR(20) NOT NULL CHECK (phone ~ '^[\d]{10,12}$'),
            CONSTRAINT pk_cp PRIMARY KEY (id_client, phone));
        """)

    conn.commit()

def new_client(soname, name, email):
    try:
        cursor.execute("""
            INSERT INTO clients(soname,name,email) VALUES(%s, %s, %s) RETURNING id_client;
            """, (soname, name, email))
        id = cursor.fetchone()[0]
        print(f'Клиент {soname} {name} добавлен, ему присвоен id = {id}')
    except:
        print('Ошибка добавления клиента')

def add_phone(id_client, phone):
    try:
        cursor.execute("""
            INSERT INTO clients_phones(id_client,phone) VALUES(%s, %s) RETURNING id_client;
            """, (id_client, phone))
        cursor.fetchone()
        print(f'Клиенту с id = {id_client} добавлен номер телефона {phone}')
    except:
        print('Ошибка добавления номера телефона')

def update_client(id_client, soname = False, name = False, email = False):
    if soname:
        try:
            cursor.execute("""
                UPDATE clients SET soname=%s WHERE id_client=%s RETURNING soname;
                """, (soname, id_client))
            cursor.fetchone()
            print(f'Клиенту с id = {id_client} фамилия обновлена на {soname}')
        except:
            print('Ошибка обновления фамилии')           
    if name:
        try:
            cursor.execute("""
                UPDATE clients SET name=%s WHERE id_client=%s RETURNING name;
                """, (name, id_client))
            cursor.fetchone()
            print(f'Клиенту с id = {id_client} имя обновлено на {name}')
        except:
            print('Ошибка обновления имени')
    if email:
        try:
            cursor.execute("""
                UPDATE clients SET email=%s WHERE id_client=%s RETURNING name;
                """, (email, id_client))
            cursor.fetchone()
            print(f'Клиенту с id = {id_client} email обновлен на {email}')
        except:
            print('Ошибка обновления email')             

def del_phone(id_client, phone):
    cursor.execute("""
        DELETE FROM clients_phones WHERE id_client=%s AND phone=%s RETURNING id_client;
        """, (id_client, phone))
    if cursor.fetchone() is not None:
        print(f'У клиента с id = {id_client} номер телефона {phone} удален')
    else:
        print('Ошибка удаления номера телефона') 

def del_client(id_client):
    cursor.execute("""
        DELETE FROM clients_phones WHERE id_client=%s;
        DELETE FROM clients WHERE id_client=%s RETURNING id_client;
        """, (id_client, id_client))
    if cursor.fetchone() is not None:
        print(f'Клиент с id = {id_client} удален')
    else:
        print('Ошибка удаления клиента')   

def search_client(soname = False, name = False, email = False, phone = False):
    sql_string = 'SELECT a.*, b.phone FROM clients AS a LEFT JOIN clients_phones AS b ON a.id_client=b.id_client WHERE '
    if soname:
        sql_string += f"a.soname='{soname}'"    
    if name:
        if sql_string[-6:] != 'WHERE ':
            sql_string += ' AND '        
        sql_string += f"a.name='{name}'"
    if email:
        if sql_string[-6:] != 'WHERE ':
            sql_string += ' AND '
        sql_string += f"a.email='{email}'"
    if phone:
        if sql_string[-6:] != 'WHERE ':
            sql_string += ' AND '        
        sql_string += f"b.phone='{phone}'"
    sql_string += ';'
    cursor.execute(sql_string)
    result = cursor.fetchall()
    if result != []:
        print('Результаты поиска:')
        for string in result:
            print(f'ID: {string[0]}, Фамилия: {string[1]}, Имя: {string[2]}, E-mail: {string[3]}, Телефон: {string[4]}')
    else:
        print('Клиента с указанными данными не найдено')


database = input('Введите имя базы данных: ')                   # 
user = input('Введите имя пользователя базы данных: ')          # 
password = input('Введите пароль пользователя: ')               # 

with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cursor:

            create_db()

            new_client('Ivanov', 'van', 'ivanov@mail.ru')
            add_phone(1, '81234567890')
            add_phone(1, '1234567891')
            add_phone(1, '1234567892')
            new_client('petrov', 'Vasiliy', 'petrov@mail.ru')
            add_phone(2, '81234567803')
            new_client('Sidorov', 'Aleksandr', 'sidorov@mai.ru')
            new_client('Abc', 'Cab', 'abc@mai.ru')
            update_client(1, False, 'Ivan', False)
            update_client(2, 'Petrov', False, False)
            update_client(3, False, False, 'sidorov@mail.ru')
            del_phone(1, '1234567892')
            del_client(4)

            search_client('Ivanov', 'Ivan', 'ivanov@mail.ru', False)
            search_client('Ivanov', 'Ivan', False, False)
            search_client(False, False, 'ivanov@mail.ru', False)
            search_client(False, False, 'ivanov@mail.ru', '81234567890')
            search_client('Ivanov', 'Ivan', False, '1234567891')

            search_client('petrov', False, False, False)
            search_client('Petrov', False, False, False)

            search_client(False, 'Aleksandr', False, False)

            search_client('Abc', False, False, False)
        cursor.close()
conn.close() 
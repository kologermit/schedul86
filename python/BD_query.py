import mysql.connector
import time
from datetime import datetime

# Функция для перевола типа данных в строку
def tp(s):
    return str(type(s))

# Функия для получения объекта sql
def get_sql(host, user, password, database):
    while True:
        try:
            sql = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
            break
        except:
            print("Error MySQLConnection")
    return sql

# Фнкция для запросов к БД
def BD_query(sql, query, table, columns = [], data = [], where = [], limit = -1):
        # query = "UPDATE", "SELECT", "INSERT"

        # Проверка типов переданных параметров
    if tp(query) != '<class \'str\'>': 
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: type query != <str>")
        return []
    if tp(table) != "<class 'str'>":
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: type table != <str>")
        return []
    if tp(data) != "<class 'list'>":
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: type data != <list>")
        return []
    if tp(where) != "<class 'list'>":
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: type where != <list>")
        return []
    query = query.upper().strip()
    if not(query in ["UPDATE", "SELECT", "INSERT"]):
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: query does not match possible queries ([\"UPDATE\", \"SELECT\", \"INSERT\"])")
        return []
    if tp(limit) != "<class 'int'>":
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "Error: type limit != <int>")
        return []
    cursor = None

    #Если query = "SELECT" (Получение данных)
    if query == "SELECT":
        if columns == [] or columns == '*':
            query += " *"
        elif tp(columns) == "<class 'list'>":
            for i in range(len(columns) - 1):
                if tp(columns[i]) == "<class 'str'>":
                    query += f" `{columns[i]}`, "
                else:
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type column[{i}] != <str>")
                    return []
            if tp(columns[-1]) == "<class 'str'>":
                query += f" `{columns[-1]}` "
            else:
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type column[{-1}] != <str>")
                return []
        elif tp(columns) == "<class 'str'>":
            query += f" {columns}"
        else:
            print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "SelectError: type columns != <list> or <str>")
            return []
        query += f" FROM `{table}`"

        if tp(where) == "<class 'list'>" and where != []:
            query += " WHERE"
            size = len(where)
            for i in range(size):
                if i == size - 1:
                    i = -1
                if tp(where[i]) not in ["<class 'list'>", "<class 'tuple'>"]:
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type where[{i}] != <list> or <tuple>")
                    return []
                if len(where[i]) < 3:
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: len where[{i}] < 3")
                    return []
                if tp(where[i][0]) != "<class 'str'>":
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type where[{i}][0] != <str>")
                    return []
                if tp(where[i][1]) != "<class 'str'>":
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type where[{i}][1] != <str>" )
                    return []
                if not(tp(where[i][2]) in ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'float'>", "<class 'NoneType'>"]):
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"SelectError: type where[{i}][2] != <bool>, <int>, <float> or <str>")
                    return []
                query += f" `{where[i][0]}` {where[i][1]} "
                if tp(where[i][2]) == "<class 'str'>":
                    query += '"' + where[i][2].replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`") + '"'
                elif tp(where[i][2]) == "<class 'bool'>":
                    query += str(int(where[i][2]))
                elif where[i][2] == None:
                    query += "null"
                else:
                    query += str(where[i][2])
                if i != -1:
                    query += " AND"
        if limit >= 1:
            query += f" LIMIT {limit}"
        while(True):
            try:
                cursor = sql.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                break
            except Exception as err:
                print("\a")
                try:
                    cursor.close()
                except:
                    print("SELECT Проблемы с закрытием курсора")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "SELECT Проблемы с mysql")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + str(err))
                time.sleep(1.5)
                sql.reconnect()
                time.sleep(1.5)
        if result == None:
            result = []
        return result

    # Если query = "UPDATE" (Изменение данных)
    elif query == "UPDATE":
        if len(data) == 0:
            print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "UpdateError: size data = 0")
            return
        if len(where) == 0:
            print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "UpdateError: size where = 0")
            return
        query += f" `{table}`\nSET"
        size = len(data)
        for i in range(size):
            if i == size - 1:
                i = -1
            if tp(data[i]) != "<class 'tuple'>":
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type data[{i}] != <tuple>")
                return
            if len(data[i]) != 2:
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: size data[{i}] != 2")
                return
            if tp(data[i][0]) != "<class 'str'>":
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type data[{i}][0] != <str>")
                return
            if tp(data[i][1]) not in ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'float'>", "<class 'NoneType'>"]:
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type data[{i}][1] != <bool>, <int>, <float> or <str>")
                return
            
            query += f" `{data[i][0]}` = "
            if tp(data[i][1]) == "<class 'str'>":
                query += '"' + data[i][1].replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`") + '"'
            elif tp(data[i][1]) == "<class 'bool'>":
                query += str(int(data[i][1]))
            elif data[i][1] == None:
               query += "null"
            else:
                query += str(data[i][1])
            if i != -1:
                query += ", "

        if tp(where) == "<class 'list'>" and where != []:
            query += "\nWHERE"
            size = len(where)
            for i in range(size):
                if i == size - 1:
                    i = -1
                if tp(where[i]) not in ["<class 'list'>", "<class 'tuple'>"]:
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type where[{i}] != <list> or <tuple>")
                    return
                if len(where[i]) < 3:
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: len where[{i}] < 3")
                    return
                if tp(where[i][0]) != "<class 'str'>":
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type where[{i}][0] != <str>")
                    return
                if tp(where[i][1]) != "<class 'str'>":
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type where[{i}][1] != <str>" )
                    return
                if not(tp(where[i][2]) in ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'float'>"]):
                    print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + f"UpdateError: type where[{i}][2] != <bool>, <int>, <float> or <str>")
                    return
                query += f" `{where[i][0]}` {where[i][1]} "
                if tp(where[i][2]) == "<class 'str'>":
                    query += '"' + str(where[i][2]).replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`") + '"'
                elif tp(where[i][2]) == "<class 'bool'>":
                    query += str(int(where[i][2]))
                elif where[i][2] == None:
                    query += "null"
                else:
                    query += str(where[i][2])
                if i != -1:
                    query += " AND"
        while(True):
            try:
                cursor = sql.cursor()
                cursor.execute(query)
                sql.commit()
                cursor.close()
                break
            except Exception as err:
                print("\a")
                try:
                    cursor.close()
                except:
                    print("UPDATE Проблемы с закрытием курсора")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "UPDATE Проблемы с mysql")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + str(err))
                time.sleep(1.5)
                try:
                    sql.reconnect()
                except:
                    print("UPDATE Проблемы с переподключением sql")
                time.sleep(1.5)
        return "UPDATE: success"

    # Если query = INSERT (Добавление данных)
    elif query == "INSERT":
        querys = []
        if len(data) == 0:
            print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "InsertError: size data = 0")
            return
        result = ""
        for i in range(len(data)):
            if tp(data[i]) != "<class 'dict'>":
                result += f"{i + 1}. InsertError: type data[{i}] != <dict>"
                continue
            size = len(data[i])
            if size == 0:
                result += f"{i + 1}. InsertError: size data[{i}] = 0"
                continue
            keys = tuple(data[i].keys())
            for j in range(size):
                if tp(data[i][keys[j]]) not in ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'float'>", "<class 'NoneType'>"]:
                    result += f"{i + 1}. InsertError: type data[{i}][\"{keys[j]}\"] != <bool>, <int>, <float> or <str>"
                    continue
            query = f"INSERT INTO `{table}` ("
            for j in range(size):
                if j == size - 1:
                    query += f"`{keys[j]}`)"
                else:
                    query += f"`{keys[j]}`, "
            query += " VALUE"
            if size > 1:
                query += "S"
            query += " ("
            for j in range(size):
                if tp(data[i][keys[j]]) == "<class 'str'>":
                    data[i][keys[j]] = '\'' + data[i][keys[j]].replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`") + '\''
                elif tp(data[i][keys[j]]) == "<class 'bool'>":
                    data[i][keys[j]] = int(data[i][keys[j]])
                elif data[i][keys[j]] == None:
                    data[i][keys[j]] = "null"
                if j == size - 1:
                    query += f"{data[i][keys[j]]})"
                else:
                    query += f"{data[i][keys[j]]}, "
            querys.append(query)
            result += f"{i + 1}. INSERT: success"
        while True:
            try:
                cursor = sql.cursor()
                for key in querys:
                    cursor.execute(key)
                break
            except Exception as err:
                print("\a")
                try:
                    cursor.close()
                except:
                    print("INSERT Проблемы с закрытием курсора")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + "INSERT Проблемы с mysql")
                print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + str(err))
                time.sleep(1.5)
                try:
                    sql.reconnect()
                except:
                    print("INSERT Проблемы с переподключением mysql")
                time.sleep(1.5)
        try:
            sql.commit()
        except:
            print("INSERT Проблемы с sql.commit()")
        try:
            cursor.close()
        except:
            print("INSERT Проблемы с закрытием курсора")
        try:
            sql.close()
        except:
            print("INSERT Проблемы с закрытием соединения mysql")
        return result

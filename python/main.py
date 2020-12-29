#Подключение библиотек
import telebot
import json
import mysql.connector
import requests
import urllib.request
import os
import time
from datetime import datetime
from telebot import types
from threading import Thread

# Подключение своих файлов
import BD_query
import read_excel
import config
import calls
import schedule
import get_weather
import edit_calls
        
TOKEN = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "info", columns="text", where=[("theme", "=", "TOKEN")])[0][0]
days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
days4 = ["ПОНЕ", "ВТОР", "СРЕД", "ЧЕТВ", "ПЯТН", "СУББ", "ВОСК"]
abc = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
answers = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "info", columns="text", where=[("theme", "=", "answers")])
   
if answers == []:
    raise "answers"
else:
    answers = json.loads(answers[0][0])
    start_settings = json.loads(BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "info", columns="text", where=[("theme", "=", "start_settings")])[0][0])
# Подключение к TelegramBotApi
while True:
    try:
        bot = telebot.TeleBot(TOKEN)
        mysql.connector.connect(**config.mysql_config)
        break
    except HTTPSConnectionPool as err:
        print(err)

BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "UPDATE", "info", data=[('text', datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))], where=[("theme", "=", "last_start")])
admins = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "info", \
    columns="text", where=[("theme", "=", "admins")])
last_start = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
if admins:
    admins = json.loads(admins[0][0])
for key in admins:
    bot.send_message(key, f"Произошёл запуск бота\nВремя запуска: {last_start}")

def split_date(line):
    line = line.strip()
    data = line.split(".")
    if len(data) != 3:
        return False
    day, month, year = data
    if not(is_num(day) and is_num(month) and is_num(year)):
        return False
    day, month, year = abs(int(day)), abs(int(month)), abs(int(year))
    return day, month, year

# Функция для разбиение строки на слова
def words(line):
    answer = []
    line = line.strip()
    a = next_word(line)
    while (a[0]):
        answer.append(a[0])
        a = next_word(a[1])
    return answer

# Функия для получения слудующего слова  
def next_word(line):
    line = line.strip()
    space = line.find(" ")
    enter = line.find("\n")
    if line == "":
        return ("", "")
    if space == -1 and enter == -1:
        return (line, "")
    min = 1e10
    if space != -1 and min > space:
        min = space
    if enter != -1 and min > enter:
        min = enter
    return (line[0: min], line[min + 1:])

# Функция для проверки строки на сдержание числа
def is_num(line):
    try:
        float(line)
        return True
    except:
        return False

# Функция для получения объекта sql класса
def get_sql():
    return BD_query.get_sql(**config.mysql_config)

# Функция для получения прошлого дня в числовой форме
def last_weekday():
    now = datetime.now().weekday() - 1
    if now == -1:
        now = 5
    return now

def edit_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Удалить"), types.KeyboardButton("Добавить"))
    markup.add(types.KeyboardButton("Меню"))
    return markup

def classes_markup(featured_classes):
    classes = BD_query.BD_query(get_sql(), "SELECT", "info", where=[("theme", "=", "classes")])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if not len(classes):
        return markup
    classes = json.loads(classes[0][0])
    answer = []
    for class_n in classes.keys():
        for class_b in classes[class_n]:
            if f"{class_n}{class_b}" not in featured_classes:
                answer.append(types.KeyboardButton(f"{class_n}{class_b}"))
    markup.add(*answer)
    markup.add("Меню")
    return markup

# Функция для создания стартового сообщения
def start_markup(commands=[]):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    arr = ["Уроки", "Звонки", "Информация", "Где физ-ра?" , "Настройки", "Меню в столовой"]
    for i in range(len(arr)):
        arr[i] = types.KeyboardButton(arr[i])
    for key in commands:
        arr.append(types.KeyboardButton(key))
    markup.add(*arr)
    return markup

# Функция для логирования в базу данных
def log_query(sql, date, chat_id, first_name, last_name, text):
    print(date, chat_id, first_name, last_name, f"|{text}|")
    return BD_query.BD_query(get_sql(), "INSERT", "log_query", data=[{
        "text": json.dumps({"date": str(date), "chat_id": chat_id, "first_name": first_name, "last_name": last_name, "text": text}, indent=2)
    }])

# Функия для получение количества параллелей
def get_classes_count():
    Min = 1e4
    Max = 0
    i = 0
    js = BD_query.BD_query(get_sql(), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
    if js == []:
        return 0
    else:
        js = json.loads(js[0][0])
    js = js.keys()
    for key in js:
        Min = min(Min, int(key))
        Max = max(Max, int(key))
    return Min, Max

# Функция для получения кнопок параллелей
def classes_n():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    js = BD_query.BD_query(get_sql(), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
    if js == []:
        return markup
    else:
        js = json.loads(js[0][0])
    answer = []
    for data in js.keys():
       answer.append(types.KeyboardButton(data))
    markup.add(*answer)
    markup.add(types.KeyboardButton("Меню"))
    return markup

# Функция для получения кнопок букв в параллели
def classes_b(status):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    js = BD_query.BD_query(get_sql(), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
    if js == []:
        return markup
    else:
        js = js[0][0]
    line = json.loads(js)[str(status)]
    answer = []
    for data in line:
        answer.append(types.KeyboardButton(data))
    markup.add(*answer)
    markup.add(types.KeyboardButton("Меню"))
    return markup

def settings_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Уведомления об изменениях в расписании"))
    markup.add(types.KeyboardButton("Избранные команды"))
    markup.add(types.KeyboardButton("Меню"))
    return markup

def commands_add_markup(commands, resize=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if not resize:
        for key in commands:
            markup.add(types.KeyboardButton(key))
    else:
        for i in range(len(commands)):
            commands[i] = (types.KeyboardButton(commands[i]))
        markup.add(*commands)
    markup.add(types.KeyboardButton("Меню"))
    return markup

# Функция для проверки существования букв в параллели
def is_b_in_classes(class_n, class_b):
    js = BD_query.BD_query(get_sql(), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
    if js == []:
        return False
    else:
        js = js[0][0]
    js = json.loads(js)[str(class_n)]
    return (js.find(class_b.upper())) != -1

# Функция проверки дня недели
def is_week_day(line):
    arr = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]
    return line.upper() in arr

# Обработчик присланных пользователем документов
@bot.message_handler(content_types=['document'])
def document(message):
    answer = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{bot.get_file(message.document.file_id).file_path}')
    if str(type(answer)) != "<class 'str'>":
        bot.send_message(message.chat.id, answers["file_download_success"])
    else:
        bot.send_message(message.chat.id, answer)
    message_id = message.chat.id
    if not os.path.exists("Temp"):
        os.mkdir("Temp")
    if not os.path.exists(f"Temp/{message_id}"):
        os.mkdir(f"Temp/{message.chat.id}")
    if not os.path.exists(f"Temp/{message_id}/documents"):
        os.mkdir(f"Temp/{message_id}/documents")
    file_path = bot.get_file(message.document.file_id).file_path
    url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=f"file: {url}"
    )
    urllib.request.urlretrieve(url, f"Temp/{message_id}/{file_path}")
    path = f"Temp/{message_id}/{file_path}"
    while True:
        try:
            file = open(path, "r")
            break
        except:
            pass
    file.close()
    try:
        result = read_excel.read(path, bot, message)
        if result:
            data, edited, day = result
            users = BD_query.BD_query(get_sql(), "SELECT", "users", columns=["id", "settings"])
            for i in range(len(users)):
                temp = {
                    "id": users[i][0],
                    "featured_classes": json.loads(users[i][1])["featured_classes"]
                }
                users[i] = temp
            for key in users:
                for key2 in key["featured_classes"]:
                    message.text = day
                    if day in ["ПЯТНИЦА", "СУББОТА", "СРЕДА"]:
                        day = day[:len(day) - 1] + "У"
                    if key2 in data.keys():
                        if is_num(key2[0:2]):
                            class_n = int(key2[0:2])
                        else:
                            class_n = int(key2[0])
                        class_b = key2[-1]
                        js = data
                        day = message.text
                        if message.text in ["ПЯТНИЦА", "СУББОТА", "СРЕДА"]:
                            day = day[:len(day) - 1] + "У"
                        if edited == 'edited':
                            answer = f'Изменения в расписании на {day.lower()} для {key2}:\n'
                        else:
                            answer = f'Изменения в основном расписании на {day.lower()} для {key2}:\n'
                        if day in ["ПЯТНИЦУ", "СУББОТУ", "СРЕДУ"]:
                            day = day[:len(day) - 1] + "А"
                        for i in range(len(data[key2])):
                            answer += f"{i + 1}. {data[key2][i]}\n"
                        bot.send_message(key["id"], answer)
                        BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "UPDATE", "users", data=[('class_n', None), ('class_b', None)], where=[("id", "=", message.chat.id)])
        else:
            os.remove(path)
            return
        for key in list(data.items()):
            if len(key[0]) == 3:
                class_n = int(key[0][0:2])
                class_b = key[0][2]
            else:
                class_n = int(key[0][0])
                class_b = key[0][1]
            answer = BD_query.BD_query(get_sql(), "SELECT", "classes", columns="schedule", where=[("class_b", "=", class_b), ("class_n", "=", class_n)])
            # print("Check 1", answer)
            if answer == []:
                raise Exception("BD_query: Error")
            else:
                answer = answer[0][0]
            answer = json.loads(answer)
            answer[edited][day.upper()] = key[1]
            r = BD_query.BD_query(get_sql(), "UPDATE", "classes", where=[("class_b", "=", class_b), ("class_n", "=", class_n)], data=[("schedule", json.dumps(answer, indent=2))])
            # print("Check 2", r)
        os.remove(path)
    except Exception as err:
        
        print(err)
        bot.send_message(message.chat.id, answers["file_processing_error"])
        os.remove(path)
        return

# Первый запуск или перезапуск бота /start
@bot.message_handler(commands=["start", "restart"])
def start(message):
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    bot.send_message(message.chat.id, answers["start_answer"])
    bot.send_message(message.chat.id, answers["commands_info"], reply_markup=start_markup())
    user = BD_query.BD_query(get_sql(), "SELECT", table="users", where=[("id", "=", message.chat.id)], limit=1)
    if not len(user):
        BD_query.BD_query(get_sql(), "INSERT", "users", data=[{"id": message.chat.id, "class_n": None, "class_b": None, "name": f"{message.chat.first_name} {message.chat.last_name}", "settings": json.dumps(start_settings, indent=2)}])
    else:
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("settings", json.dumps(start_settings, indent=2))],\
         where=[("id", "=", message.chat.id)])
    return


@bot.message_handler(commands=["set_menu"])
def edit_schedule(message):
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    message.text = message.text.strip()
    chat_id = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "techers")])
    if chat_id == []:
        return None
    elif message.chat.id not in json.loads(chat_id[0][0]):
        bot.send_message(message.chat.id, "У вас нет прав изменять \nменю столовой!")
        return None
    answer = edit_calls.next_word(message.text)[1]
    if answer:
        BD_query.BD_query(get_sql(), "UPDATE", "info", data=[("text", answer)], \
            where=[("theme", "=", "menu")])
        bot.send_message(message.chat.id, "Меню столовой изменено")
    else:
        bot.send_message(message.chat.id, "В команде нет изменений!")

@bot.message_handler(commands=["edit_schedule"])
def edit_schedule(message):
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    chat_id = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "techers")])
    if chat_id == []:
        return None
    elif message.chat.id not in json.loads(chat_id[0][0]):
        bot.send_message(message.chat.id, "У вас нет прав изменять \nрасписание уроков!")
        return None
    print(edit_calls.main(bot, message))

def week_min(line):
    if line == 'ПН':
        return "ПОНЕДЕЛЬНИК"
    if line == 'ВТ':
        return "ВТОРНИК"
    if line == 'СР':
        return "СРЕДА"
    if line == 'ЧТ':
        return "ЧЕТВЕРГ"
    if line == 'ПТ':
        return "ПЯТНИЦА"
    if line == 'СБ':
        return "СУББОТА"
    return line

@bot.message_handler(commands=["info"])
def info(message):
    bot.send_message(message.chat.id, answers["info"])
    bot.send_message(message.chat.id, answers["commands_info"])
    if message.text.strip()[0:len("/info")].upper() == "/INFO":
        log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    return

# Управление ботом через бота
@bot.message_handler(commands=["python_command"])
def python_command(message):
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    chat_id = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "techers")])
    if chat_id == []:
        return None
    elif message.chat.id not in json.loads(chat_id[0][0]):
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде")
        return None
    answer = next_word(message.text)
    try:
        exec(answer[1])
    except:
        bot.send_message(message.chat.id, "Произошла ошибка во время выполненя кода")



# Обработчик присланных пользователем сообщений
@bot.message_handler(content_types=['text'])
def main1(message):
    if message.chat.id == 607443836:
        bot.send_message(847721936, f"Андрей: {message.text}")
    text = message.text
    log_query(get_sql(), 
        date=datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        chat_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        text=message.text
    )
    message.text = message.text.upper().strip()
    is_technical_work = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", \
        where=[("theme", "=", "is_technical_work")])
    if is_technical_work != []:
        if is_technical_work[0][0] == "True":
            answer = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "info", \
                columns="text", where=[("theme", "=", "technical_work_answer")])
            if answer != []:
                answer = answer[0][0]
            else:
                try:
                    answer = open("answers/technical_work_answer", "r").read()
                except:
                    answer = "На данный момент сервер не может дать ответ по техничестим причинам"
            bot.send_message(message.chat.id, answer)
            return
    if message.chat.type != 'private':
        return


    user = BD_query.BD_query(get_sql(), "SELECT", table="users", columns=["class_n", "class_b", "settings"], \
        where=[("id", "=", message.chat.id)], limit=1)
    if not len(user):
        BD_query.BD_query(get_sql(), "INSERT", "users", data=[{"id": message.chat.id, "class_n": None, \
            "class_b": None, "name": f"{message.chat.first_name} {message.chat.last_name}", "settings": json.dumps(start_settings, indent=2)}])
        status = {
            "class_n": None,
            "class_b": None,
            "settings": start_settings
        }
    else:
        status = {
            "class_n": user[0][0],
            "class_b": user[0][1],
            "settings": json.loads(user[0][2])
        }
    def is_settings():
        return status["settings"]["is_setting_commands_add"] == False and \
        status["settings"]["is_setting_commands_erase"] == False and \
        status["settings"]["is_setting_classes_add"] == False and \
        status["settings"]["is_setting_classes_erase"] == False
    if is_num(message.text) and is_settings():
        Min, Max = get_classes_count()
        if int(message.text) >= Min and int(message.text) <= Max and status["class_n"] == None and \
        status["class_b"] == None:
            bot.send_message(message.chat.id, answers["choose_class_b"], \
                reply_markup=classes_b(int(message.text)))
            BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", int(message.text)), \
                ("class_b", None)], where=[("id", "=", message.chat.id)])
            return
    
    classes = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", \
        columns="text", where=[("theme", "=", "classes")])
    if classes == []:
        return

    t = words(message.text)
    if (len(t) == 2 or len(t) == 3) and is_settings():
        if read_excel.is_class_name(json.loads(classes[0][0]), t[0]) and is_week_day(t[1]):
            t[1] = week_min(t[1])
            if is_num(t[0][0:2]):
                class_n = int(t[0][0:2])
            else:
                class_n = int(t[0][0])
            class_b = t[0][-1]
            message.text = t[1]
            schedule.weekday(message, bot, class_n, class_b, start_markup(status["settings"]["commands"]))
            return
        elif len(t) == 3 and read_excel.is_class_name(json.loads(classes[0][0]), t[0]):
            if t[1] == "ВСЯ" and t[2] == "НЕДЕЛЯ":
                if is_num(t[0][0:2]):
                    class_n = int(t[0][0:2])
                else:
                    class_n = int(t[0][0])
                class_b = t[0][-1]
                message.text = "ВСЯ НЕДЕЛЯ"
                schedule.alldays(message, bot, {"class_n": class_n, "class_b": class_b}, start_markup(status["settings"]["commands"]))
                return

    if read_excel.is_class_name(json.loads(classes[0][0]), message.text) and is_settings():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        arr = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        if is_num(message.text[0:2]):
            class_n = int(message.text[0:2])
        else:
            class_n = int(message.text[0])
        class_b = message.text[-1]
        i = 0
        for data in arr:
            arr[i] = types.KeyboardButton(data)
            i += 1
        markup.add(*arr)
        markup.add(types.KeyboardButton("Вся неделя"))
        markup.add(types.KeyboardButton("Меню"))
        bot.send_message(message.chat.id, answers["choose_day"], reply_markup=markup)
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", class_n), ("class_b", class_b)], where=[("id", "=", message.chat.id)])
        return
        

    if status["class_n"] != None and is_settings():
        if is_week_day(message.text):
            message.text = week_min(message.text)
            schedule.weekday(message, bot, status["class_n"], status["class_b"], start_markup(status["settings"]["commands"]))
            return
        
        elif message.text == "ВСЯ НЕДЕЛЯ":
            schedule.alldays(message, bot, status, start_markup(status["settings"]["commands"]))
            return
    
    if message.text == "МЕНЮ В СТОЛОВОЙ":
        answer = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "menu")], limit=1)
        answer = answer[0][0]
        bot.send_message(message.chat.id, answer)
        return    

    if status["class_n"] != None and is_settings():
        if is_b_in_classes(status["class_n"], message.text):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            arr = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
            i = 0
            for data in arr:
                arr[i] = types.KeyboardButton(data)
                i += 1
            markup.add(*arr)
            markup.add(types.KeyboardButton("Вся неделя"))
            markup.add(types.KeyboardButton("Меню"))
            bot.send_message(message.chat.id, answers["choose_day"], reply_markup=markup)
            BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", status["class_n"]), \
                ("class_b", message.text)], where=[("id", "=", message.chat.id)])
            return
    
    if message.text in ["УРОКИ", "УЗНАТЬ РАСПИСАНИЕ УРОКОВ"] and is_settings():
        bot.send_message(message.chat.id, answers["choose_paral"], reply_markup=classes_n())
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None)], \
            where=[("id", "=", message.chat.id)])
        return

    if message.text == "МЕНЮ":
        bot.send_message(message.chat.id, answers["menu"], reply_markup=start_markup(status["settings"]["commands"]))
        status["settings"]["is_setting"] = False
        status["settings"]["is_setting_classes"] = False
        status["settings"]["is_setting_commands"] = False
        status["settings"]["is_setting_classes_erase"] = False
        status["settings"]["is_setting_commands_add"] = False
        status["settings"]["is_setting_classes_add"] = False
        status["settings"]["is_setting_commands_erase"] = False
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        return

    if message.text == "ЗВОНКИ" and is_settings():
        if calls.main(get_sql(), message, bot):
            return

    if message.text == "ИНФОРМАЦИЯ" and is_settings():
        info(message)
        return

    if message.text == "ГДЕ ФИЗ-РА?" and is_settings():
        r = get_weather.where_fizra()
        if r == None:
            return
        else:
            bot.send_message(message.chat.id, r + "\nНо надо знать, что погода вещь не постоянная!")
        return

    if message.text == "НАСТРОЙКИ" and is_settings():
        status["settings"]["is_setting"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_answer"], reply_markup=settings_markup())
        return

    if status["settings"]["is_setting"] and message.text == 'ИЗБРАННЫЕ КОМАНДЫ' and \
     not status["settings"]["is_setting_classes"] and status["settings"]["is_setting_commands_add"] == False  and status["settings"]["is_setting_commands_erase"] == False:
        status["settings"]["is_setting_commands"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_commands_answer"], reply_markup=edit_markup())
        return

    if message.text == "ДОБАВИТЬ" and status["settings"]["is_setting"] and \
    status["settings"]["is_setting_commands"] and status["settings"]["is_setting_commands_add"] == False  and status["settings"]["is_setting_commands_erase"] == False:
        status["settings"]["is_setting_commands_add"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_commands_add"], reply_markup=commands_add_markup([]))
        return

    if status["settings"]["is_setting"] and status["settings"]["is_setting_commands"] and \
    status["settings"]["is_setting_commands_add"] and status["settings"]["is_setting_commands_erase"] == False:
        status["settings"]["commands"].append(text)
        status["settings"]["is_setting_commands_add"] = False
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_answer"], reply_markup=edit_markup())
        return

    if message.text == "УДАЛИТЬ" and status["settings"]["is_setting"] and \
    status["settings"]["is_setting_commands"] and status["settings"]["is_setting_commands_add"] == False  and status["settings"]["is_setting_commands_erase"] == False:
        if len(status["settings"]["commands"]) == 0:
            bot.send_message(message.chat.id, answers["settings_commands_erase_not_commands"])
            return
        status["settings"]["is_setting_commands_erase"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        answer = answers["settings_commands_erase"] + "\n"
        for i in range(len(status["settings"]["commands"])):
            answer += f"{i + 1}. {status['settings']['commands'][i]}\n"
        bot.send_message(message.chat.id, answer, reply_markup=commands_add_markup(status["settings"]["commands"]))
        return

    if status["settings"]["is_setting"] and \
    status["settings"]["is_setting_commands"] and status["settings"]["is_setting_commands_erase"]:
        if text not in status["settings"]["commands"]:
            answer = answers["settings_commands_erase_error"]
        else:
            answer = answers["settings_commands_erase_success"]
            status["settings"]["commands"].remove(text)
        status["settings"]["is_setting_commands_erase"] = False
        bot.send_message(message.chat.id, answer, reply_markup=edit_markup())
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        return
        
    if status["settings"]["is_setting"] and message.text == 'УВЕДОМЛЕНИЯ ОБ ИЗМЕНЕНИЯХ В РАСПИСАНИИ'\
    and not status["settings"]["is_setting_commands"]:
        status["settings"]["is_setting_classes"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_classes"], reply_markup=edit_markup())
        return

    if message.text == "ДОБАВИТЬ" and status["settings"]["is_setting"] and \
    status["settings"]["is_setting_classes"] and status["settings"]["is_setting_classes_add"] == False  and status["settings"]["is_setting_commands_erase"] == False:
        status["settings"]["is_setting_classes_add"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_classes_add"], reply_markup=classes_markup(status["settings"]["featured_classes"]))
        return

    if status["settings"]["is_setting"] and \
    status["settings"]["is_setting_classes"] and read_excel.is_class_name(json.loads(classes[0][0]), message.text) and \
    status["settings"]["is_setting_classes_add"]:
        if message.text in status["settings"]["featured_classes"]:
            bot.send_message(message.chat.id, answers["settings_classes_add_error"])
            return
        status["settings"]["featured_classes"].append(message.text)
        status["settings"]["is_setting_classes_add"] = False
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_classes_add_success"], reply_markup=edit_markup())
        return 

    if message.text == "УДАЛИТЬ" and status["settings"]["is_setting"] and \
    status["settings"]["is_setting_classes"] and status["settings"]["is_setting_classes_erase"] == False  and status["settings"]["is_setting_commands_erase"] == False:
        if not len(status["settings"]["featured_classes"]):
            bot.send_message(message.chat.id, answers["settings_classes_erase_error2"])
            return
        status["settings"]["is_setting_classes_erase"] = True
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_classes_erase"], reply_markup=commands_add_markup(status["settings"]["featured_classes"], True))
        return

    if status["settings"]["is_setting"] and \
    status["settings"]["is_setting_classes"] and read_excel.is_class_name(json.loads(classes[0][0]), message.text) and \
    status["settings"]["is_setting_classes_erase"]:
        if message.text not in status["settings"]["featured_classes"]:
            bot.send_message(message.chat.id, answers["settings_classes_erase_error"])
            return
        status["settings"]["featured_classes"].remove(message.text)
        status["settings"]["is_setting_classes_erase"] = False
        BD_query.BD_query(get_sql(), "UPDATE", "users", data=[("class_n", None), ("class_b", None), \
            ("settings", json.dumps(status["settings"], indent=2))], where=[("id", "=", message.chat.id)])
        bot.send_message(message.chat.id, answers["settings_classes_erase_success"], reply_markup=edit_markup())
        return 

    bot.send_message(message.chat.id, answers["error_read_user_message"])

# параллельная программа, отвечайщая за удаление изменений в расписании
def weekdays():
    time_last = last_weekday()
    while True:
        if time_last != last_weekday():
            calls = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "schedule_calls")], limit=1)
            admins = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "admins")])
            last_start = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "last_start")])
            if calls:
                calls = json.loads(calls[0][0])
                admins = json.loads(admins[0][0])
                last_start = last_start[0][0]
            for key in admins:
                bot.send_message(key, f"Я ВРОДЕ КАК ЖИВОЙ\nЯ был запущен: {last_start}")
            today = datetime.now()
            today = f"{today.day}.{today.month}.{today.year}"
            if calls["edited"]["date"] != None:
                flag = False
                if len(calls["edited"]["date"]) == 1:
                    if calls["edited"]["date"][0] == today:
                        calls["edited"]["date"] = None
                        calls["edited"]["data"] = None
                        flag = True
                else:
                    find = calls["edited"]["date"].count(today)
                    if find:
                        calls["edited"]["date"].remove(today)
                        flag = True
                if flag:
                    print(BD_query.BD_query(get_sql(), "UPDATE", "info", where=[("theme", "=", "schedule_calls")], data=[("text", json.dumps(calls, indent=2))]))
            time_last = last_weekday()

            print("Смена дня " + days[time_last])
            answer = BD_query.BD_query(get_sql(), "SELECT", "classes", columns=["class_n", "class_b", "schedule"])
            for key in answer:
                schedule = json.loads(key[2])
                flag = False
                if schedule["edited"].get(days[time_last]):
                    schedule["edited"].pop(days[time_last])
                    flag = True

                if flag:
                    BD_query.BD_query(get_sql(), "UPDATE", "classes", 
                        where=[("class_n", "=", key[0]), ("class_b", "=", key[1])], 
                        data=[("schedule", json.dumps(schedule, indent=2))])
                    print(f"{key[0], key[1]}")
            print("Обработка расписания закончена")
        time_last = last_weekday()
        answers = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "answers")])
        start_settings = BD_query.BD_query(get_sql(), "SELECT", "info", columns="text", where=[("theme", "=", "start_settings")])
        if answers == []:
            raise "answers"
        else:
            answers = json.loads(answers[0][0])
            start_settings = json.loads(start_settings[0][0])
        time.sleep(30)
        requests.post(f'https://ya.ru')
        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"), len(answers))

thread1 = Thread(target=weekdays)
thread1.start()
while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e) 
        time.sleep(15)
    
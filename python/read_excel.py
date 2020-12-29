import BD_query
import config
import json
import xlrd

def erase_null(line):
    if str(type(line)) == "<class 'float'>":
        return int(line)
    return line

def is_num(line):
    try:
        float(line)
        return True
    except:
        
        return False
    
def is_class_name(classes, line):
    abc = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    line = line.strip().upper()
    size = len(line)
    if size <= 1 or size > 3:
        return False
    if size == 2 and is_num(line[0]):
        if classes.get((line[0])) != None:
            if line[1] in classes.get((line[0])):
                return True
    if size == 3 and is_num(line[0:2]) and line[2] in abc:
        if classes.get((line[0:2])) != None:
            if line[2] in classes.get((line[0:2])):
                return True
    
    return False

def next_line(text):
    text = text.strip()
    if len(text) == 0:
        return ""
    else:
        if text.find("\n") == -1:
            return text
        else:
            return text[0: text.find("\n")]

def next_word(text):
    text = text.strip().replace("\n", " ")
    if len(text) == 0:
        return ""
    else:
        if text.find(" ") != -1:
            return text[0: text.find(" ")].upper()
        else:
            return text.upper()

def read(path, bot, message):
    classes = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "classes")])
    chat_id = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="info", columns="text", where=[("theme", "=", "techers")])
    if chat_id == []:
        return None
    elif message.chat.id not in json.loads(chat_id[0][0]):
        bot.send_message(message.chat.id, "У вас нет прав изменять \nрасписание уроков!")
        return None
    if classes != []:
        classes = classes[0][0]
    classes = json.loads(classes)
    rb = xlrd.open_workbook(path, formatting_info=True)
    sheet = rb.sheet_by_index(0)
    day, chat_id, edited = (None, None, None)
    flag = False
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            line = str(sheet.cell_value(i, j)).strip().upper()
            NW = next_word(line)
            if NW != "/EDIT":
                continue
            line = line[len(NW):].strip()
            days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
            if line.find("ОСНОВНОЕ") != -1:
                edited = "standart"
            elif line.find("ИЗМЕНЕНИЯ") != -1:
                edited = "edited"
            else:
                continue
            chat_id = message.chat.id
            day = False
            for key in days:
                if line.find(key) != -1:
                    day = key
                    break
            flag = True
            break
            break
    if not flag:
        bot.send_message(message.chat.id, "В excel-файле не была найдена ячейка с указаниями к изменению данных")
        return None
    else:
        data = {}
        classes_in_excel = []
        for i in range(sheet.nrows):
            for j in range(sheet.ncols):
                key = sheet.cell_value(i, j)
                if is_class_name(classes, str(key)):
                    classes_in_excel.append(key)
                    data[key] = []
                    try:
                        for i1 in range(1, 17, 2):
                            if str(sheet.cell_value(i + i1, j)) == "":
                                data[key].append("-")
                                continue

                            lesson = f"{erase_null(sheet.cell_value(i + i1, j))} "
                            if sheet.cell_value(i + i1, j + 1):
                                lesson += f"({erase_null(sheet.cell_value(i + i1, j + 1))}"
                            if sheet.cell_value(i + i1 + 1, j + 1):
                                lesson += f", {erase_null(sheet.cell_value(i + i1 + 1, j + 1))})"
                            elif sheet.cell_value(i + i1, j + 1):
                                lesson += ")"
                            if str(sheet.cell_value(i + i1, j + 2)) == "/":
                                lesson += f" ({erase_null(sheet.cell_value(i + i1, j + 3))}"
                            if sheet.cell_value(i + i1 + 1, j + 3):
                                lesson += f", {erase_null(sheet.cell_value(i + i1 + 1, j + 3))})"
                            elif str(sheet.cell_value(i + i1, j + 2)) == "/":
                                lesson += ")"
                            if len(lesson) <= 5:
                                # print(lesson)
                            data[key].append(lesson)
                    except:
                        pass
                    while len(data[key]) and data[key][-1] == "-":
                        data[key].pop()
    answer = f"День: {day}\nРасписание: {edited}\nКлассы: {classes_in_excel}\nДанные: {data}"
    for i in range(100, len(answer), 100):
        bot.send_message(message.chat.id, answer[i - 100: i])
    return (data, edited, day)
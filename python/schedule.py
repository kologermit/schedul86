import BD_query
import config
import json
def weekday(message, bot, class_n, class_b, markup=None, answer=""):
    js = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", "classes", columns="schedule", where=[("class_n", "=", class_n), ("class_b", "=", class_b)])
    if js == []:
        return False
    js = json.loads(js[0][0])
    
    day = message.text
    if message.text in ["ПЯТНИЦА", "СУББОТА", "СРЕДА"]:
        day = day[:len(day) - 1] + "У"
    if answer == '':
        answer = f"Расписание уроков {class_n}{class_b} на {day.lower()}:\n"
    i = 1
    for data in js["standart"][message.text]:
        answer += str(i) + ". " + data + "\n"
        i += 1
    if js["edited"].get(message.text) == None:
        answer += "Изменений нет"
    else:
        answer += "Именёния таковы:\n"
        i = 1
        for data in js["edited"][message.text]:
            answer += str(i) + ". " + data + "\n"
            i += 1
    if markup:
        bot.send_message(message.chat.id, answer, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, answer)
    BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "UPDATE", "users", data=[('class_n', None), ('class_b', None)], where=[("id", "=", message.chat.id)])

def alldays(message, bot, status, markup):
    js = BD_query.BD_query(BD_query.get_sql(**config.mysql_config), "SELECT", table="classes", columns="schedule", where=[("class_n", "=", status["class_n"]), ("class_b", "=", status["class_b"])])
    if js == []:
        return
    js = json.loads(js[0][0])
    answer = "Расписание на неделю:\n"
    arr = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
    for data in arr:
        answer += data.capitalize() + ":\n"
        i = 1
        for data2 in js["standart"][data]:
            answer += f"{i}. {data2}\n"
            i += 1
        answer += '\n'
    answer += '\n'
    if js["edited"] == {}:
        answer += "\nИзменений нет"
    else:
        answer += "\nИзменения:\n"
        for data in arr:
            if js["edited"].get(data) != None:
                answer += data.capitalize() + ":\n"
                i = 1
                for data2 in js["edited"][data]:
                    answer += "{0}. {1}\n".format(i, data2)
                    i += 1
                answer += "\n\n"
    bot.send_message(message.chat.id, answer, reply_markup=markup)
    return   
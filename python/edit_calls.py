from config import mysql_config
import BD_query
from BD_query import get_sql
import json

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

def next_line(text):
    text = text.strip()
    if len(text) == 0:
        return ""
    else:
        if text.find("\n") == -1:
            return text
        else:
            return text[0: text.find("\n")]

def is_date(line):
	if split_date(line) == False:
		return False
	day, month, year = split_date(line)
	
	if not (month >= 1 and month <= 12):
		return False

	def is_w_year(year):
		return (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0)

	if not (month in [1, 3, 5, 7, 8, 10, 12] and day >= 1 and day <= 31) \
	and not (month in [4, 6, 9, 11] and day >= 1 and day <= 30) \
	and not (month == 2 and is_w_year(year) and day >= 1 and day <= 29) \
	and not (month == 2 and is_w_year(year) == False and day >= 1 and day <= 28):
		return False
	return True

def is_num(line):
    try:
        float(line)
        return True
    except:
        return False

def erace_double_space(line):
	while line.find("  ") != -1:
		line.replace("  ", " ")
	return line

def main(bot, message):
	date, edited = None, None
	message.text = erace_double_space(message.text.strip())
	NW = next_word(next_word(next_line(message.text.upper()))[1]) 
	if NW[0] in ["ИЗМЕНЕНИЕ", "ИЗМЕНЁННОЕ", "ИЗМЕНЕНИЯ"]:
		edited = "edited"
		e = NW[0]
	elif NW[0] in ["СТАНДАРТНОЕ", "ОСНОВНОЕ"]:
		edited = "standart"
		e = NW[0]
	else:
		bot.send_message(message.chat.id, "Параметр -e не соответствует нужным!")
		return False
	# dd.mm.yyyy
	date = NW[1].split(" ")
	data = BD_query.BD_query(get_sql(**mysql_config), "SELECT", "info", where=[("theme", "=", "schedule_calls")], limit=1)
	if not data:
		return False
	else:
		data = json.loads(data[0][0])
	if len(date) == 0 and edited == 'edited':
		if edited == 'edited':
			data["edited"]["data"] = None
			data["edited"]["date"] = None
		else:
			data["standart"] = []
		result = BD_query.BD_query(get_sql(**mysql_config), "UPDATE", "info", data=[("text", json.dumps(data, indent=2))], where=[("theme", "=", "schedule_calls")])
		bot.send_message(message.chat.id, f"В команде не был найден параметр -d. Расписание на {e} удалено!")
		return result
	if edited == 'edited':
		for key in date:
			
			if is_date(key):
				day, month, year = split_date(key)
				if data["edited"]["date"] == None:
					data["edited"]["date"] = []
				data["edited"]["date"].append(f"{day}.{month}.{year}")
		calls = []
		message.text = message.text[len(next_line(message.text)):].strip()
		while message.text:
			NL = next_line(message.text)
			calls.append(NL)
			message.text = message.text[len(NL):].strip()
		if len(calls) == 0:
			return False
		data["edited"]["data"] = calls
	else:
		calls = []
		message.text = message.text[len(next_line(message.text)):].strip()
		while message.text:
			NL = next_line(message.text)
			calls.append(NL)
			message.text = message.text[len(NL):].strip()
		data["standart"] = calls
	result = BD_query.BD_query(get_sql(**mysql_config), "UPDATE", "info", data=[("text", json.dumps(data, indent=2))],  where=[("theme", "=", "schedule_calls")])
	bot.send_message(message.chat.id, json.dumps(data, indent=2))
	return result
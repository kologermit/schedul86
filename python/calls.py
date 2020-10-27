import BD_query
import json
def main(sql, message, bot):
    query = BD_query.BD_query(sql, "SELECT", "info", columns="text", where=[("theme", "=", "schedule_calls")])
    if query != []:
        query = json.loads(query[0][0])
        answer = "Расписание звонков: \n"
        for i in range(0, len(query['standart'])):
            answer += f"{i + 1}. {query['standart'][i]}\n"
        answer += "\n"
        if query['edited']['date'] == None:
            answer += "Изменений нет"
        else:

            answer += f"Изменения на {query['edited']['date'][0]}"
            for i in range(1, len(query['edited']['date'])):
                answer += f", {query['edited']['date'][i]}"
            answer += ":\n"
            for i in range(0, len(query['edited']["data"])):
                answer += f"{i + 1}. {query['edited']['data'][i]}\n"
        bot.send_message(message.chat.id, answer)
        return True
    return False
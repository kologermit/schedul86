import json
import mysql.connector
import BD_query
import time
import config
def get_sql():
    while(True):
        try:
            sql = mysql.connector.connect(**config.mysql_config
    )
        except Exception as err:
            
            print(err)
            print("Нет подключения к mysql")
            time.sleep(3)
        else:
            break
    return sql
file = BD_query.BD_query(get_sql(), "SELECT", "info")[0][0]
js = json.loads(file)
schedule = json.dumps(json.loads("""{
    "standart": {
            "ПОНЕДЕЛЬНИК": [        ],
            "ВТОРНИК": [        ],        
            "СРЕДА": [        ],        
            "ЧЕТВЕРГ": [        ],        
            "ПЯТНИЦА": [        ],        
            "СУББОТА": [        ]    
            },    
    "edited": {    
    }
}"""), indent=2)
data = []
for d in js.keys():
    for key in js[d]:
        print(f"class_n: {d}, class_b: {key}")
        data.append({"class_n": d, "class_b": key, "schedule": schedule})
print(BD_query.BD_query(get_sql(), "INSERT", "classes", data=data))
from BD_query import BD_query
from config import mysql_config
from BD_query import get_sql
import json
data = []
classes = BD_query(get_sql(**mysql_config), "UPDATE", "classes", data=[("featured", json.dumps(data, indent=2))], where=[("class_n", ">=", 0)])
print(classes)
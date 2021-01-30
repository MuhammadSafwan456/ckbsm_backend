from database_layer.database import execute_query
from config import database_config

# print(database_config.get_config("DB_USERNAME"))



print("first")
a = execute_query("SHOW TABLES")
print("A",a)
for i in a:
    print("i",i)


print("_______________________________Second")
a = execute_query("SHOW TABLES")
print("A",a)
for i in a:
    print("j",i)





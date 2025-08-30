import mysql.connector as mysql
import settings as s
import sys

connection = mysql.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )

if connection.is_connected():
    pass
else:
    sys.exit(1)

try:
    cursor = connection.cursor()

    # columns_query = "SHOW COLUMNS FROM Quant.BTCUSD;"
    # cursor.execute(columns_query)
    # columns = cursor.fetchone()

    select_query = "SELECT * FROM Quant.BTCUSD ORDER BY id ASC;"
    cursor.execute(select_query)
    data = cursor.fetchall()

    cursor.close()
except Exception as e:
    print("Something happend: ", e)
    connection.close()
    sys.exit(1)


top_ten = 10
index = 0
while index < top_ten:
    print(data[index])
    index += 1




connection.close()
import yfinance as yf
import mysql.connector as mysql
import settings as s

asset_ticker = "EURUSD=X"
ref_ticker = yf.Ticker(asset_ticker)
data = ref_ticker.history(period="max")
print(data.columns)

connection = mysql.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )
if connection.is_connected:
    print("Connection Successful")

cursor = connection.cursor()

table_name = asset_ticker.replace("=", "")
print(table_name)

try:
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            PricingDate DATETIME NOT NULL,
            Open DOUBLE,
            High DOUBLE,
            Low DOUBLE,
            Close DOUBLE,
            Volume DOUBLE
        )
    """)

    for index, row in data.iterrows():
        cursor.execute(
            f"""
            INSERT INTO {table_name} (PricingDate, Open, High, Low, Close, Volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (index.to_pydatetime(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
        )

    connection.commit()
    print("Everything went well. Check the table")
except Exception as e:
    print("Something failed with: ", e)
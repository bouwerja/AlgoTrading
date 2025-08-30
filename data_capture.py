import yfinance as yf
import mysql.connector as mysql
import settings as s
import sys

connection = mysql.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )

try:
    ticker_select = """
SELECT DISTINCT 
    Symbol
FROM Quant.MarketMaster
"""
    cursor = connection.cursor()
    cursor.execute(ticker_select)
    ticker_list = cursor.fetchall()

    ticker_insert = """
INSERT INTO Quant.ScriptsLogs (ScriptName, Status)
VALUES ('data_capture', 'Success')
"""
    cursor.execute(ticker_insert)
    connection.commit()
    cursor.close()
except Exception as e:
    connection.close()
    sys.exit(1)

for ticker in ticker_list:
    ticker_symbol = ticker[0]
    ref_ticker = yf.Ticker(ticker_symbol)
    data = ref_ticker.history(period="1d")

    cursor = connection.cursor()
    
    table_name = ticker_symbol.replace("=", "")
    
    try:
        for index, row in data.iterrows():
            cursor.execute(
                f"""
                INSERT INTO {table_name} (PricingDate, Open, High, Low, Close, Volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (index.to_pydatetime(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
            )
    
        connection.commit()
        cursor.close()
    except Exception as e:
        connection.close()
        sys.exit(1)

connection.close()
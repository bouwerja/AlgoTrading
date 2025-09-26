import mysql.connector as mysql
import settings as s

connection = mysql.connect(
    host=s.DATABASE_HOSTNAME,
    user=s.ACTIVE_USERNAME,
    password=s.ACTIVE_USER_PWD,
    database=s.ACTIVE_DATABASE,
)

if connection.is_connected():
    print("Connected")


def load_data(ticker=None, rows=10, sort_order="ASC", year_value=1900):
    """
    Load financial data for a given ticker from the database.

    Args:
        ticker (str): The ticker symbol (e.g., "BTCUSD"). Must not be None.
        rows (int): Number of rows to fetch. Use 0 to fetch everything.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains:
            - ID (int)
            - DateCreated (datetime)
            - Close (float)
            - Change (float)
            - Direction (str: "Bull" or "Bear")

    Raises:
        Exception: If the query or database connection fails.
    """
    if ticker is None:
        return "Please provide a ticker value"

    try:
        conn = mysql.connect(
            host=s.DATABASE_HOSTNAME,
            user=s.ACTIVE_USERNAME,
            password=s.ACTIVE_USER_PWD,
            database=s.ACTIVE_DATABASE,
        )
        cursor = conn.cursor(buffered=True)

        ticker = ticker.upper()
        cursor.execute(
            f"SELECT * FROM Quant.{ticker} WHERE YEAR(PricingDate) >= {year_value} ORDER BY 1 {sort_order}"
        )

        if rows == 0:
            data = cursor.fetchall()
        else:
            data = cursor.fetchall()[:rows]  # slice

        result = []
        closes = []
        opens = []

        for i, row in enumerate(data):
            row: dict = row
            dic_Data = {
                "ID": row[0],
                "DateCreated": row[1],
                "Close": row[5],
                "Open": row[2],
            }

            closes.append(row[5])
            opens.append(row[2])

            if i == 0:
                dic_Data["Change"] = 0.00
            else:
                dic_Data["Change"] = closes[i] - opens[i]

            dic_Data["Direction"] = "Bull" if dic_Data["Change"] > 0 else "Bear"
            dic_Data["PrevDirection"] = "Bull" if closes[i - 1] > 0 else "Bear"
            result.append(dic_Data)

        cursor.close()
        conn.close()
        return result

    except Exception as e:
        return "Exception occurred", e

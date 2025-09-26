from DataOperations import load_data
import numpy as np

full_data = load_data("OH_GBPUSDX", rows=0, sort_order="ASC", year_value=2025)
date_list = []
price_list = []
direction_list = []


for i, row in enumerate(full_data):
    row: dict = row
    date_list.append(row["DateCreated"])
    price_list.append(row["Change"])
    direction_list.append(row["Direction"])


print("Amount of dates: ", len(price_list))


def cumm_Probabilities(p_trails=0):
    prob_dict = {}
    for i in range(p_trails):
        if i == 0:
            prob_dict[f"{i + 1}"] = geometric_prob(i)
        else:
            prob_dict[f"{i + 1}"] = geometric_prob(i) + prob_dict[f"{i}"]

    return prob_dict


def geometric_prob(trails):
    """
    Geometric Distribution

    The geometric distribution models the number of failures
      before the first success in a sequence of independent Bernoulli trials.

    Definitions:
      Success = observing a 1
      Failure = observing a 0
      p = probability of success (observing a 1)

    Probability Mass Function (PMF):
      P(X = n) = (1-p)^n * p
        - X = n means there are n failures (zeros) before the first success (1)

    Cumulative Distribution Function (CDF):
      P(X <= n) = 1 - (1-p)^(n+1)
        - probability that the first success occurs within n+1 trials

    Memoryless Property:
      The probability of success on the next trial is always p,
      regardless of how many failures (zeros) have already occurred.
    """

    # set positive values as bull
    # calculate p of bull
    list_length = len(direction_list)
    bull_length = sum(1 for x in direction_list if x == "Bull")
    p_bull = float(bull_length / list_length)

    return (
        ((1 - p_bull) ** (trails)) * p_bull,
        (1 / p_bull),
        ((1 - p_bull) / (p_bull**2)),
    )


_, geo_mean, geo_var = geometric_prob(10)
geo_std = np.sqrt(geo_var)
geo_error = (geo_std / geo_std) / 100

portfolio_status = {
    "profitablePositions": 0,
    "positionsOpened": 0,
    "openPosition": False,
    "openDate": None,
    "closeDate": None,
    "openPrice": 0,
    "stoploss": 0,
    "StopPrice": 0,
    "profitLevel": 0,
    "ProfitPrice": 0,
    "currentValue": 100,
    "unitsBaught": 0,
    "lossValue": geo_error,
    "TableID": None,
}
inter_list = []

for i, row in enumerate(full_data):
    row: dict = row
    direction = row["Direction"]
    date_opened = row["DateCreated"]
    close_price = float(row["Close"])
    open_price = float(row["Open"])
    if close_price == 0.0:
        pass

    if len(inter_list) == 0:
        inter_list.append(direction)
    else:
        if len(inter_list) <= 2:
            if direction == inter_list[-1]:
                inter_list.append(direction)
            else:
                inter_list = []
        else:
            directionPrediction = "Bear"
            if inter_list[-1] == "Bear":
                directionPrediction = "Bull"

            if (
                portfolio_status["openPosition"] is False
                and directionPrediction == "Bull"
            ):
                """
                This opens a new position
                """
                portfolio_status["TableID"] = row["ID"]
                portfolio_status["openPosition"] = True
                portfolio_status["positionsOpened"] += 1
                portfolio_status["openPrice"] = open_price
                portfolio_status["openDate"] = date_opened
                portfolio_status["closeDate"] = None
                portfolio_status["unitsBaught"] = (
                    portfolio_status["currentValue"] / open_price
                )
                portfolio_status["stoploss"] = portfolio_status["currentValue"] - (
                    portfolio_status["currentValue"] * portfolio_status["lossValue"]
                )
                portfolio_status["profitLevel"] = portfolio_status[
                    "currentValue"
                ] + portfolio_status["currentValue"] * (
                    2 * portfolio_status["lossValue"]
                )
                portfolio_status["StopPrice"] = (
                    portfolio_status["stoploss"] / portfolio_status["unitsBaught"]
                )
                portfolio_status["ProfitPrice"] = (
                    portfolio_status["profitLevel"] / portfolio_status["unitsBaught"]
                )
                print("Opened Trade: ")
                print(portfolio_status)

            elif portfolio_status["openPosition"] is True:
                # always update current value first
                portfolio_status["currentValue"] = (
                    portfolio_status["unitsBaught"] * close_price
                )

                # check stoploss or take profit
                if (
                    portfolio_status["currentValue"] <= portfolio_status["stoploss"]
                    or portfolio_status["currentValue"]
                    >= portfolio_status["profitLevel"]
                ):
                    # record profitable trades
                    if (
                        portfolio_status["currentValue"]
                        >= portfolio_status["profitLevel"]
                    ):
                        portfolio_status["profitablePositions"] += 1

                    # close trade
                    portfolio_status["openPrice"] = 0
                    portfolio_status["unitsBaught"] = 0
                    portfolio_status["stoploss"] = 0
                    portfolio_status["profitLevel"] = 0
                    portfolio_status["openPosition"] = False
                    portfolio_status["closeDate"] = date_opened
                    print("Closed Trade: ")
                    print(portfolio_status)
            inter_list = []


# plt.figure(dpi=150)
# bars = plt.bar(cumm_prob.keys(), cumm_prob.values())
# plt.title("Change in Price")
#
# for bar in bars:
#     height = bar.get_height()
#     plt.text(
#         bar.get_x() + bar.get_width() / 2,
#         height,
#         f"{height:.2f}",
#         ha="center",
#         va="bottom",
#     )
#
# plt.show()

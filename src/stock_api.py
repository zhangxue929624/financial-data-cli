
import yfinance as yf
def get_stock_info(symbol):
    """
    获取股票行情数据。

    参数：
        symbol: 股票代码，例如 AAPL

    返回：
        包含股票行情的字典
    """

    stock = yf.Ticker(symbol)

    history = stock.history(period="5d")

    if history.empty:
        raise ValueError("没有查询到股票数据")

    latest = history.iloc[-1]

    previous = (
        history.iloc[-2]
        if len(history) >= 2
        else None
    )

    price = float(latest["Close"])

    change = None

    if previous is not None:

        previous_close = float(
            previous["Close"]
        )

        if previous_close != 0:

            change = (
                (price - previous_close)
                / previous_close
                * 100
            )

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "volume": int(latest["Volume"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"])
    }


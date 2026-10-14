
import yfinance as yf

from src.formatter import display_stock
from src.stock_tool import get_stock_info

from src.stock_repository import (
    save_stock,
    save_stock_price,
    get_stock_history,
    get_average_close_price,
    get_highest_lowest_price
)


def get_symbols():
    """读取并整理用户输入的股票代码。"""

    symbols = input(
        "请输入股票代码（多个用逗号分隔）："
    )

    stock_list = [
        symbol.strip().upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]

    return stock_list


def show_stock_info():
    """功能1：保留原来的批量行情查询功能。"""

    stock_list = get_symbols()

    if not stock_list:
        print("请输入有效的股票代码")
        return

    for symbol in stock_list:
        try:
            data = get_stock_info(symbol)
            display_stock(data)

        except Exception as error:
            print(f"{symbol} 查询失败：{error}")


def save_stock_history():
    """功能2：获取并保存股票历史行情。"""

    symbol = input("请输入股票代码：").strip().upper()
    market = input("请输入市场（例如 NASDAQ）：").strip().upper()
    company_name = input("请输入公司名称：").strip()
    period = input("请输入历史周期（例如 1mo、3mo、1y）：").strip()

    if not symbol or not market or not company_name:
        print("股票代码、市场和公司名称不能为空")
        return

    if not period:
        period = "1mo"

    # 从 yfinance 获取历史行情
    ticker = yf.Ticker(symbol)
    history = ticker.history(
        period=period,
        auto_adjust=False
    )

    if history.empty:
        print("没有获取到历史行情")
        return

    # 保存股票基本信息，并获取 stock_id
    stock_id = save_stock(
        symbol=symbol,
        company_name=company_name,
        market=market
    )

    saved_count = 0

    # 逐日保存行情
    for trade_date, row in history.iterrows():

        save_stock_price(
            stock_id=stock_id,
            trade_date=trade_date.date(),
            open_price=float(row["Open"]),
            high_price=float(row["High"]),
            low_price=float(row["Low"]),
            close_price=float(row["Close"]),
            volume=int(row["Volume"])
        )

        saved_count += 1

    print(f"{symbol} 行情保存完成，共处理 {saved_count} 条记录")


def query_stock_history():
    """功能3：查询数据库中的历史行情。"""

    symbol = input("请输入股票代码：").strip().upper()
    market = input("请输入市场：").strip().upper()

    if not symbol or not market:
        print("股票代码和市场不能为空")
        return

    history = get_stock_history(
        symbol=symbol,
        market=market,
        limit=30
    )

    if not history:
        print("数据库中没有找到相关行情")
        return

    for row in history:
        print(
            f"日期：{row['trade_date']} | "
            f"开盘：{row['open_price']} | "
            f"收盘：{row['close_price']} | "
            f"成交量：{row['volume']}"
        )


def query_average_price():
    """功能4：查询平均收盘价。"""

    symbol = input("请输入股票代码：").strip().upper()
    market = input("请输入市场：").strip().upper()

    if not symbol or not market:
        print("股票代码和市场不能为空")
        return

    average = get_average_close_price(
        symbol=symbol,
        market=market
    )

    if average is None:
        print("没有找到行情数据")
        return

    print(f"{symbol} 平均收盘价：{average:.4f}")


def query_price_range():
    """功能5：查询最高价和最低价。"""

    symbol = input("请输入股票代码：").strip().upper()
    market = input("请输入市场：").strip().upper()

    if not symbol or not market:
        print("股票代码和市场不能为空")
        return

    result = get_highest_lowest_price(
        symbol=symbol,
        market=market
    )

    if result["highest_price"] is None:
        print("没有找到行情数据")
        return

    print(f"股票代码：{symbol}")
    print(f"最高价：{result['highest_price']}")
    print(f"最低价：{result['lowest_price']}")


def main():
    """程序主入口。"""

    while True:

        print("\n========== 股票行情系统 ==========")
        print("1. 获取实时或近期股票行情")
        print("2. 获取并保存股票历史行情")
        print("3. 查询数据库中的历史行情")
        print("4. 查询平均收盘价")
        print("5. 查询最高价和最低价")
        print("0. 退出程序")

        choice = input("请选择功能：").strip()

        if choice == "0":
            print("程序已退出")
            break

        actions = {
            "1": show_stock_info,
            "2": save_stock_history,
            "3": query_stock_history,
            "4": query_average_price,
            "5": query_price_range
        }

        action = actions.get(choice)

        if action is None:
            print("无效选项，请重新输入")
            continue

        try:
            action()

        except Exception as error:
            print(f"操作失败：{error}")


if __name__ == "__main__":
    main()

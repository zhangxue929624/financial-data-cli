
from src.formatter import display_stock
from src.stock_api import get_stock_info


def main():
    """
    主程序：
    接收输入并批量查询股票。
    """

    symbols = input(
        "请输入股票代码（多个用逗号分隔）："
    )

    stock_list = [
        symbol.strip().upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]

    if not stock_list:

        print("请输入有效的股票代码")

        return

    for symbol in stock_list:

        try:

            data = get_stock_info(symbol)

            display_stock(data)

        except Exception as error:

            print(
                f"{symbol} 查询失败: {error}"
            )


if __name__ == "__main__":

    main()
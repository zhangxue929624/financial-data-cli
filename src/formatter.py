def display_stock(data):
    """
    将股票行情打印到终端。
    """

    print("-" * 30)

    print(
        f"Stock:  {data['symbol']}"
    )

    print(
        f"Price:  ${data['price']:.2f}"
    )

    if data["change"] is not None:

        print(
            f"Change: {data['change']:+.2f}%"
        )

    else:

        print("Change: N/A")

    print(
        f"Volume: {data['volume']:,}"
    )

    print(
        f"High:   ${data['high']:.2f}"
    )

    print(
        f"Low:    ${data['low']:.2f}"
    )

    print("-" * 30)


# src/formatter.py

def display_stock(data):

    print("-" * 30)
    print(f"Stock:  {data['symbol']}")
    print(f"Price:  ${data['price']:.2f}")

    if data["change"] is not None:
        print(f"Change: {data['change']:+.2f}%")
    else:
        print("Change: N/A")

    print(f"Volume: {data['volume']:,}")
    print(f"High:   ${data['high']:.2f}")
    print(f"Low:    ${data['low']:.2f}")
    print("-" * 30)



from src.database import get_connection


def save_stock(symbol, company_name, market):
    """
    保存股票基本信息。

    如果股票已经存在，则更新公司名称。
    如果股票不存在，则插入新记录。

    返回：
        股票在 stocks 表中的 id。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
                INSERT INTO stocks
                    (symbol, company_name, market)
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id = LAST_INSERT_ID(id),
                    company_name = %s
            """

            cursor.execute(
                sql,
                (symbol, company_name, market, company_name)
            )

            stock_id = cursor.lastrowid

        connection.commit()
        return stock_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_stock_price(
    stock_id,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
):
    """
    保存某只股票某一天的行情。

    如果该股票当天的行情已经存在，
    则更新原有数据，避免重复插入。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
                INSERT INTO stock_prices
                    (
                        stock_id,
                        trade_date,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume
                    )
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    open_price = %s,
                    high_price = %s,
                    low_price = %s,
                    close_price = %s,
                    volume = %s
            """

            cursor.execute(
                sql,
                (
                    stock_id,
                    trade_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_stock_history(symbol, market=None, limit=30):
    """
    查询指定股票最近的历史行情。

    参数：
        symbol: 股票代码
        market: 股票市场，默认不指定
        limit: 最多返回多少条记录

    返回：
        字典列表。
    """

    limit = int(limit)

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
                SELECT
                    s.symbol,
                    s.company_name,
                    s.market,
                    p.trade_date,
                    p.open_price,
                    p.high_price,
                    p.low_price,
                    p.close_price,
                    p.volume
                FROM stocks AS s
                INNER JOIN stock_prices AS p
                    ON s.id = p.stock_id
                WHERE s.symbol = %s
            """

            params = [symbol]

            if market is not None:
                sql += " AND s.market = %s"
                params.append(market)

            sql += """
                ORDER BY p.trade_date DESC
                LIMIT %s
            """

            params.append(limit)

            cursor.execute(sql, tuple(params))

            return cursor.fetchall()

    finally:
        connection.close()


def get_average_close_price(symbol, market=None):
    """
    计算指定股票所有已保存行情的平均收盘价。

    返回：
        Decimal 或 None。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
                SELECT
                    AVG(p.close_price) AS average_close
                FROM stocks AS s
                INNER JOIN stock_prices AS p
                    ON s.id = p.stock_id
                WHERE s.symbol = %s
            """

            params = [symbol]

            if market is not None:
                sql += " AND s.market = %s"
                params.append(market)

            cursor.execute(sql, tuple(params))

            result = cursor.fetchone()

            return result["average_close"]

    finally:
        connection.close()


def get_highest_lowest_price(symbol, market=None):
    """
    查询指定股票所有已保存行情中的
    最高价和最低价。

    返回：
        {
            "highest_price": Decimal 或 None,
            "lowest_price": Decimal 或 None
        }
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
                SELECT
                    MAX(p.high_price) AS highest_price,
                    MIN(p.low_price) AS lowest_price
                FROM stocks AS s
                INNER JOIN stock_prices AS p
                    ON s.id = p.stock_id
                WHERE s.symbol = %s
            """

            params = [symbol]

            if market is not None:
                sql += " AND s.market = %s"
                params.append(market)

            cursor.execute(sql, tuple(params))

            return cursor.fetchone()

    finally:
        connection.close()

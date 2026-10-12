
"""
测试 database.py 中的 MySQL 数据库连接功能。

运行命令：
python -m pytest tests/test_database.py -v
"""

import pymysql
import pytest

from src.database import get_connection


def test_database_connection():
    """测试能否成功连接 MySQL。"""

    connection = get_connection()

    try:
        assert connection is not None
        assert connection.open

        print("\nMySQL 数据库连接成功")

    finally:
        connection.close()


def test_database_version():
    """测试能否查询 MySQL 版本。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")

            result = cursor.fetchone()

            assert result is not None
            assert result["version"]

            print(f"\nMySQL 版本：{result['version']}")

    finally:
        connection.close()


def test_database_name():
    """测试当前连接的数据库是否为 financial_data。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS db_name")

            result = cursor.fetchone()

            assert result["db_name"] == "financial_data"

            print(f"\n当前数据库：{result['db_name']}")

    finally:
        connection.close()


def test_required_tables():
    """测试数据库中是否存在 stocks 和 stock_prices。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")

            result = cursor.fetchall()

            # DictCursor 返回字典，取出每行的表名
            table_names = {
                next(iter(row.values()))
                for row in result
            }

            assert "stocks" in table_names
            assert "stock_prices" in table_names

            print(f"\n数据库中的表：{table_names}")

    finally:
        connection.close()

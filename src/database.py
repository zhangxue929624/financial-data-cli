
import os

import pymysql
from dotenv import load_dotenv


# 1. 加载 .env 文件中的环境变量
load_dotenv()


def get_connection():
    """
    创建并返回 MySQL 数据库连接。

    返回：
        pymysql.connections.Connection 对象

    异常：
        数据库连接失败时，向调用方抛出异常。
    """

    # 2. 读取数据库连接配置
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = os.environ["DB_NAME"]

    # 3. 建立 MySQL 数据库连接
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

    # 4. 返回连接对象
    return connection

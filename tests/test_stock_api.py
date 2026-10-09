# tests/test_stock_api.py

from src.stock_api import get_stock_info


def test_get_stock_info():

    # 调用真实的股票查询函数
    data = get_stock_info("AAPL")

    # 检查返回的数据
    assert data["symbol"] == "AAPL"
    assert data["price"] > 0
    assert data["volume"] >= 0
    assert data["high"] >= data["low"]

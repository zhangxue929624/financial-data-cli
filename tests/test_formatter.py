from src.formatter import display_stock


def test_display_stock(capsys):

    # 准备模拟股票数据
    data = {
        "symbol": "AAPL",
        "price": 250.0,
        "change": 1.25,
        "volume": 45000000,
        "high": 253.5,
        "low": 247.2
    }

    # 调用正式代码中的函数
    display_stock(data)

    # 获取打印到终端的内容,这里的 capsys 是 pytest 提供的功能，可以捕获 print() 的输出。
    output = capsys.readouterr().out

    # 验证输出是否正确
    assert "AAPL" in output
    assert "$250.00" in output
    assert "+1.25%" in output
    assert "45,000,000" in output
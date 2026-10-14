import akshare as ak

def get_stock_info(symbol):
    """使用 AKShare 获取美股日线行情（国内直连不限流）"""
    """自动识别并获取 A股(6位数字)或 美股（英文字母）的最新行情数据"""
    try:
        # 清理可能附带的市场前缀或后缀（比如把 '600036.SH' 变成纯数字 '600036'）
        
        clean_symbol = symbol.split(".")[0].strip()
# ==========================================
        # 分支 1：如果是纯数字（例如 600036），走中国 A 股接口！
        # ==========================================
        if clean_symbol.isdigit():
            df = ak.stock_zh_a_hist(symbol=clean_symbol, period="daily", adjust="")
            if df.empty:
                return {"error": f"没有查询到 A 股 {clean_symbol} 的数据"}
                
            latest = df.iloc[-1]
            # 惊喜：A股接口直接自带算好的中文列，连涨跌幅都不用我们自己算！
            return {
                "symbol": clean_symbol,
                "market": "A股 (CNY)",
                "price": round(float(latest["收盘"]), 2),
                "change_percent": round(float(latest["涨跌幅"]), 2),
                "volume": int(latest["成交量"]),
                "high": round(float(latest["最高"]), 2),
                "low": round(float(latest["最低"]), 2)
            }


        # ==========================================
        # 分支 2：如果是英文字母（例如 AAPL, NVDA），走美股接口！
        # ==========================================
        else:
            df = ak.stock_us_daily(symbol=clean_symbol, adjust="")
            if df.empty:
                return {"error": f"没有查询到美股 {clean_symbol} 的数据"}
                
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) >= 2 else None
            
            price = float(latest["close"])
            change_percent = None
            if previous is not None and float(previous["close"]) != 0:
                prev_close = float(previous["close"])
                change_pct = (price - prev_close) / prev_close * 100
                
            return {
                "symbol": clean_symbol,
                "market": "美股 (USD)",
                "price": round(price, 2),
                "change_percent": round(change_pct, 2) if change_pct is not None else None,
                "volume": int(latest["volume"]),
                "high": round(float(latest["high"]), 2),
                "low": round(float(latest["low"]), 2)
            }
        
    except Exception as e:
        return {"error": f"获取行情失败: {str(e)}"}
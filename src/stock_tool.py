import akshare as ak
import os

# 强制绕过本地代理，保证国内直连顺畅
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

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
            market_name = "A股 (CNY)"
            if clean_symbol.startswith("6"):
                sina_symbol = f"sh{clean_symbol}"
            else:
                sina_symbol = f"sz{clean_symbol}"

            # 调用 AKShare 的新浪 A 股日线接口（极其稳定，不走东方财富）
            df = ak.stock_zh_a_daily(symbol=sina_symbol, adjust="")
            
        else:
            market_name = "美股 (USD)"
            sina_symbol = clean_symbol.upper()
            # 调用 AKShare 的新浪美股日线接口
            df = ak.stock_us_daily(symbol=sina_symbol, adjust="")
        
            
        if df.empty:
            return {"error": f"没有查询到标的 {clean_symbol} 的数据"}
            
    
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) >= 2 else None
        
        price = float(latest["close"])
        change_pct = None
        if previous is not None and float(previous["close"]) != 0:
            prev_close = float(previous["close"])
            change_pct = (price - prev_close) / prev_close * 100
            
        return {
            "symbol": sina_symbol,
            "market": market_name,
            "date": str(latest["date"])[:10],
            "price": round(price, 2),
            "change_percent": f"{round(change_pct, 2)}%" if change_pct is not None else None,
            "volume": int(latest["volume"]),
            "high": round(float(latest["high"]), 2),
            "low": round(float(latest["low"]), 2)
        }
        
    except Exception as e:
        return {"error": f"获取行情失败: {str(e)}"}
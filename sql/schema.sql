
-- ==========================================
-- 股票行情数据库初始化脚本
-- 项目：financial-data-cli
-- ==========================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS financial_data
CHARACTER SET utf8mb4;

-- 2. 选择数据库
USE financial_data;


-- ==========================================
-- 3. 股票基本信息表
-- ==========================================

CREATE TABLE IF NOT EXISTS stocks (

    -- 股票唯一ID
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    -- 股票代码
    symbol VARCHAR(20) NOT NULL,

    -- 公司名称
    company_name VARCHAR(100) NOT NULL,

    -- 所属市场
    market VARCHAR(20) NOT NULL,

    -- 同一个市场内，股票代码不能重复
    UNIQUE KEY uk_market_symbol (market, symbol)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ==========================================
-- 4. 股票每日行情表
-- ==========================================

CREATE TABLE IF NOT EXISTS stock_prices (

    -- 行情记录唯一ID
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    -- 对应stocks表中的股票ID
    stock_id BIGINT NOT NULL,

    -- 交易日期
    trade_date DATE NOT NULL,

    -- 开盘价
    open_price DECIMAL(12,4) NOT NULL,

    -- 最高价
    high_price DECIMAL(12,4) NOT NULL,

    -- 最低价
    low_price DECIMAL(12,4) NOT NULL,

    -- 收盘价
    close_price DECIMAL(12,4) NOT NULL,

    -- 成交量
    volume BIGINT,

    -- 同一股票同一天只能有一条行情
    UNIQUE KEY uk_stock_date (stock_id, trade_date),

    -- 外键：关联股票基本信息表
    CONSTRAINT fk_stock_prices_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id),

    -- 用于按日期查询
    INDEX idx_trade_date (trade_date)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

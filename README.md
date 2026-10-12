# Financial Data CLI

基于 **Python + MySQL + yfinance** 开发的股票行情命令行管理系统。

项目通过 Yahoo Finance 获取股票行情数据，使用 MySQL 保存股票基本信息和历史行情，并提供查询、统计和数据更新功能。

## 1. 项目简介

Financial Data CLI 是一个面向金融数据处理的 Python 学习项目，主要用于实践：

- Python 模块化开发
- 第三方 API 数据获取
- MySQL 数据库设计与操作
- Python 与 MySQL 数据交互
- SQL 查询和数据统计
- 自动化测试
- Git 和 GitHub 版本管理

项目采用分层设计，将行情获取、数据存储、数据展示和程序入口分离，便于维护和扩展。

## 2. 技术栈

| 技术 | 用途 |
|---|---|
| Python | 项目开发语言 |
| yfinance | 获取股票行情 |
| MySQL 8.0 | 关系型数据库 |
| PyMySQL | Python 连接 MySQL |
| python-dotenv | 管理环境变量 |
| Pandas | 处理行情数据 |
| pytest | 自动化测试 |
| Git / GitHub | 代码版本管理 |

## 3. 项目功能

### 3.1 股票行情查询

- 输入单个或多个股票代码
- 从 yfinance 获取近期行情
- 格式化输出股票数据
- 处理无效代码和查询异常

### 3.2 股票历史数据管理

- 获取股票历史 OHLCV 行情
- 保存股票基本信息
- 保存每日历史行情
- 使用唯一索引避免重复记录
- 支持更新已存在的行情

### 3.3 数据库查询与统计

- 查询指定股票的历史行情
- 计算平均收盘价
- 查询最高价与最低价
- 按股票代码和交易日期检索数据

> 功能状态：上述功能为项目当前设计范围，具体是否全部可用以代码实现和测试结果为准。

## 4. 项目目录结构

```text
financial-data-cli/
├── src/
│   ├── __init__.py
│   ├── stock_api.py
│   ├── formatter.py
│   ├── database.py
│   └── stock_repository.py
│
├── tests/
│   ├── test_stock_api.py
│   ├── test_formatter.py
│   └── test_database.py
│
├── sql/
│   └── schema.sql
│
├── main.py
├── db_test.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### 核心模块职责

| 文件 | 职责 |
|---|---|
| `main.py` | 程序入口与命令行菜单 |
| `stock_api.py` | 获取股票行情 |
| `formatter.py` | 格式化行情输出 |
| `database.py` | 创建和管理 MySQL 连接 |
| `stock_repository.py` | 股票数据的保存、查询和更新 |
| `schema.sql` | 定义数据库表结构 |
| `db_test.py` | 数据库连接调试 |
| `tests/` | 自动化测试 |

## 5. 数据库设计

数据库名称：`financial_data`

### 5.1 stocks：股票基本信息

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT | 自增主键 |
| symbol | VARCHAR(20) | 股票代码 |
| company_name | VARCHAR(100) | 公司名称 |
| market | VARCHAR(20) | 股票市场 |

联合唯一索引：

```sql
UNIQUE KEY uk_market_symbol (market, symbol)
```

用于防止同一市场内的股票代码重复。

### 5.2 stock_prices：每日股票行情

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT | 自增主键 |
| stock_id | BIGINT | 股票外键 |
| trade_date | DATE | 交易日期 |
| open_price | DECIMAL(12,4) | 开盘价 |
| high_price | DECIMAL(12,4) | 最高价 |
| low_price | DECIMAL(12,4) | 最低价 |
| close_price | DECIMAL(12,4) | 收盘价 |
| volume | BIGINT | 成交量 |

联合唯一索引：

```sql
UNIQUE KEY uk_stock_date (stock_id, trade_date)
```

两张表通过 `stock_prices.stock_id` 与 `stocks.id` 建立一对多关系。

## 6. 环境配置

### 6.1 克隆项目

```bash
git clone https://github.com/zhangxue929624-glitch/financial-data-cli.git

cd financial-data-cli
```

### 6.2 创建虚拟环境

```bash
python -m venv .venv
```

Windows PowerShell 激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 6.3 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 6.4 配置环境变量

在项目根目录创建 `.env` 文件：

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=financial_data
```

将 `your_password` 替换为本地 MySQL 密码。

注意：

- `.env` 包含敏感信息，不应提交到 GitHub。
- `.env.example` 可以提交，但不能包含真实密码。

### 6.5 初始化数据库

打开 MySQL Workbench，连接本地 MySQL Server。

执行：

```text
sql/schema.sql
```

检查数据库：

```sql
USE financial_data;

SHOW TABLES;

DESCRIBE stocks;

DESCRIBE stock_prices;
```

注意：`CREATE TABLE IF NOT EXISTS` 不会自动修改已经存在的表结构。

## 7. 运行项目

在项目根目录执行：

```bash
python main.py
```

计划提供以下命令行菜单：

```text
========== 股票行情系统 ==========

1. 获取实时或近期股票行情
2. 获取并保存股票历史行情
3. 查询数据库中的历史行情
4. 查询平均收盘价
5. 查询最高价和最低价
0. 退出程序
```

### 示例：查询股票行情

```text
请选择功能：1

请输入股票代码（多个用逗号分隔）：AAPL,MSFT,NVDA
```

程序将分别获取股票行情，并展示查询结果。

### 示例：保存历史行情

```text
请选择功能：2

请输入股票代码：AAPL
请输入市场：NASDAQ
请输入公司名称：Apple Inc.
请输入历史周期：1mo
```

程序获取历史行情后，将数据保存至 MySQL。

## 8. 自动化测试

项目使用 pytest 进行测试。

运行全部测试：

```bash
python -m pytest tests/ -v
```

运行数据库测试：

```bash
python -m pytest tests/test_database.py -v -s
```

运行行情 API 测试：

```bash
python -m pytest tests/test_stock_api.py -v
```

数据库测试需要 MySQL 服务正常运行，并配置正确的 `.env`。

## 9. 项目工作流程

```text
用户输入股票代码
       |
       v
     main.py
       |
       v
   stock_api.py
       |
       v
     yfinance
       |
       v
   股票行情数据
       |
       +------------------+
       |                  |
       v                  v
 formatter.py      stock_repository.py
       |                  |
       v                  v
  终端显示结果         database.py
                          |
                          v
                        MySQL
                          |
                  +-------+-------+
                  |               |
                  v               v
                stocks       stock_prices
```

## 10. 后续优化方向

- 支持股票代码与市场自动识别
- 支持批量下载历史行情
- 使用批量插入提高写入效率
- 增加数据库事务和异常处理
- 支持日期范围查询
- 增加日志记录
- 支持 CSV 数据导出
- 增加股票收益率和波动率计算
- 引入数据可视化
- 后续扩展为 FastAPI 数据服务

## 11. 注意事项

1. yfinance 属于第三方行情数据接口，数据可能存在延迟、缺失或获取失败。
2. 当前项目主要用于学习和研究，不应直接作为实盘交易决策系统。
3. 数据库密码应保存在本地 `.env` 中。
4. 修改数据库表结构
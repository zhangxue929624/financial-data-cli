# Financial Research Assistant

基于 Python 的金融研究助手，支持股票行情查询、MySQL 历史数据管理，以及带引用的财报问答。

## 功能

- **行情查询**：使用 AKShare 获取股票最近日线行情。
- **历史数据**：使用 yfinance 获取历史行情，保存至 MySQL。
- **财报处理**：提取 PDF、保留页序、切分文本并生成向量。
- **财报问答**：按公司和报告期间检索，生成附带原文引用的回答。
- **API 服务**：使用 FastAPI 提供查询和问答接口。

## 技术栈

Python、FastAPI、Pydantic、MySQL、Chroma、Sentence Transformers、pypdf、AKShare、yfinance。

Embedding 模型：`BAAI/bge-small-zh-v1.5`。

## 项目结构

```text
financial-data-cli/
├── main.py                 # 股票行情 CLI
├── requirements.txt
├── .env.example
├── sql/schema.sql          # 数据库初始化
├── src/
│   ├── server.py           # API 接口
│   ├── stock_tool.py       # 行情查询
│   ├── database.py         # MySQL 连接
│   ├── stock_repository.py # 行情存储与统计
│   └── rag/
│       ├── extract.py      # PDF 提取
│       ├── chunk.py        # 文本切分
│       ├── embeddings.py   # 向量生成
│       ├── store.py        # Chroma 配置
│       ├── index.py        # 向量入库
│       ├── search.py       # 检索
│       └── answer.py       # 回答与引用校验
├── data/
│   ├── raw_reports/        # 原始 PDF
│   └── processed/          # 页面与文本块
└── tests/
```

## 环境配置

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pypdf
```

当前 `requirements.txt` 尚未包含 `pypdf`，需单独安装。

参考 `.env.example` 创建 `.env`：

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_password
DB_NAME=financial_data

DEEPSEEK_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

`.env` 不应提交到版本库。使用历史行情管理功能前，需执行 `sql/schema.sql` 初始化 MySQL；财报检索使用 Chroma。

## 财报入库

将 PDF 放入 `data/raw_reports/`，并在 `src/rag/extract.py` 的 `REPORTS` 中登记文件名、公司和报告期间。

依次执行：

```powershell
python -m src.rag.extract
python -m src.rag.chunk
python -m src.rag.index
```

当前按页切分，配置为 500 字符、目标重叠 80 字符。向量保存在 `chroma_reports_day34/`，集合名称为 `reports_v1`。

单独运行检索：

```powershell
python -m src.rag.search
```

## 启动服务

```powershell
python -m uvicorn src.server:app --reload
```

看到 `Application startup complete.` 后，打开：

```text
http://127.0.0.1:8000/docs
```

| 接口 | 功能 |
| --- | --- |
| `GET /stock/{symbol}` | 查询股票行情 |
| `POST /analyze` | 根据行情生成分析 |
| `POST /ask` | 财报问答 |

`/ask` 请求示例：

```json
{
  "question": "营业收入及同比变化是多少？",
  "company": "迪安诊断",
  "report_period": "2026Q1",
  "top_k": 3
}
```

公司与期间必须匹配入库信息。响应包含答案、引用编号、来源文件、PDF 页序及请求编号；无资料或证据不足时返回明确状态。

股票 CLI：

```powershell
python main.py
```

## 常见问题

- **找不到 `src`**：在项目根目录使用 `python -m src.rag.模块名` 运行。
- **模型联网超时**：检查网络与代理。当前 `stock_tool.py` 会清空进程代理设置，可能影响模型下载。
- **使用本地模型缓存**：缓存完整时，可在启动前执行 `$env:HF_HUB_OFFLINE = "1"`；离线模式不能补齐缺失文件。
- **索引不可用**：先执行入库脚本，确认集合非空。
- **更换 embedding 模型**：重新生成文档向量，并重建对应索引。

## 当前限制与计划

当前已编写基础 RAG 流程，完整运行与回答质量仍需验收。PDF 表格可能提取错位，引用编号有效也不代表答案正确，需要回到原文核对。

后续计划：建立评测集、优化检索、整合 Agent 工具、接入 LangGraph 与 MCP，并完善记录存储和 Docker 部署。
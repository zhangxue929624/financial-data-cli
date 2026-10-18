
import os
from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
# 导入你封装好的股票查询工具
from src.stock_tool import get_stock_info
# 加载环境变量（读取 .env 中的 DEEPSEEK_API_KEY）

import logging
import time
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from openai import (
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from src.rag.answer import (
    answer_question,
    ModelOutputError,
    ModelConfigurationError,
)
from src.rag.store import IndexUnavailableError


load_dotenv()

#  创建 FastAPI 总台实例
app = FastAPI(title="量化金融 AI Agent 与行情服务后台")

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL","https://api.deepseek.com")
)

# ==========================================================
# 1. 定义 Pydantic 请求模具（用于 POST /analyze 接口的数据校验）
# ==========================================================
class ChatRequest(BaseModel):
    question: str = Field(description="用户输入的自然语言问题，例如：分析一下英伟达今天的股价行情")
    symbol: str = Field(default="NVDA", description="默认关联的股票代码")

# ==========================================================
# 2. 注册 GET 接口：直接通过网址路径查行情
# ==========================================================
@app.get("/stock/{symbol}")
def read_stock(symbol: str):
    """
    前端只要访问 http://127.0.0.1:8000/stock/NVDA
    FastAPI 就会自动把网址里的 NVDA 抓出来传给 symbol 参数！
    """
    data = get_stock_info(symbol)
    # FastAPI 会自动把 Python 字典转换成标准的 JSON 返回给前端，连 json.dumps 都不用写！
    return data

# ==========================================================
# 3. 注册 POST 接口：核心 AI Agent 智能分析服务
# ==========================================================
@app.post("/analyze")
def analyze_stock_agent(request: ChatRequest):
    """
    前端提交 JSON 数据包：
    {
        "question": "英伟达现在表现怎么样？",
        "symbol": "NVDA"
    }
    后台会触发 AI 智能体逻辑，自动获取行情并由大模型输出专业的金融深度分析报告。
    """
    user_question = request.question
    target_symbol = request.symbol

    # 第一步：在后台默默调用你的股票工具获取真实行情
    market_data = get_stock_info(target_symbol)

    # 第二步：将用户的提问和刚刚拿到的真实金融数据拼装成 Prompt，发给 DeepSeek 大模型
    prompt = f"""
    你是一个专业的金融科技产品经理与量化分析师。
    用户的问题是: {user_question}
    我通过底层数据接口获取到的最新行情数据如下:
    {market_data}

    请根据以上真实行情数据，为用户生成一份结构清晰、专业客观的金融分析报告（包含涨跌情况、波动评估和投资建议）。
    """

    try:
        # 调用 DeepSeek 聊天大模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个精通全球市场的专业量化金融助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        ai_reply = response.choices[0].message.content

        return {
            "status": "success",
            "target_symbol": target_symbol,
            "raw_market_data": market_data,
            "ai_analysis_report": ai_reply
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"AI 分析生成失败: {str(e)}"
        }

logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    company: str = Field(min_length=1, max_length=100)
    report_period: str = Field(min_length=1, max_length=50)
    top_k: int = Field(default=3, ge=1, le=10)

    @field_validator("question", "company", "report_period")
    @classmethod
    def strip_and_check(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("不能只输入空白字符")

        return value


@app.post("/ask")
def ask(request: AskRequest):
    request_id = uuid4().hex
    started = time.perf_counter()

    try:
        result = answer_question(
            question=request.question,
            company=request.company,
            report_period=request.report_period,
            top_k=request.top_k,
        )

        return {
            "request_id": request_id,
            "elapsed_seconds": round(
                time.perf_counter() - started,
                3,
            ),
            **result,
        }

    except APITimeoutError as exc:
        logger.exception("模型超时 request_id=%s", request_id)
        raise HTTPException(
            status_code=504,
            detail={
                "request_id": request_id,
                "message": "模型响应超时，请稍后重试。",
            },
        ) from exc

    except APIConnectionError as exc:
        logger.exception("模型连接失败 request_id=%s", request_id)
        raise HTTPException(
            status_code=502,
            detail={
                "request_id": request_id,
                "message": "无法连接模型服务。",
            },
        ) from exc

    except APIStatusError as exc:
        logger.exception("模型服务返回错误 request_id=%s", request_id)
        raise HTTPException(
            status_code=502,
            detail={
                "request_id": request_id,
                "message": "模型服务调用失败，请检查服务状态与配置。",
            },
        ) from exc

    except ModelOutputError as exc:
        logger.exception("模型输出无效 request_id=%s", request_id)
        raise HTTPException(
            status_code=502,
            detail={
                "request_id": request_id,
                "message": "模型返回的格式或引用无效。",
            },
        ) from exc

    except (IndexUnavailableError, ModelConfigurationError) as exc:
        logger.exception("服务未就绪 request_id=%s", request_id)
        raise HTTPException(
            status_code=503,
            detail={
                "request_id": request_id,
                "message": "服务尚未准备好，请检查索引和模型配置。",
            },
        ) from exc

    except Exception as exc:
        logger.exception("未处理异常 request_id=%s", request_id)
        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "message": "内部处理失败，请根据请求编号检查日志。",
            },
        ) from exc
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel,Field

# 导入你写好的行情获取函数
from stock_tool import get_stock_info  

# 启动魔法：自动寻找项目根目录下的 .env 文件，并将其加载到系统的环境变量中
load_dotenv()
# 安全提取：使用 os.getenv() 根据变量名获取秘钥
# 如果 .env 文件中没有这个变量，它会安全地返回 None，而不是让程序直接崩溃

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY")
                , base_url=os.getenv("LLM_BASE_URL","https://api.deepseek.com")
)

# ==========================================
# 1. 用刚学的 Pydantic 定义参数模具，自动生成“工具说明书”
# ==========================================
class StockQueryParams(BaseModel):
    symbol: str = Field(description="股票代码，例如 AAPL, TSLA, NVDA")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_info",
            "description": "获取指定股票的最新实时行情数据，包括当前价格、涨跌幅、成交量、最高价和最低价。",
            # 利用 Pydantic 一键生成大模型能看懂的 JSON Schema 说明书！"
            "parameters": StockQueryParams.model_json_schema()
        }
    }
]


def chat_with_llm():
    # 捕获【用户问题】 (对应图中的“用户问题”)
    user_input = input("请输入你的问题: ")
    # 用列表维护完整的对话上下文
    messages = [
        {"role": "system", "content": "你是一个专业的量化金融助手。遇到需要实时行情的问题，请务必先调用工具获取真实数据再做分析。"},
        {"role": "user", "content": user_input}
    ]
    # ==========================================
    # 2. 第一次请求：把问题和“工具说明书”一起发给大模型
    # ==========================================
    response = client.chat.completions.create(
        model="deepseek-chat", # 指定模型名称
        temperature=0.0,       # 控制创造力
        messages=messages,
        tools=tools            #递交工具箱
    )

    # LLM 返回的是一个复杂的对象，我们只需要提取最核心的文本内容
    response_message = response.choices[0].message

    # ==========================================
    # 3. 检查大模型是否决定调用工具 (Tool Calling)
    # ==========================================
    if response_message.tool_calls:
            # 先把大模型发出的“我要调用工具”这条指令本身，存入对话历史（官方强制要求，否则第二次请求会报错）
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                # 解析大模型生成的 JSON 参数，例 '{"symbol": "AAPL"}'
                function_args = json.loads(tool_call.function.arguments)
                symbol = function_args.get("symbol")
                
                print(f"\n [系统后台] AI 决定调用工具: {function_name}，目标标的: {symbol}")
                
                if function_name == "get_stock_info":
                    # 真正运行你写的本地 Python 函数！
                    real_stock_data = get_stock_info(symbol)
                    print(f"📈 [系统后台] 成功获取真实行情: {real_stock_data}")
                    
                    # 把拿到的字典转成 JSON 字符串，作为 "tool" 角色的消息塞回对话历史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id, # 必须原样对上号，告诉模型这是哪个调用的结果
                        "content": json.dumps(real_stock_data)
                    })

            # ==========================================
            # 4. 第二次请求：带着拿到的真实数据，让大模型做最终分析
            # ==========================================
            print("🧠 [系统后台] 正在结合真实行情数据生成深度分析...\n")
            second_response = client.chat.completions.create(
                model="deepseek-chat",
                temperature=0.5,
                messages=messages
            )
            print("AI 最终回答：")
            print(second_response.choices[0].message.content)

    else:
        # 如果用户只是问“你好”，大模型觉得不需要查股价，就会直接走这里回答
        print("\nAI 回答：")
        print(response_message.content)

if __name__ == "__main__":
    chat_with_llm()
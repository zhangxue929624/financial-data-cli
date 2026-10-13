import os
from dotenv import load_dotenv
from openai import OpenAI

# 启动魔法：自动寻找项目根目录下的 .env 文件，并将其加载到系统的环境变量中
load_dotenv()
# 安全提取：使用 os.getenv() 根据变量名获取秘钥
# 如果 .env 文件中没有这个变量，它会安全地返回 None，而不是让程序直接崩溃
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("错误：未找到 API 秘钥，请检查 .env 文件！")
    exit()

# 建立 API 桥梁 (需填入你自己的 API Key)
# 这里的 base_url 可以换成任何兼容 OpenAI 格式的模型厂商
base_url = os.getenv("LLM_BASE_URL")

client = OpenAI(api_key=api_key, base_url=base_url)  

def chat_with_llm():
    # 步骤 1: 捕获【用户问题】 (对应图中的“用户问题”)
    user_input = input("请输入你的问题: ")
    
    # 步骤 2: 在【Python】中组装 Prompt，并通过 API 发送给【LLM】 (对应图中的“Python -> LLM”)
    # 这里定义了 System 人设和 User 的具体问题
    response = client.chat.completions.create(
        model="deepseek-chat", # 指定模型名称
        temperature=0.5,       # 控制创造力
        messages=[
            {"role": "system", "content": "你是一个精通 Python、Pandas 和金融底层逻辑的高级量化工程师。处理价格数据时请注意防范浮点数精度丢失，直接输出可执行代码，不要输出任何废话解释。"},
            {"role": "user", "content": user_input}
        ]
    )
    
    # 步骤 3: 提取并打印【回答】 (对应图中的“回答”)
    # LLM 返回的是一个复杂的对象，我们只需要提取最核心的文本内容
    answer = response.choices[0].message.content
    print("\nAI 回答:")
    print(answer)
    cost_tokens = response.usage.total_tokens
    print(f"本次调用共消耗了 {cost_tokens} 个 Token。")

# 启动程序
if __name__ == "__main__":
    chat_with_llm()
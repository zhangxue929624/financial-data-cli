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
print(api_key,base_url)
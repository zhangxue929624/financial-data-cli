import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 确保本地模型顺畅

import chromadb
from chromadb.utils import embedding_functions

# 1. 初始化本地持久化 Chroma 客户端（数据会自动保存在当前目录的 chroma_db 文件夹下）[cite: 19]
client = chromadb.PersistentClient(path="./chroma_db")

# 2. 使用我们刚才下载的开源中文 Embedding 模型作为 Chroma 的底层翻译官
# 这样每次你往数据库存文字时，它会自动帮你转成向量
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 3. 创建或获取一个名为 "financial_reports" 的数据集合（Collection）[cite: 19]
collection = client.get_or_create_collection(
    name="financial_reports",
    embedding_function=embedding_fn
)

# 4. 模拟写入几条带“元数据（Metadata）”的金融财报切片数据
collection.add(
    documents=[
        "2025财年，苹果公司实现总营业收入 4120 亿美元，综合毛利率达到 46.2%。",
        "招商银行今日股价大涨，不良贷款率持续下降，资产质量显著改善。",
        "英伟达发布最新一代 Blackwell 架构 GPU 芯片，AI 算力需求持续爆棚。"
    ],
    metadatas=[
        {"symbol": "AAPL", "year": 2025, "section": "finance"},
        {"symbol": "600036", "year": 2026, "section": "market"},
        {"symbol": "NVDA", "year": 2026, "section": "tech"}
    ],
    ids=["doc_1", "doc_2", "doc_3"]  # 每条数据的唯一身份证号
)

print("✅ 成功向本地 Chroma 数据库写入了 3 条金融研报切片！")

# 5. 测试检索：用一句自然语言去搜索，并加上 Metadata 过滤！
results = collection.query(
    query_texts=["招行的资产质量怎么样？"],
    n_results=1,  # 只要最相似的 1 条
    where={"symbol": "600036"}  # ⬅️ 这就是 Metadata 过滤！精确锁定招商银行的股票代码
)

print("\n=== 检索结果 ===")
print(f"搜到的原文内容: {results['documents'][0]}")
print(f"匹配的元数据: {results['metadatas'][0]}")
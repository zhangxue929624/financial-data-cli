import os
# 关键配置：强制使用国内 HuggingFace 镜像站，无需代理即可满速下载模型！
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from sentence_transformers import SentenceTransformer
import numpy as np

# 加载智源开源的中文王牌 Embedding 模型（首次运行会自动下载权重，也可换用轻量版 bge-small-zh-v1.5）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

sentences = [
    "招商银行今日股价大涨，不良贷款率持续下降",      # 句子 0：核心目标
    "招行最新财报显示资产质量改善，二级市场表现强劲",  # 句子 1：字面几乎没重合，但语义高度相似！
    "英伟达发布最新一代 Blackwell 架构 GPU 芯片"     # 句子 2：完全跨行业的科技新闻
]

# 生成向量并直接开启归一化 (normalize_embeddings=True)
embeddings = model.encode(sentences, normalize_embeddings=True)
print(f"生成的稠密向量维度: {embeddings.shape} (共 {embeddings.shape[0]} 句话，每句话是 {embeddings.shape[1]} 维浮点数)\n")

# 因为已经归一化，直接用矩阵点积 (@ 运算符) 即可算出余弦相似度！
sim_0_1 = np.dot(embeddings[0], embeddings[1])
sim_0_2 = np.dot(embeddings[0], embeddings[2])

print(f"【招行股价】 vs 【招行财报】 语义相似度: {sim_0_1:.4f}  <-- 哪怕用词不同，向量也能认出是同一件事！")
print(f"【招行股价】 vs 【英伟达芯片】 语义相似度: {sim_0_2:.4f}  <-- 语义无关，分数显著拉开")
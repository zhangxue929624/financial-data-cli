import os
# 继续使用国内镜像站高速下载轻量级精排模型
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# 1. 准备用户问题与 3 段极具迷惑性的候选财报切片
query = "招商银行 2025 年的不良贷款率是多少？"

docs = [
    # 切片 0（干扰项 A - 含大量“招商银行”高频词，但完全没提不良贷款率）：
    "招商银行股份有限公司发布 2025 年年度报告。招商银行董事会宣布，招商银行 2025 年全年营业收入稳步增长，招商银行零售客户数突破 2 亿户。",
    
    # 切片 1（干扰项 B - 句式与问题一模一样，但年份是 2023 年！）：
    "根据历史财务数据披露，招商银行 2023 年的不良贷款率为 0.95%，拨备覆盖率保持高位。",
    
    # 切片 2（真正正确的答案 - 表述比较书面，没重复那么多次“招商银行”）：
    "报告期内，本行资产质量保持稳健。截至 2025 年末，本行（招行）不良贷款总额有所下降，不良贷款率为 0.92%，较上年末下降 0.03 个百分点。"
]

# ==========================================================
# 第一阶段：使用 Embedding 模型进行【向量粗排】
# ==========================================================
bi_encoder = SentenceTransformer('BAAI/bge-small-zh-v1.5')
query_emb = bi_encoder.encode(query, normalize_embeddings=True)
doc_embs = bi_encoder.encode(docs, normalize_embeddings=True)

# 计算余弦相似度得分
vector_scores = np.dot(doc_embs, query_emb)

print("=== 1. 第一阶段：纯向量检索 (粗排) 结果 ===")
for idx in np.argsort(vector_scores)[::-1]:
    print(f"[粗排得分: {vector_scores[idx]:.4f}] {docs[idx]}")

# ==========================================================
# 第二阶段：引入 Cross-Encoder (BGE-Reranker) 进行【精排重打分】
# ==========================================================
# 加载智源开源的中文重排序模型（首次运行会自动下载）
reranker = CrossEncoder('BAAI/bge-reranker-base')

# 将 [问题, 切片] 组装成配对列表，让 Reranker 逐字交叉精读
pairs = [[query, doc] for doc in docs]
rerank_scores = reranker.predict(pairs)
print (rerank_scores)
print("\n=== 2. 第二阶段：BGE-Reranker (精排) 逆转后的结果 ===")
for idx in np.argsort(rerank_scores)[::-1]:
    print(f"[精排得分: {rerank_scores[idx]:7.4f}] {docs[idx]}")


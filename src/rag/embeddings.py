#文本转换为向量

from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"

model = SentenceTransformer(MODEL_NAME)


def embed_documents(texts: list[str]):
    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )


def embed_query(question: str):
    query_text = (
        "为这个句子生成表示以用于检索相关文章："
        + question
    )

    return model.encode(
        query_text,
        normalize_embeddings=True,
    )
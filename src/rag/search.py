#向量检索
from src.rag.embeddings import embed_query
from src.rag.store import get_collection

#在指定公司和报告期间的资料中，根据问题搜索相关文本块，并整理成易用的结果列表。
def search_reports(
    question: str,
    company: str,
    report_period: str,
    top_k: int = 3,
) -> list[dict]:

    question = question.strip()
    company = company.strip()
    report_period = report_period.strip()

    if not question or not company or not report_period:
        raise ValueError("问题、公司和报告期间不能为空。")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k 必须在 1 到 10 之间。")

    collection = get_collection()
    query_vector = embed_query(question)

    result = collection.query(
        query_embeddings=[query_vector.tolist()],
        n_results=min(top_k, collection.count()),
        where={
            "$and": [
                {"company": {"$eq": company}},
                {"report_period": {"$eq": report_period}},
            ]
        },
        include=["documents", "metadatas", "distances"],
    )

    hits = []

    for chunk_id, text, meta, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append({
            "chunk_id": chunk_id,
            "text": text,
            "company": meta["company"],
            "report_period": meta["report_period"],
            "file_name": meta["file_name"],
            "pdf_page": meta["pdf_page"],
            "distance": float(distance),
        })

    return hits


def main():
    question = input("问题：")
    company = input("公司：")
    report_period = input("报告期间：")

    hits = search_reports(question, company, report_period)

    if not hits:
        print("没有找到符合过滤条件的片段。")
        return

    for number, hit in enumerate(hits, start=1):
        print("\n" + "=" * 50)
        print("排名：", number)
        print("chunk_id：", hit["chunk_id"])
        print("来源：", hit["file_name"])
        print("PDF页序：", hit["pdf_page"])
        print("距离：", hit["distance"])
        print("原文：")
        print(hit["text"])


if __name__ == "__main__":
    main()
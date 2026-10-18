#向量入库

import json

from src.rag.embeddings import embed_documents
from src.rag.store import PROJECT_ROOT, create_collection


CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
BATCH_SIZE = 32

#函数负责**读取 `chunks.jsonl`，检查文本块是否有效，然后返回文本块列表**
def load_chunks():
    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue

            chunk = json.loads(line)

            if not chunk["text"].strip():
                raise ValueError(
                    f"第 {line_number} 行的文本为空，请检查切分结果。"
                )

            chunks.append(chunk)

    if not chunks:
        raise ValueError("chunks.jsonl 中没有可入库记录。")

    ids = [chunk["chunk_id"] for chunk in chunks]

    if len(ids) != len(set(ids)):
        raise ValueError("存在重复 chunk_id，请先修复。")

    return chunks

#这段 `main()` 是**入库主流程**：读取文本块，分批生成向量，再将文本、向量和元数据写入 Chroma
def main():
    chunks = load_chunks()
    collection = create_collection()

    before = collection.count()

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [chunk["text"] for chunk in batch]

        vectors = embed_documents(texts)

        metadata_list = []

        for chunk in batch:
            metadata_list.append({
                "doc_id": chunk["doc_id"],
                "company": chunk["company"],
                "report_period": chunk["report_period"],
                "file_name": chunk["file_name"],
                "pdf_page": chunk["pdf_page"],
                "chunk_config_version": chunk["chunk_config_version"],
            })

        collection.upsert(
            ids=[chunk["chunk_id"] for chunk in batch],
            documents=texts,
            embeddings=vectors.tolist(),
            metadatas=metadata_list,
        )

        print(f"已处理 {start + len(batch)} / {len(chunks)} 块")

    print("入库前数量：", before)
    print("入库后数量：", collection.count())


if __name__ == "__main__":
    main()
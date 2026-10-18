#进行分块保留为json格式
import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PAGES_PATH = PROJECT_ROOT / "data" / "processed" / "pages.jsonl"
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80,
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        "。",
        "!",
        "?",
        ";",
        " ",
        "",
    ],
)


def load_pages() -> list[dict]:
    records = []

    with PAGES_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    return records


def split_page(page_record: dict) -> list[dict]:
    text = page_record["text"]

    if not text:
        return []

    pieces = splitter.split_text(text)
    chunks = []

    for chunk_index, piece in enumerate(pieces):
        chunk_id = (
            f"{page_record['doc_id']}"
            f"_p{page_record['pdf_page']}"
            f"_c{chunk_index}"
        )

        chunk = {
            "chunk_id": chunk_id,
            "chunk_index": chunk_index,
            "chunk_config_version": "char500_overlap80_v1",
            "doc_id": page_record["doc_id"],
            "company": page_record["company"],
            "report_period": page_record["report_period"],
            "file_name": page_record["file_name"],
            "source_url": page_record["source_url"],
            "pdf_page": page_record["pdf_page"],
            "text": piece,
        }

        chunks.append(chunk)

    return chunks



def main():
    pages = load_pages()
    all_chunks = []

    for page_record in pages:
        page_chunks = split_page(page_record)
        all_chunks.extend(page_chunks)

    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with CHUNKS_PATH.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            line = json.dumps(chunk, ensure_ascii=False)
            f.write(line + "\n")

    print("页面数量：", len(pages))
    print("文本块数量：", len(all_chunks))
    print("输出文件：", CHUNKS_PATH)

    for chunk in all_chunks[:10]:
        print("\n---")
        print("chunk_id:", chunk["chunk_id"])
        print("公司：", chunk["company"])
        print("报告期间：", chunk["report_period"])
        print("PDF页码:", chunk["pdf_page"])
        print("字符数：", len(chunk["text"]))
        print("文本：", chunk["text"][:200])


if __name__ == "__main__":
    main()
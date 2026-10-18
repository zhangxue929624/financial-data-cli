#提取并清洗数据保存为json格式

import json
from pathlib import Path
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw_reports"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


REPORTS = [
    {
        "doc_id": "dian_2026q1_v1",
        "company": "迪安诊断",
        "report_period": "2026Q1",
        "file_name": "迪安诊断：2026年一季度报告.pdf",
        "source_url": "",
    },
    {
        "doc_id": "dian_2025q3_v1",
        "company": "迪安诊断",
        "report_period": "2025Q3",
        "file_name": "迪安诊断：2025年三季度报告.pdf",
        "source_url": "",
    },
    {
        "doc_id": "kunlun_2026q1_v1",
        "company": "昆仑万维",
        "report_period": "2026Q1",
        "file_name": "昆仑万维：2026年一季度报告.pdf",
        "source_url": "",
    },
]


def clean_text(text: str) -> str:
    """进行最小限度清洗，保留正文换行与内部空格。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "")
    return text.strip()


def extract_report(meta: dict) -> tuple[list[dict], dict]:
    """提取一份报告，并返回页面记录和文件汇总。"""
    pdf_path = RAW_DIR / meta["file_name"]
    records = []

    summary = {
        "doc_id": meta["doc_id"],
        "file_name": meta["file_name"],
        "total_pages": 0,
        "ok_pages": 0,
        "empty_pages": 0,
        "error_pages": 0,
        "file_error": "",
    }

    try:
        reader = PdfReader(pdf_path)
        summary["total_pages"] = len(reader.pages)
    except Exception as exc:
        summary["file_error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return records, summary

    for page_number in range(1, summary["total_pages"] + 1):
        record = {
            **meta,
            "pdf_page": page_number,
            "raw_text": "",
            "text": "",
            "extraction_status": "",
            "error": "",
        }

        try:
            page = reader.pages[page_number - 1]
            raw_text = page.extract_text() or ""
            text = clean_text(raw_text)

            record["raw_text"] = raw_text
            record["text"] = text

            if text:
                record["extraction_status"] = "ok"
                summary["ok_pages"] += 1
            else:
                record["extraction_status"] = "empty"
                summary["empty_pages"] += 1

        except Exception as exc:
            record["extraction_status"] = "error"
            record["error"] = (
                f"{type(exc).__name__}: {exc}"
            )
            summary["error_pages"] += 1

        records.append(record)

    return records, summary


def main():
    # 防止配置中出现重复的文档ID。
    doc_ids = [item["doc_id"] for item in REPORTS]
    if len(doc_ids) != len(set(doc_ids)):
        raise ValueError("REPORTS 中存在重复 doc_id")

    all_records = []
    summaries = []

    for meta in REPORTS:
        records, summary = extract_report(meta)
        all_records.extend(records)
        summaries.append(summary)

        print(
            f"{summary['file_name']}:"
            f"总页数={summary['total_pages']},"
            f"非空页={summary['ok_pages']},"
            f"空页={summary['empty_pages']}m"
            f"错误页={summary['error_pages']}"
        )

        if summary["file_error"]:
            print("  文件错误：", summary["file_error"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pages_path = OUTPUT_DIR / "pages.jsonl"

    # 覆盖本次生成的中间文件，不会修改原始PDF。
    with pages_path.open("w", encoding="utf-8") as f:
        for record in all_records:
            line = json.dumps(record, ensure_ascii=False)
            f.write(line + "\n")

    summary_path = OUTPUT_DIR / "extraction_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(
            summaries,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("页面记录已保存：", pages_path)
    print("提取汇总已保存：", summary_path)


if __name__ == "__main__":
    main()
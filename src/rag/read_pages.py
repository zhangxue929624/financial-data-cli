#验证文本读取是否正常
import json
from pathlib import Path


pages_path = Path("data/processed/pages.jsonl")

with pages_path.open("r", encoding="utf-8") as f:
    records = [
        json.loads(line)
        for line in f
        if line.strip()
    ]

print("读取到的页面记录数：", len(records))

target = next(
    (
        record
        for record in records
        if record["doc_id"] == "dian_2026q1_v1"
        and record["pdf_page"] == 2
    ),
    None,
)

if target is None:
    print("没有找到目标页面，请检查配置与提取汇总。")
else:
    print(target["file_name"])
    print("PDF页序:", target["pdf_page"])
    print("状态：", target["extraction_status"])
    print(target["text"])
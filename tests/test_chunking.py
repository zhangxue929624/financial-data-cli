from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# 模拟一段从苹果 10-K 财报中解析出的 Markdown 文本
sample_financial_report = """# 苹果公司 (AAPL) 2025 财年年度报告
## 第一部分：核心财务表现与毛利率分析
2025财年，苹果公司实现总营业收入 4120 亿美元，同比增长 5.4%。其中 iPhone 业务依然是核心支柱，贡献了 2150 亿美元营收。
得益于自研芯片成本优化以及高毛利的服务业务（Services）占比提升至 25%，公司全年综合毛利率达到创纪录的 46.2%，较去年的 44.1% 提升了 210 个基点。管理层预计下一财季毛利率将维持在 46.0% 至 47.0% 之间。

## 第二部分：供应链与地缘政治风险披露
公司绝大多数硬件产品的组装与核心零部件制造高度集中于亚洲地区。如果未来发生极端贸易摩擦、关税壁垒升级或局部物流中断，可能导致新品发布延迟，并对短期营业利润率造成 150 至 300 个基点的负面冲击。
"""

# 1. 第一步：先按 Markdown 标题层级做结构化切分，自动提取章节作为 Metadata
headers_to_split_on = [
    ("#", "Report_Title"),
    ("##", "Section"),
]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = md_splitter.split_text(sample_financial_report)

# 2. 第二步：在章节内部，使用递归字符切分器控制块大小与重叠
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,          # 为了演示切分效果，这里故意设小为 120 字符（实际生产建议 500~800）
    chunk_overlap=30,        # 设置 30 字符的重叠保护区
    separators=["\n\n", "\n", "。", "，", " ", ""]
)

final_chunks = text_splitter.split_documents(md_header_splits)

# 3. 打印观察切分结果与自动携带的 Metadata（未来直接存入 MySQL！）
for i, chunk in enumerate(final_chunks):
    print(f"=== 切片 Chunk #{i+1} (长度: {len(chunk.page_content)} 字) ===")
    print(f"【元数据 Metadata】: {chunk.metadata}")
    print(f"【切片正文】: {chunk.page_content}\n")
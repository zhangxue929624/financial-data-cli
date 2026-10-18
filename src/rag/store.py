
#准备 Chroma 向量数据库的客户端，创建一个用于存放财报文本块的集合
from functools import lru_cache
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "chroma_reports_day34"
COLLECTION_NAME = "reports_v1"


class IndexUnavailableError(RuntimeError):
    """向量索引不存在、为空或无法打开。"""


@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=str(DB_PATH))


def create_collection():
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )


@lru_cache(maxsize=1)
def get_collection():
    try:
        collection = get_client().get_collection(
            name=COLLECTION_NAME,
            embedding_function=None,
        )

        if collection.count() == 0:
            raise IndexUnavailableError("集合为空，请先完成入库。")

        return collection

    except IndexUnavailableError:
        raise

    except Exception as exc:
        raise IndexUnavailableError(
            "无法打开向量索引，请检查目录并先执行入库。"
        ) from exc
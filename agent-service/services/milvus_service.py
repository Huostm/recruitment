import os
from pymilvus import MilvusClient
from typing import List, Dict


class MilvusService:
    def __init__(self):
        # 禁用代理，避免 Milvus 本地连接走代理
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        os.environ['no_proxy'] = 'localhost,127.0.0.1'

        self.url = os.getenv('MILVUS_URL', 'http://localhost:19530')
        self.client = MilvusClient(self.url)
        self.db_name = 'recruitment_db'
        self.collection_name = 'jd_collection'

        print(f"连接到 Milvus: {self.url}")
        self.ensure_database()
        self.ensure_collection()

    def ensure_database(self):
        """确保 Database 存在，不存在则创建"""
        existed_databases = self.client.list_databases()
        if self.db_name not in existed_databases:
            self.client.create_database(db_name=self.db_name)
            print(f"Database '{self.db_name}' 创建成功")
        else:
            print(f"Database '{self.db_name}' 已存在")

        # 切换到该 database
        self.client.using_database(self.db_name)

    def ensure_collection(self):
        """确保 Collection 存在，不存在则创建"""
        if self.client.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' 已存在")
        else:
            self.create_collection()

    def create_collection(self):
        """创建 Collection"""
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=4096,
            metric_type="COSINE"
        )
        print(f"Collection '{self.collection_name}' 创建成功")

    def insert_jd_batch(self, texts: List[str]) -> bool:
        """批量插入 JD（自动切分 + 向量化）"""
        try:
            from services.llm_service import LLMService
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            llm_service = LLMService()

            # 切分文本
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )

            # 对每个 JD 单独切分，并记录所属 JD
            data = []
            chunk_id = 0

            for jd_index, text in enumerate(texts):
                chunks = text_splitter.split_text(text)

                for chunk in chunks:
                    data.append({
                        "id": chunk_id,
                        "text": chunk,
                        "jd_index": jd_index
                    })
                    chunk_id += 1

            # 批量向量化所有 chunks
            all_chunk_texts = [d["text"] for d in data]
            embeddings = llm_service.get_embeddings()
            vectors = embeddings.embed_documents(all_chunk_texts)

            # 添加向量到数据
            for i, d in enumerate(data):
                d["vector"] = vectors[i]

            # 批量插入
            self.client.upsert(
                collection_name=self.collection_name,
                data=data
            )
            print(f"成功插入 {len(data)} 个 JD chunks")
            return True
        except Exception as e:
            print(f"批量插入 JD 失败: {e}")
            return False

    def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """向量检索（自动向量化）"""
        try:
            from services.llm_service import LLMService
            llm_service = LLMService()

            # 将查询文本向量化
            query_embedding = llm_service.get_embeddings()
            query_vector = query_embedding.embed_query(str(query_text))

            # 向量检索
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=top_k,
                output_fields=["text"]
            )

            matches = []
            if results and len(results) > 0:
                for hit in results[0]:
                    matches.append({
                        "id": hit.get('id'),
                        "text": hit.get('entity', {}).get('text', ''),
                        "score": hit.get('distance', 0)
                    })

            return matches
        except Exception as e:
            print(f"检索失败: {e}")
            return []

    def get_count(self) -> int:
        """获取 Collection 中的数据数量"""
        try:
            # 查询所有记录并统计
            result = self.client.query(
                collection_name=self.collection_name,
                filter="id >= 0",
                output_fields=["id"],
                limit=10000
            )
            return len(result)
        except Exception as e:
            print(f"获取数量失败: {e}")
            return 0

    def clear_collection(self):
        """清空 Collection"""
        try:
            if self.client.has_collection(self.collection_name):
                self.client.drop_collection(self.collection_name)
                self.create_collection()
                print(f"Collection '{self.collection_name}' 已清空")
        except Exception as e:
            print(f"清空 Collection 失败: {e}")
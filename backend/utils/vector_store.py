import openai
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Optional
from config.config import Config

class EmbeddingModel:
    """嵌入模型接口"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.API_BASE_URL
        )
    
    def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        try:
            response = self.client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {e}")
            return []
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return embeddings

class VectorStore:
    """向量存储器"""
    
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = Config.VECTOR_DB_PATH
        
        self.persist_directory = persist_directory
        
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True)
        )
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="jiangsu_tourism",
            metadata={"description": "江苏地区旅游知识库"}
        )
        
        self.embedding_model = EmbeddingModel()
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """添加文档到向量库"""
        try:
            if not documents:
                return True
            
            # 准备数据
            texts = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            ids = [f"{doc['metadata']['filename']}_{doc['metadata']['chunk_id']}" 
                   for doc in documents]
            
            # 生成嵌入向量
            print("Generating embeddings...")
            embeddings = self.embedding_model.embed_batch(texts)
            
            # 添加到向量库
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, k: int = 3, region_filter: str = None) -> List[Dict]:
        """搜索相关文档"""
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.embed_text(query)
            if not query_embedding:
                return []
            
            # 构建查询条件
            where_condition = {}
            if region_filter and region_filter != "all":
                where_condition["region"] = region_filter
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_condition if where_condition else None
            )
            
            # 格式化结果
            documents = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    doc = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def get_collection_info(self) -> Dict:
        """获取集合信息"""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': 'jiangsu_tourism'
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {'document_count': 0, 'collection_name': 'jiangsu_tourism'}
    
    def reset_collection(self) -> bool:
        """重置集合（清空所有文档）"""
        try:
            self.client.delete_collection("jiangsu_tourism")
            self.collection = self.client.get_or_create_collection(
                name="jiangsu_tourism",
                metadata={"description": "江苏地区旅游知识库"}
            )
            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False
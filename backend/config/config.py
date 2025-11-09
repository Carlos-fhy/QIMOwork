import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""
    
    # 阿里百炼API配置
    API_BASE_URL = os.environ.get('API_BASE_URL')
    API_KEY = os.environ.get('API_KEY')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'text-embedding-v1')
    CHAT_MODEL = os.environ.get('CHAT_MODEL', 'qwen-max')
    
    # 高德地图API配置
    AMAP_API_KEY = os.environ.get('AMAP_API_KEY')
    
    # 向量数据库配置
    VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', '../vector_db')
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '800'))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '200'))
    TOP_K = int(os.environ.get('TOP_K', '3'))
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jiangsu-tourism-rag-system')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
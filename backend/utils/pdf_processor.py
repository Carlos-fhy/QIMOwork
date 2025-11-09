import PyPDF2
import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def process_pdf(self, pdf_path: str, region: str = "") -> List[Dict]:
        """处理单个PDF文件，返回分块文档"""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # 文本分块
        chunks = self.text_splitter.split_text(text)
        
        # 构造文档元数据
        documents = []
        filename = os.path.basename(pdf_path)
        
        for i, chunk in enumerate(chunks):
            doc = {
                'content': chunk,
                'metadata': {
                    'source': pdf_path,
                    'filename': filename,
                    'region': region,
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                }
            }
            documents.append(doc)
        
        return documents
    
    def process_directory(self, directory_path: str) -> List[Dict]:
        """处理目录下的所有PDF文件"""
        all_documents = []
        
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist")
            return all_documents
        
        for file in os.listdir(directory_path):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(directory_path, file)
                
                # 从文件名提取地区信息
                region = self._extract_region_from_filename(file)
                
                documents = self.process_pdf(pdf_path, region)
                all_documents.extend(documents)
                print(f"Processed {file}: {len(documents)} chunks")
        
        return all_documents
    
    def _extract_region_from_filename(self, filename: str) -> str:
        """从文件名提取地区信息"""
        regions = {
            '南京': '南京',
            '苏州': '苏州', 
            '扬州': '扬州',
            '无锡': '无锡',
            '常州': '常州',
            '镇江': '镇江',
            '连云港': '连云港',
            '周庄': '周庄',
            '同里': '同里'
        }
        
        for region_key, region_value in regions.items():
            if region_key in filename:
                return region_value
        
        return '江苏'
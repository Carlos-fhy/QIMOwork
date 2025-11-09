#!/usr/bin/env python3
"""
简化的知识库构建脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from utils.pdf_processor import PDFProcessor
    from utils.vector_store import VectorStore
    from config.config import Config
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖包已安装")
    sys.exit(1)

def main():
    print("=" * 50)
    print("江苏旅游知识库构建工具")
    print("=" * 50)
    
    # 初始化处理器
    try:
        pdf_processor = PDFProcessor(chunk_size=800, chunk_overlap=200)
        vector_store = VectorStore()
    except Exception as e:
        print(f"初始化失败: {e}")
        return 1
    
    # 检查数据目录
    data_dir = Path("../data/江苏地区")
    if not data_dir.exists():
        print(f"数据目录不存在: {data_dir}")
        return 1
    
    # 检查现有数据
    try:
        info = vector_store.get_collection_info()
        if info['document_count'] > 0:
            print(f"向量数据库已存在 {info['document_count']} 个文档")
            response = input("是否重新构建？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
            vector_store.reset_collection()
    except Exception as e:
        print(f"检查现有数据时出错: {e}")
    
    # 处理PDF文档
    print(f"\n扫描目录: {data_dir}")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("未找到PDF文件")
        return 1
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    print(f"\n开始处理文档...")
    try:
        documents = pdf_processor.process_directory(str(data_dir))
    except Exception as e:
        print(f"处理文档时出错: {e}")
        return 1
    
    if not documents:
        print("未能处理任何文档")
        return 1
    
    print(f"成功处理 {len(documents)} 个文档块")
    
    # 统计各地区文档数量
    region_stats = {}
    for doc in documents:
        region = doc['metadata'].get('region', '未知')
        region_stats[region] = region_stats.get(region, 0) + 1
    
    print("\n地区分布:")
    for region, count in region_stats.items():
        print(f"  {region}: {count} 个文档块")
    
    # 添加到向量库
    print(f"\n生成向量并存储到数据库...")
    try:
        success = vector_store.add_documents(documents)
    except Exception as e:
        print(f"存储到向量库时出错: {e}")
        return 1
    
    if success:
        try:
            final_info = vector_store.get_collection_info()
            print(f"知识库构建完成!")
            print(f"总文档数量: {final_info['document_count']}")
            print(f"存储位置: {Config.VECTOR_DB_PATH}")
            return 0
        except Exception as e:
            print(f"获取最终信息时出错: {e}")
            return 0
    else:
        print("知识库构建失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
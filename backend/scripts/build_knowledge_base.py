#!/usr/bin/env python3
"""
江苏旅游知识库构建脚本
用于处理PDF文档并构建向量数据库
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.pdf_processor import PDFProcessor
from utils.vector_store import VectorStore
from config.config import Config

def main():
    parser = argparse.ArgumentParser(description='构建江苏旅游知识库')
    parser.add_argument('--data-dir', default='../data/江苏地区', 
                       help='PDF文档目录路径')
    parser.add_argument('--reset', action='store_true', 
                       help='重置向量数据库（删除现有数据）')
    parser.add_argument('--chunk-size', type=int, default=800, 
                       help='文本分块大小')
    parser.add_argument('--chunk-overlap', type=int, default=200, 
                       help='文本分块重叠大小')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("江苏旅游知识库构建工具")
    print("=" * 50)
    
    # 初始化处理器
    pdf_processor = PDFProcessor(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    vector_store = VectorStore()
    
    # 检查数据目录
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"❌ 数据目录不存在: {data_dir}")
        return 1
    
    # 检查是否需要重置
    if args.reset:
        print("🔄 重置向量数据库...")
        vector_store.reset_collection()
        print("✅ 向量数据库已重置")
    
    # 检查现有数据
    info = vector_store.get_collection_info()
    if info['document_count'] > 0 and not args.reset:
        print(f"ℹ️  向量数据库已存在 {info['document_count']} 个文档")
        response = input("是否继续添加文档？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return 0
    
    # 处理PDF文档
    print(f"\n📂 扫描目录: {data_dir}")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return 1
    
    print(f"📄 找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    print(f"\n🔨 开始处理文档...")
    documents = pdf_processor.process_directory(str(data_dir))
    
    if not documents:
        print("❌ 未能处理任何文档")
        return 1
    
    print(f"📝 成功处理 {len(documents)} 个文档块")
    
    # 统计各地区文档数量
    region_stats = {}
    for doc in documents:
        region = doc['metadata'].get('region', '未知')
        region_stats[region] = region_stats.get(region, 0) + 1
    
    print("\n📊 地区分布:")
    for region, count in region_stats.items():
        print(f"  {region}: {count} 个文档块")
    
    # 添加到向量库
    print(f"\n⚡ 生成向量并存储到数据库...")
    success = vector_store.add_documents(documents)
    
    if success:
        final_info = vector_store.get_collection_info()
        print(f"✅ 知识库构建完成!")
        print(f"📈 总文档数量: {final_info['document_count']}")
        print(f"💾 存储位置: {Config.VECTOR_DB_PATH}")
        return 0
    else:
        print("❌ 知识库构建失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
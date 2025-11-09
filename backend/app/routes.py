from flask import Blueprint, request, jsonify, Response, stream_template
import json
import time
from utils.qa_system import QASystem
from utils.amap_service import AMapService

main = Blueprint('main', __name__)

# 初始化问答系统
qa_system = QASystem()

# 初始化地图服务
amap_service = AMapService()

@main.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查向量库连接
        info = qa_system.vector_store.get_collection_info()
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'vector_db': info
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@main.route('/api/regions', methods=['GET'])
def get_regions():
    """获取可用地区列表"""
    try:
        regions = qa_system.get_available_regions()
        return jsonify({
            'success': True,
            'regions': regions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/chat', methods=['POST'])
def chat():
    """普通问答接口"""
    try:
        print("=" * 50)
        print("收到普通问答请求")
        print(f"请求方法: {request.method}")
        print(f"请求头: {dict(request.headers)}")
        
        # 确保正确的编码处理
        raw_data = request.get_data()
        print(f"原始数据: {raw_data}")
        
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            # 尝试手动解析JSON
            try:
                import json
                raw_data_text = request.get_data(as_text=True)
                print(f"原始数据（文本）: {raw_data_text}")
                data = json.loads(raw_data_text)
            except Exception as parse_error:
                print(f"JSON解析错误: {parse_error}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON data'
                }), 400
        
        print(f"解析后的数据: {data}")
        
        # 验证请求参数
        if not data or 'question' not in data:
            print("错误: 缺少question参数")
            return jsonify({
                'success': False,
                'error': 'Missing question parameter'
            }), 400
        
        question = str(data['question']).strip()
        if not question:
            print("错误: 问题为空")
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400
        
        region = str(data.get('region', 'all'))
        k = int(data.get('k', 3))
        
        print(f"问题: {question}")
        print(f"地区: {region}")
        print(f"Top-K: {k}")
        print("开始调用问答系统...")
        
        # 调用问答系统
        result = qa_system.answer_question(question, region, k)
        
        print(f"问答结果: success={result.get('success')}")
        if result.get('success'):
            print(f"回答长度: {len(result.get('answer', ''))}")
            print(f"来源数量: {len(result.get('sources', []))}")
        else:
            print(f"错误信息: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print("发生异常:")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.route('/api/chat/stream', methods=['GET'])
def chat_stream():
    """流式问答接口"""
    try:
        question = request.args.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Missing question parameter'}), 400
        
        region = request.args.get('region', 'all')
        k = int(request.args.get('k', 3))
        
        # 简化日志输出，确保编码正确
        try:
            print(f"问题: {question}")
            if '路' in question or '规划' in question or '怎么' in question:
                print("检测到可能的路径规划请求")
        except UnicodeEncodeError:
            print("收到中文路径规划问题")
        
        def generate():
            """生成器函数用于SSE"""
            try:
                total_content = ""
                route_related = False
                
                for chunk in qa_system.stream_answer(question, region, k):
                    # 累积内容用于路径分析
                    if 'content' in chunk:
                        total_content += chunk.get('content', '')
                    
                    # 检查是否包含路径规划内容
                    if not route_related:
                        route_keywords = ['路线', '路径', '怎么去', '怎么走', '交通', '行程', '自驾', '导航', '距离']
                        if any(keyword in total_content for keyword in route_keywords):
                            route_related = True
                            print("AI回答中检测到路径规划内容")
                    
                    # 格式化为SSE事件
                    data = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    
                    # 如果完成，发送结束事件
                    if chunk.get('done', False):
                        # 如果是路径规划相关，提取地点信息
                        if route_related:
                            try:
                                from utils.route_extractor import RouteExtractor
                                locations = RouteExtractor.extract_locations(total_content)
                                if locations:
                                    print(f"提取到地点: {', '.join(locations)} (共{len(locations)}个)")
                                    print("地图组件将自动启动路线规划...")
                                else:
                                    print("未提取到具体地点")
                            except Exception as e:
                                print(f"地点提取失败: {e}")
                        
                        print("AI回答生成完成")
                        yield "data: [DONE]\n\n"
                        break
                        
            except Exception as e:
                print(f"流式生成错误: {e}")
                import traceback
                traceback.print_exc()
                
                error_data = json.dumps({
                    'content': f'Error: {str(e)}',
                    'done': True,
                    'sources': []
                }, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        print("流式接口发生异常:")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.route('/api/build-knowledge-base', methods=['POST'])
def build_knowledge_base():
    """构建知识库接口"""
    try:
        data = request.get_json() or {}
        reset = data.get('reset', False)
        
        # 如果需要重置，清空现有数据
        if reset:
            qa_system.vector_store.reset_collection()
        
        # 检查是否已有数据
        info = qa_system.vector_store.get_collection_info()
        if info['document_count'] > 0 and not reset:
            return jsonify({
                'success': True,
                'message': 'Knowledge base already exists',
                'document_count': info['document_count']
            })
        
        # 开始构建知识库
        from utils.pdf_processor import PDFProcessor
        import os
        
        pdf_processor = PDFProcessor()
        # 修复路径问题 - 使用绝对路径
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(backend_dir)
        data_dir = os.path.join(project_root, 'data', '江苏地区')
        
        print(f"Looking for data in: {data_dir}")  # 调试信息
        
        if not os.path.exists(data_dir):
            return jsonify({
                'success': False,
                'error': 'Data directory not found'
            }), 400
        
        # 处理PDF文档
        documents = pdf_processor.process_directory(data_dir)
        
        if not documents:
            return jsonify({
                'success': False,
                'error': 'No documents processed'
            }), 400
        
        # 添加到向量库
        success = qa_system.vector_store.add_documents(documents)
        
        if success:
            info = qa_system.vector_store.get_collection_info()
            return jsonify({
                'success': True,
                'message': 'Knowledge base built successfully',
                'document_count': info['document_count'],
                'processed_chunks': len(documents)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to build knowledge base'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.route('/api/map/geocode', methods=['POST'])
def geocode():
    """地理编码接口"""
    try:
        data = request.get_json()
        address = data.get('address')
        city = data.get('city', '江苏')
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Missing address parameter'
            }), 400
        
        print(f"地理编码请求: {address}")
        result = amap_service.geocode(address, city)
        
        if result.get('success'):
            print(f"地理编码成功: {address} -> ({result.get('longitude', 'N/A')}, {result.get('latitude', 'N/A')})")
        else:
            print(f"地理编码失败: {address}")
            
        return jsonify(result)
        
    except Exception as e:
        print(f"地理编码异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.route('/api/map/route', methods=['POST'])
def driving_route():
    """驾车路线规划接口"""
    try:
        data = request.get_json()
        origin_address = data.get('origin')
        destination_address = data.get('destination')
        
        if not origin_address or not destination_address:
            return jsonify({
                'success': False,
                'error': 'Missing origin or destination parameter'
            }), 400
        
        print(f"路线规划请求: {origin_address} -> {destination_address}")
        
        # 先进行地理编码
        origin_geo = amap_service.geocode(origin_address)
        if not origin_geo['success']:
            print(f"起点地址解析失败: {origin_address}")
            return jsonify({
                'success': False,
                'error': f'起点地址解析失败: {origin_geo["error"]}'
            }), 400
        
        destination_geo = amap_service.geocode(destination_address)
        if not destination_geo['success']:
            print(f"终点地址解析失败: {destination_address}")
            return jsonify({
                'success': False,
                'error': f'终点地址解析失败: {destination_geo["error"]}'
            }), 400
        
        # 进行路线规划
        route_result = amap_service.driving_route(origin_geo, destination_geo)
        
        if route_result['success']:
            print(f"路线规划成功")
            # 添加地理编码结果
            route_result['origin'] = {
                'address': origin_address,
                'longitude': origin_geo['longitude'],
                'latitude': origin_geo['latitude'],
                'formatted_address': origin_geo['formatted_address']
            }
            route_result['destination'] = {
                'address': destination_address,
                'longitude': destination_geo['longitude'],
                'latitude': destination_geo['latitude'],
                'formatted_address': destination_geo['formatted_address']
            }
        else:
            print(f"路线规划失败")
        
        return jsonify(route_result)
        
    except Exception as e:
        print(f"路线规划异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.route('/api/map/poi', methods=['POST'])
def search_poi():
    """搜索周边POI接口"""
    try:
        data = request.get_json()
        address = data.get('address')
        keywords = data.get('keywords', '景点')
        radius = data.get('radius', 5000)
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Missing address parameter'
            }), 400
        
        # 先进行地理编码
        geo_result = amap_service.geocode(address)
        if not geo_result['success']:
            return jsonify({
                'success': False,
                'error': f'地址解析失败: {geo_result["error"]}'
            }), 400
        
        # 搜索POI
        poi_result = amap_service.get_poi_around(
            geo_result['longitude'],
            geo_result['latitude'],
            keywords,
            radius
        )
        
        return jsonify(poi_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@main.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': 'API endpoint not found'
    }), 404

@main.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
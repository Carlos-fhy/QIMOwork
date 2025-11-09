import openai
from typing import List, Dict, Generator
from config.config import Config
from utils.vector_store import VectorStore

class ChatModel:
    """聊天模型接口"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.API_BASE_URL
        )
    
    def generate_response(self, messages: List[Dict], stream: bool = False):
        """生成回答"""
        try:
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=messages,
                stream=stream,
                temperature=0.7,
                max_tokens=2000
            )
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

class QASystem:
    """问答系统"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.chat_model = ChatModel()
        
    def _build_context_prompt(self, query: str, documents: List[Dict]) -> str:
        """构建包含上下文的提示词"""
        context = "\n\n".join([
            f"文档{i+1}（来源：{doc['metadata'].get('region', '江苏')}）：\n{doc['content']}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""你是一个专业的江苏旅游顾问。请基于以下提供的旅游资料，回答用户的问题。

相关旅游资料：
{context}

用户问题：{query}

请注意：
1. 请基于提供的资料进行回答，如果资料中没有相关信息，请说明
2. 回答要具体、实用，包含详细的旅游信息
3. 如果涉及多个地区，请分别介绍
4. 语言要亲切自然，像一个当地向导在介绍
5. 可以适当补充实用的旅游建议

回答："""
        return prompt
    
    def answer_question(self, query: str, region: str = "all", k: int = None) -> Dict:
        """回答问题"""
        if k is None:
            k = Config.TOP_K
            
        try:
            print(f"[QA系统] 开始处理问题: {query}")
            print(f"[QA系统] 检索参数 - 地区: {region}, Top-K: {k}")
            
            # 检索相关文档
            print("[QA系统] 开始向量检索...")
            documents = self.vector_store.search(query, k=k, region_filter=region)
            print(f"[QA系统] 检索到 {len(documents)} 个相关文档")
            
            if not documents:
                print("[QA系统] 未找到相关文档")
                return {
                    'success': False,
                    'answer': '抱歉，我没有找到相关的旅游信息。请尝试重新描述您的问题。',
                    'sources': []
                }
            
            # 构建提示词
            print("[QA系统] 构建提示词...")
            prompt = self._build_context_prompt(query, documents)
            print(f"[QA系统] 提示词长度: {len(prompt)} 字符")
            
            # 生成回答
            print("[QA系统] 调用大语言模型...")
            messages = [{"role": "user", "content": prompt}]
            response = self.chat_model.generate_response(messages)
            
            if response and response.choices:
                answer = response.choices[0].message.content
                print(f"[QA系统] 生成回答成功，长度: {len(answer)} 字符")
                
                # 构建来源信息
                sources = []
                for doc in documents:
                    source = {
                        'region': doc['metadata'].get('region', '江苏'),
                        'filename': doc['metadata'].get('filename', ''),
                        'chunk_id': doc['metadata'].get('chunk_id', 0),
                        'content_preview': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content']
                    }
                    sources.append(source)
                
                print(f"[QA系统] 问答完成，来源: {len(sources)} 个")
                return {
                    'success': True,
                    'answer': answer,
                    'sources': sources
                }
            else:
                print("[QA系统] 大语言模型返回为空")
                return {
                    'success': False,
                    'answer': '生成回答时出现错误，请稍后重试。',
                    'sources': []
                }
                
        except Exception as e:
            print(f"[QA系统] 发生错误: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'answer': '系统出现错误，请稍后重试。',
                'sources': []
            }
    
    def stream_answer(self, query: str, region: str = "all", k: int = None) -> Generator[Dict, None, None]:
        """流式回答问题"""
        if k is None:
            k = Config.TOP_K
            
        try:
            # 检索相关文档
            documents = self.vector_store.search(query, k=k, region_filter=region)
            
            if not documents:
                yield {
                    'content': '抱歉，我没有找到相关的旅游信息。请尝试重新描述您的问题。',
                    'done': True,
                    'sources': []
                }
                return
            
            # 构建提示词
            prompt = self._build_context_prompt(query, documents)
            
            # 流式生成回答
            messages = [{"role": "user", "content": prompt}]
            response = self.chat_model.generate_response(messages, stream=True)
            
            if response:
                full_content = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        yield {
                            'content': content,
                            'done': False,
                            'sources': []
                        }
                
                # 构建来源信息
                sources = []
                for doc in documents:
                    source = {
                        'region': doc['metadata'].get('region', '江苏'),
                        'filename': doc['metadata'].get('filename', ''),
                        'chunk_id': doc['metadata'].get('chunk_id', 0),
                        'content_preview': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content']
                    }
                    sources.append(source)
                
                # 发送完成信号和来源信息
                yield {
                    'content': '',
                    'done': True,
                    'sources': sources
                }
            else:
                yield {
                    'content': '生成回答时出现错误，请稍后重试。',
                    'done': True,
                    'sources': []
                }
                
        except Exception as e:
            print(f"Error in stream_answer: {e}")
            yield {
                'content': '系统出现错误，请稍后重试。',
                'done': True,
                'sources': []
            }
    
    def get_available_regions(self) -> List[str]:
        """获取可用的地区列表"""
        return [
            "all", "南京", "苏州", "扬州", "无锡", 
            "常州", "镇江", "连云港", "周庄", "同里"
        ]
# AI地点清理工具
import openai
from config.config import Config

class AILocationCleaner:
    """使用AI清理地点名称"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.API_BASE_URL
        )
    
    def clean_locations(self, raw_locations_text):
        """使用AI清理地点列表"""
        try:
            prompt = f"""
请从以下文本中提取出江苏省的地点名称，只返回纯净的地点名称，用逗号分隔。

要求：
1. 只提取江苏省内的城市、景点、地标
2. 移除所有描述性文字（如：步行约、米、景区、**、参观、游览等）
3. 去除重复地点
4. 最多返回6个地点
5. 只返回地点名称列表，不要任何其他文字

原始文本：{raw_locations_text}

请返回格式：地点1, 地点2, 地点3
"""
            
            response = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            cleaned_text = response.choices[0].message.content.strip()
            # 分割成列表并清理
            locations = [loc.strip() for loc in cleaned_text.split(',') if loc.strip()]
            
            print(f"AI清理前: {raw_locations_text}")
            print(f"AI清理后: {locations}")
            
            return locations[:6]  # 最多返回6个地点
            
        except Exception as e:
            print(f"AI地点清理失败: {e}")
            # 如果AI失败，使用简单的文本清理
            return self.simple_clean(raw_locations_text)
    
    def simple_clean(self, text):
        """简单的文本清理作为AI的后备方案"""
        import re
        
        # 江苏地点关键词
        jiangsu_locations = [
            '南京', '苏州', '无锡', '常州', '扬州', '镇江', 
            '南通', '泰州', '盐城', '淮安', '徐州', '连云港', '宿迁',
            '拙政园', '留园', '虎丘', '寒山寺', '狮子林', '网师园',
            '中山陵', '夫子庙', '总统府', '明孝陵', '玄武湖',
            '瘦西湖', '何园', '个园', '大明寺', '冶春园',
            '同里', '周庄', '锦溪', '甪直',
            '太湖', '天目湖', '茅山', '花果山', '金鸡湖',
            '古运河', '东关街'
        ]
        
        found_locations = []
        for location in jiangsu_locations:
            if location in text and location not in found_locations:
                found_locations.append(location)
        
        return found_locations[:6]
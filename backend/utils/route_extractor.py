# 后端路径提取工具
import re
from typing import List

class RouteExtractor:
    """路径提取工具类"""
    
    @staticmethod
    def extract_locations(content: str) -> List[str]:
        """从文本内容中提取地点信息，使用AI清理"""
        if not content:
            return []
        
        # 先使用基础方法提取原始地点文本
        raw_locations = RouteExtractor._extract_raw_locations(content)
        
        if not raw_locations:
            return []
        
        # 使用AI清理地点名称
        try:
            from utils.ai_location_cleaner import AILocationCleaner
            ai_cleaner = AILocationCleaner()
            
            # 将原始地点拼接成文本
            raw_text = ', '.join(raw_locations)
            
            # AI清理
            cleaned_locations = ai_cleaner.clean_locations(raw_text)
            
            print(f'AI清理结果: {cleaned_locations}')
            return cleaned_locations
            
        except Exception as e:
            print(f'AI清理失败，使用传统方法: {e}')
            return RouteExtractor._traditional_clean(raw_locations)
    
    @staticmethod
    def _extract_raw_locations(content: str) -> List[str]:
        """提取原始地点文本"""
        locations = []
        
        # 1. 优先提取【】标记的景点
        bracket_pattern = r'【([^】]+)】'
        bracket_matches = re.finditer(bracket_pattern, content)
        
        for match in bracket_matches:
            location = match.group(1).strip()
            if location not in locations:
                locations.append(location)
        
        print(f'从【】标记中提取: {locations}')
        
        # 2. 提取动词引导的地点
        if len(locations) < 5:
            route_patterns = [
                r'前往\s*([^，。！？\n]+)',
                r'参观\s*([^，。！？\n]+)',
                r'游览\s*([^，。！？\n]+)',
                r'到达\s*([^，。！？\n]+)',
                r'抵达\s*([^，。！？\n]+)',
                r'步行约[^，]*到\s*([^，。！？\n]+)',
                r'([^，。！？\n]*景区)',
                r'([^，。！？\n]*古镇)',
                r'([^，。！？\n]*公园)'
            ]
            
            for pattern in route_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    location = match.group(1).strip()
                    if location and len(location) < 50 and location not in locations:
                        locations.append(location)
        
        print(f'从动词模式中提取: {locations}')
        
        # 3. 提取**标记的重点
        star_pattern = r'\*\*([^*]+)\*\*'
        star_matches = re.finditer(star_pattern, content)
        
        for match in star_matches:
            location = match.group(1).strip()
            if location and location not in locations:
                locations.append(location)
        
        print(f'从**标记中提取: {locations}')
        
        return locations[:10]  # 最多10个原始地点送给AI清理
    
    @staticmethod
    def _traditional_clean(raw_locations):
        """传统清理方法作为备用"""
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
        
        found = []
        for raw in raw_locations:
            for place in jiangsu_locations:
                if place in raw and place not in found:
                    found.append(place)
        
        return found[:6]
    
    @staticmethod
    def contains_route_content(content: str) -> bool:
        """判断内容是否包含路径规划相关信息"""
        route_keywords = [
            '路线', '路径', '怎么去', '怎么走', '交通', '行程',
            '自驾', '导航', '距离', '开车', '乘车', '线路',
            '一日游', '二日游', '三日游', '多日游', '游览顺序',
            '第一天', '第二天', '第三天', '上午', '下午', '晚上'
        ]
        
        return any(keyword in content for keyword in route_keywords)
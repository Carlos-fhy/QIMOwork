import requests
import json
from config.config import Config

class AMapService:
    """高德地图服务"""
    
    def __init__(self):
        self.api_key = Config.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    def geocode(self, address, city="江苏"):
        """地理编码 - 将地址转换为坐标"""
        try:
            url = f"{self.base_url}/geocode/geo"
            params = {
                'key': self.api_key,
                'address': address,
                'city': city
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == '1' and data['geocodes']:
                location = data['geocodes'][0]['location']
                lng, lat = location.split(',')
                return {
                    'success': True,
                    'longitude': float(lng),
                    'latitude': float(lat),
                    'formatted_address': data['geocodes'][0]['formatted_address']
                }
            else:
                return {
                    'success': False,
                    'error': '地址解析失败'
                }
                
        except Exception as e:
            print(f"地理编码错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def driving_route(self, origin, destination):
        """驾车路线规划"""
        try:
            url = f"{self.base_url}/direction/driving"
            params = {
                'key': self.api_key,
                'origin': f"{origin['longitude']},{origin['latitude']}",
                'destination': f"{destination['longitude']},{destination['latitude']}",
                'strategy': 0  # 速度优先
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == '1' and data['route']['paths']:
                path = data['route']['paths'][0]
                return {
                    'success': True,
                    'distance': round(float(path['distance']) / 1000, 1),  # 转换为公里
                    'duration': self._format_duration(int(path['duration'])),
                    'steps': self._extract_steps(path['steps'])
                }
            else:
                return {
                    'success': False,
                    'error': '路线规划失败'
                }
                
        except Exception as e:
            print(f"路线规划错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_duration(self, seconds):
        """格式化时间"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def _extract_steps(self, steps):
        """提取路线步骤"""
        extracted_steps = []
        for step in steps:
            extracted_steps.append({
                'instruction': step.get('instruction', ''),
                'distance': round(float(step.get('distance', 0)) / 1000, 1),
                'duration': self._format_duration(int(step.get('duration', 0)))
            })
        return extracted_steps
    
    def get_poi_around(self, longitude, latitude, keywords, radius=5000):
        """搜索周边POI"""
        try:
            url = f"{self.base_url}/place/around"
            params = {
                'key': self.api_key,
                'location': f"{longitude},{latitude}",
                'keywords': keywords,
                'radius': radius,
                'types': '110000|120000|130000|140000|150000|160000|170000|180000|190000'  # 旅游景点相关类型
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == '1':
                pois = []
                for poi in data['pois']:
                    lng, lat = poi['location'].split(',')
                    pois.append({
                        'name': poi['name'],
                        'address': poi['address'],
                        'longitude': float(lng),
                        'latitude': float(lat),
                        'distance': poi.get('distance', '未知'),
                        'type': poi.get('type', '景点')
                    })
                
                return {
                    'success': True,
                    'pois': pois
                }
            else:
                return {
                    'success': False,
                    'error': 'POI搜索失败'
                }
                
        except Exception as e:
            print(f"POI搜索错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
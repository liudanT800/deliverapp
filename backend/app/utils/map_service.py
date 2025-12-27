"""
高德地图Web服务API工具类
提供距离计算、路径规划、地理编码等服务
"""
import os
import httpx
from typing import Dict, List, Optional, Tuple
from app.core.config import settings


class AMapWebService:
    """高德地图Web服务API客户端"""
    
    def __init__(self):
        self.api_key = settings.amap_web_service_key
        self.base_url = "https://restapi.amap.com/v3"
        
    async def get_distance(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]]
    ) -> Optional[Dict]:
        """
        计算多起点到多终点的距离和时间
        
        Args:
            origins: 起点列表 [(lng, lat), ...]
            destinations: 终点列表 [(lng, lat), ...]
            
        Returns:
            距离和时间信息
        """
        if not self.api_key or self.api_key == "CHANGE_ME":
            # 如果没有配置API密钥，返回模拟数据
            return self._mock_distance_result(origins, destinations)
        
        # 格式化起点和终点坐标
        origins_str = "|".join([f"{lng},{lat}" for lng, lat in origins])
        destinations_str = "|".join([f"{lng},{lat}" for lng, lat in destinations])
        
        url = f"{self.base_url}/distance"
        params = {
            "key": self.api_key,
            "origins": origins_str,
            "destination": destinations_str,
            "strategy": "0",  # 默认路线规划策略
            "output": "json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                result = response.json()
                
                if result.get("status") == "1" and "results" in result:
                    return result["results"]
                else:
                    print(f"高德地图API距离计算错误: {result.get('info', 'Unknown error')}")
                    return None
        except Exception as e:
            print(f"调用高德地图API时发生错误: {str(e)}")
            return None
    
    async def geocode(self, address: str) -> Optional[Dict]:
        """
        地理编码：将地址转换为经纬度
        
        Args:
            address: 地址字符串
            
        Returns:
            经纬度信息
        """
        if not self.api_key or self.api_key == "CHANGE_ME":
            # 如果没有配置API密钥，返回模拟数据
            return self._mock_geocode_result(address)
        
        url = f"{self.base_url}/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                result = response.json()
                
                if result.get("status") == "1" and len(result.get("geocodes", [])) > 0:
                    return result["geocodes"][0]
                else:
                    print(f"高德地图API地理编码错误: {result.get('info', 'Unknown error')}")
                    return None
        except Exception as e:
            print(f"调用高德地图API时发生错误: {str(e)}")
            return None
    
    async def regeocode(self, lng: float, lat: float) -> Optional[Dict]:
        """
        逆地理编码：将经纬度转换为地址
        
        Args:
            lng: 经度
            lat: 纬度
            
        Returns:
            地址信息
        """
        if not self.api_key or self.api_key == "CHANGE_ME":
            # 如果没有配置API密钥，返回模拟数据
            return self._mock_regeocode_result(lng, lat)
        
        url = f"{self.base_url}/geocode/regeo"
        params = {
            "key": self.api_key,
            "location": f"{lng},{lat}",
            "output": "json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                result = response.json()
                
                if result.get("status") == "1" and result.get("regeocode"):
                    return result["regeocode"]
                else:
                    print(f"高德地图API逆地理编码错误: {result.get('info', 'Unknown error')}")
                    return None
        except Exception as e:
            print(f"调用高德地图API时发生错误: {str(e)}")
            return None
    
    def _mock_distance_result(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]]
    ) -> Dict:
        """
        模拟距离计算结果（当没有API密钥时使用）
        """
        results = []
        for i in range(len(origins)):
            for j in range(len(destinations)):
                # 使用简化的距离计算公式模拟
                origin = origins[i]
                dest = destinations[j]
                
                # 简化计算两点间距离（米）
                lat_diff = abs(dest[1] - origin[1])
                lng_diff = abs(dest[0] - origin[0])
                
                # 约1度约等于111公里
                distance = round((lat_diff * 111000 + lng_diff * 111000) * 0.8, 0)
                # 简化时间计算（假设平均速度15km/h）
                time = round(distance / (15000 / 3600), 0)
                
                results.append({
                    "distance": {"value": str(distance), "text": f"{distance/1000:.2f}公里"},
                    "duration": {"value": str(time), "text": f"{time//60:.0f}分钟"},
                    "origin_id": i,
                    "destination_id": j
                })
        
        return results
    
    def _mock_geocode_result(self, address: str) -> Dict:
        """
        模拟地理编码结果（当没有API密钥时使用）
        """
        # 对于演示目的，返回北京天安门的坐标
        return {
            "formatted_address": address,
            "location": "116.397428,39.90923",
            "level": "门牌号"
        }
    
    def _mock_regeocode_result(self, lng: float, lat: float) -> Dict:
        """
        模拟逆地理编码结果（当没有API密钥时使用）
        """
        return {
            "formatted_address": f"模拟地址({lng:.6f}, {lat:.6f})",
            "addressComponent": {
                "city": "北京市",
                "province": "北京市",
                "district": "东城区",
                "township": "东华门街道",
                "neighborhood": "天安门广场",
                "building": "模拟建筑"
            }
        }


# 全局地图服务实例
amap_service = AMapWebService()
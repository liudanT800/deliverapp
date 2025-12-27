"""
地图服务API路由
提供地理编码、逆地理编码等服务
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.response import ResponseModel
from app.services.task_service import geocode_location
from app.utils.map_service import amap_service


router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("/geocode")
async def geocode_address(
    address: str = Query(..., description="要编码的地址"),
    session: Annotated[AsyncSession, Depends(deps.get_db)] = None,
):
    """
    地理编码：将地址转换为经纬度
    """
    result = await geocode_location(address)
    if result:
        # 如果后端返回了location字段（格式为"lng,lat"），直接返回
        if 'location' in result:
            location_str = result['location']
        else:
            # 从geocodes中提取坐标
            location_data = result.get('geocodes', [{}])[0] if 'geocodes' in result else result
            location_str = location_data.get('location', '0,0')
        
        # 格式化响应以匹配前端期望的格式
        formatted_result = {
            'formatted_address': result.get('formatted_address', address),
            'location': location_str,
            'level': result.get('level', '地名')
        }
        
        return ResponseModel(
            success=True,
            message="地理编码成功",
            data=formatted_result
        )
    else:
        return ResponseModel(
            success=False,
            message="地理编码失败",
            data=None
        )


@router.get("/reverse-geocode")
async def reverse_geocode(
    lng: float = Query(..., description="经度"),
    lat: float = Query(..., description="纬度"),
    session: Annotated[AsyncSession, Depends(deps.get_db)] = None,
):
    """
    逆地理编码：将经纬度转换为地址
    """
    result = await amap_service.regeocode(lng, lat)
    if result:
        return ResponseModel(
            success=True,
            message="逆地理编码成功",
            data=result
        )
    else:
        return ResponseModel(
            success=False,
            message="逆地理编码失败",
            data=None
        )
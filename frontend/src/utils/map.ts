/**
 * 地图服务工具类
 * 基于高德地图API封装的工具函数
 */

export interface LocationData {
  name: string
  address: string
  lat: number
  lng: number
}

export interface MapConfig {
  apiKey: string
  version: string
  plugins: string[]
}

// 地图配置
export const MAP_CONFIG: MapConfig = {
  apiKey: import.meta.env.VITE_AMAP_API_KEY || 'your-amap-api-key',
  version: '2.0',
  plugins: ['AMap.Geocoder', 'AMap.PlaceSearch', 'AMap.Geolocation']
}

/**
 * 检查地图API是否可用
 */
export function isMapApiAvailable(): boolean {
  return !!(window as any).AMap
}

/**
 * 格式化坐标为高德地图格式
 */
export function formatLngLat(lng: number, lat: number): [number, number] {
  return [lng, lat]
}

/**
 * 解析高德地图坐标格式
 */
export function parseLngLat(lnglat: [number, number]): { lng: number; lat: number } {
  return {
    lng: lnglat[0],
    lat: lnglat[1]
  }
}

/**
 * 计算两点之间的距离（米）
 */
export function calculateDistance(
  point1: { lng: number; lat: number },
  point2: { lng: number; lat: number }
): number {
  if (!isMapApiAvailable()) {
    // 简化的距离计算（非精确）
    const R = 6371000 // 地球半径（米）
    const dLat = (point2.lat - point1.lat) * Math.PI / 180
    const dLng = (point2.lng - point1.lng) * Math.PI / 180
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  const AMap = (window as any).AMap
  const p1 = new AMap.LngLat(point1.lng, point1.lat)
  const p2 = new AMap.LngLat(point2.lng, point2.lat)
  return p1.distance(p2)
}

/**
 * 地址搜索
 */
export async function searchPlaces(
  keyword: string,
  options: {
    city?: string
    pageSize?: number
    pageIndex?: number
  } = {}
): Promise<any[]> {
  return new Promise((resolve, reject) => {
    if (!isMapApiAvailable()) {
      reject(new Error('地图API不可用'))
      return
    }

    const AMap = (window as any).AMap
    const placeSearch = new AMap.PlaceSearch({
      city: options.city || '全国',
      pageSize: options.pageSize || 10,
      pageIndex: options.pageIndex || 1
    })

    placeSearch.search(keyword, (status: string, result: any) => {
      if (status === 'complete' && result.info === 'OK') {
        resolve(result.poiList.pois)
      } else {
        reject(new Error('搜索失败'))
      }
    })
  })
}

/**
 * 地理编码（地址转坐标）
 */
export async function geocode(address: string, city?: string): Promise<LocationData> {
  return new Promise((resolve, reject) => {
    if (!isMapApiAvailable()) {
      reject(new Error('地图API不可用'))
      return
    }

    const AMap = (window as any).AMap
    const geocoder = new AMap.Geocoder({
      city: city || '全国'
    })

    geocoder.getLocation(address, (status: string, result: any) => {
      if (status === 'complete' && result.info === 'OK' && result.geocodes.length > 0) {
        const geocode = result.geocodes[0]
        resolve({
          name: geocode.formattedAddress,
          address: geocode.formattedAddress,
          lat: geocode.location.lat,
          lng: geocode.location.lng
        })
      } else {
        reject(new Error('地理编码失败'))
      }
    })
  })
}

/**
 * 逆地理编码（坐标转地址）
 */
export async function reverseGeocode(lng: number, lat: number): Promise<LocationData> {
  return new Promise((resolve, reject) => {
    if (!isMapApiAvailable()) {
      reject(new Error('地图API不可用'))
      return
    }

    const AMap = (window as any).AMap
    const geocoder = new AMap.Geocoder()

    geocoder.getAddress([lng, lat], (status: string, result: any) => {
      if (status === 'complete' && result.info === 'OK') {
        const addressComponent = result.regeocode.addressComponent
        const formattedAddress = result.regeocode.formattedAddress

        resolve({
          name: addressComponent.building || addressComponent.neighborhood || '位置',
          address: formattedAddress,
          lat,
          lng
        })
      } else {
        reject(new Error('逆地理编码失败'))
      }
    })
  })
}

/**
 * 获取当前位置
 */
export async function getCurrentLocation(): Promise<LocationData> {
  return new Promise((resolve, reject) => {
    if (!isMapApiAvailable()) {
      reject(new Error('地图API不可用'))
      return
    }

    const AMap = (window as any).AMap
    const geolocation = new AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 10000
    })

    geolocation.getCurrentPosition((status: string, result: any) => {
      if (status === 'complete') {
        const lng = result.position.lng
        const lat = result.position.lat

        // 获取地址信息
        reverseGeocode(lng, lat)
          .then(resolve)
          .catch(() => {
            // 如果逆地理编码失败，返回基础位置信息
            resolve({
              name: '当前位置',
              address: `${lng.toFixed(6)}, ${lat.toFixed(6)}`,
              lat,
              lng
            })
          })
      } else {
        reject(new Error('获取当前位置失败'))
      }
    })
  })
}

/**
 * 验证坐标是否有效
 */
export function isValidCoordinate(lng: number, lat: number): boolean {
  return lng >= -180 && lng <= 180 && lat >= -90 && lat <= 90
}

/**
 * 格式化距离显示
 */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}米`
  } else {
    return `${(meters / 1000).toFixed(1)}公里`
  }
}

/**
 * 通过后端API进行逆地理编码
 */
export async function reverseGeocodeBackend(lng: number, lat: number): Promise<LocationData> {
  try {
    const response = await fetch(`/api/maps/reverse-geocode?lng=${lng}&lat=${lat}`);
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status} - ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success && result.data) {
      const addressComponent = result.data.addressComponent || {};
      // 确保 name 属性是字符串，防止对象被传递给Vue组件
      const building = typeof addressComponent.building === 'string' ? addressComponent.building : '';
      const neighborhood = typeof addressComponent.neighborhood === 'string' ? addressComponent.neighborhood : '';
      const name = building || neighborhood || `坐标位置(${lng.toFixed(6)}, ${lat.toFixed(6)})`;
      
      return {
        name: name,
        address: result.data.formatted_address || `坐标: ${lng.toFixed(6)}, ${lat.toFixed(6)}`,
        lat: lat,
        lng: lng
      };
    } else {
      throw new Error(result.message || '逆地理编码失败');
    }
  } catch (error) {
    console.error('后端逆地理编码失败:', error);
    throw error;
  }
}

/**
 * 通过后端API进行地理编码
 */
export async function geocodeBackend(address: string): Promise<LocationData> {
  try {
    const encodedAddress = encodeURIComponent(address);
    const response = await fetch(`/api/maps/geocode?address=${encodedAddress}`);
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status} - ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success && result.data && result.data.location) {
      const locationParts = result.data.location.split(',');
      if (locationParts.length < 2) {
        throw new Error('后端返回的坐标格式不正确');
      }
      
      const lng = parseFloat(locationParts[0]);
      const lat = parseFloat(locationParts[1]);
      
      if (isNaN(lng) || isNaN(lat)) {
        throw new Error('后端返回的坐标不是有效数字');
      }
      
      // 确保 name 属性是字符串，防止对象被传递给Vue组件
      const formattedAddress = typeof result.data.formatted_address === 'string' ? result.data.formatted_address : '';
      const name = formattedAddress || address;
      
      return {
        name: name,
        address: formattedAddress || address,
        lat: lat,
        lng: lng
      };
    } else {
      throw new Error(result.message || '地理编码失败');
    }
  } catch (error) {
    console.error('后端地理编码失败:', error);
    throw error;
  }
}

/**
 * 地图类型定义扩展
 */
declare global {
  interface Window {
    AMap: any
  }
}

<!--
  高德地图选址组件 - 基于高德JS API 2.0实现
  官方文档参考: https://lbs.amap.com/api/javascript-api-v2/tutorails/display-a-map
  功能: 地图显示、地点搜索、坐标选址、地理编码等
-->
<template>
  <div class="map-selector">
    <!-- 调试信息 -->
    <div v-if="debugMode" class="debug-info">
      <p>地图状态: {{ mapLoaded ? '已加载' : '未加载' }}</p>
      <p>点击计数: {{ clickCount }}</p>
      <p>搜索关键词: {{ searchKeyword || '无' }}</p>
      <p>搜索结果数: {{ searchResults.length }}</p>
      <p>选中位置: {{ selectedLocation ? `${selectedLocation.lat}, ${selectedLocation.lng}` : '无' }}</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <n-input
        v-model:value="searchKeyword"
        placeholder="搜索地点名称或地址"
        @keyup.enter="searchPlaces"
        clearable
        class="map-search-input"
      >
        <template #suffix>
          <n-button @click="searchPlaces" size="small">
            <template #icon>
              <n-icon><SearchIcon /></n-icon>
            </template>
          </n-button>
        </template>
      </n-input>
    </div>

    <!-- 地图容器 -->
    <div class="map-container" ref="mapContainer">
      <n-spin v-if="loading" class="loading-overlay" show>
        <template #description>
          正在加载地图...
        </template>
      </n-spin>
      <div v-else-if="!mapLoaded" class="map-placeholder">
        <n-empty description="地图加载失败">
          <template #extra>
            <div style="text-align: center; max-width: 400px;">
              <p style="margin-bottom: 1rem; color: #ff6b6b; font-size: 14px; line-height: 1.5;">
                高德地图API密钥配置错误<br>
                请按以下步骤解决：
              </p>
              <ol style="text-align: left; margin-bottom: 1rem; font-size: 13px; color: #666;">
                <li>访问 <a href="https://lbs.amap.com/dev/key/app" target="_blank" style="color: #18a058;">高德地图控制台</a></li>
                <li>创建Web应用(JS API)类型的应用</li>
                <li>获取API Key并配置到frontend/.env文件</li>
              </ol>
              <n-space vertical>
                <n-button @click="initMap">重新加载</n-button>
                <n-button text @click="openConfigGuide">
                  📖 详细配置指南
                </n-button>
              </n-space>
            </div>
          </template>
        </n-empty>
      </div>
    </div>

    <!-- 搜索结果列表 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="results-header">
        <span>搜索结果 ({{ searchResults.length }})</span>
        <n-button text @click="clearSearch">清除</n-button>
      </div>
      <n-scrollbar style="max-height: 200px;">
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="result-item"
          @click="selectResult(result)"
        >
          <div class="result-info">
            <strong>{{ result.name }}</strong>
            <p>{{ result.address }}</p>
          </div>
          <n-icon v-if="selectedResult?.id === result.id" color="#18a058">
            <CheckIcon />
          </n-icon>
        </div>
      </n-scrollbar>
    </div>

    <!-- 操作按钮 -->
    <div class="map-actions">
      <n-space>
        <n-button @click="getCurrentLocation" :loading="gettingLocation">
          <template #icon>
            <n-icon><LocationIcon /></n-icon>
          </template>
          我的位置
        </n-button>
        <n-button @click="resetMap">
          <template #icon>
            <n-icon><RefreshIcon /></n-icon>
          </template>
          重置
        </n-button>
        <n-button v-if="locationError" @click="locationError = ''" type="warning" ghost>
          清除提示
        </n-button>
        <n-button type="primary" @click="confirmSelection" :disabled="!selectedLocation">
          确认选择
        </n-button>
      </n-space>
    </div>

    <!-- 定位失败提示 -->
    <div v-if="locationError" class="location-error">
      <n-alert type="warning" :show-icon="false" :show-close="true" @close="locationError = ''">
        <template #header>
          <strong>📍 定位服务提示</strong>
        </template>
        {{ locationError }}
        <br><br>
        💡 <strong>手动选择位置：</strong>直接点击地图上的任意位置即可选择
      </n-alert>
    </div>

    <!-- 当前选择信息 -->
    <div v-if="selectedLocation" class="selected-info">
      <n-card size="small">
        <template #header>
          <strong>已选择地点</strong>
        </template>
        <div class="location-details">
          <p><strong>{{ selectedLocation.name }}</strong></p>
          <p>{{ selectedLocation.address }}</p>
          <p class="coordinates">
            坐标: {{ selectedLocation.lng.toFixed(6) }}, {{ selectedLocation.lat.toFixed(6) }}
          </p>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { NInput, NButton, NIcon, NSpin, NEmpty, NScrollbar, NSpace, NCard } from 'naive-ui'
import { SearchOutline as SearchIcon, CheckmarkOutline as CheckIcon, LocationOutline as LocationIcon, RefreshOutline as RefreshIcon } from '@vicons/ionicons5'

// 导入高德地图JS API加载器
// 参考官方文档: https://lbs.amap.com/api/javascript-api-v2/tutorails/display-a-map
import AMapLoader from '@amap/amap-jsapi-loader'

// 类型定义
interface LocationData {
  name: string
  address: string
  lat: number
  lng: number
}

interface SearchResult {
  id: string
  name: string
  address: string
  location: [number, number] // [lng, lat]
}

// Props
interface Props {
  defaultLocation?: LocationData
  apiKey?: string
}

const props = withDefaults(defineProps<Props>(), {
  apiKey: import.meta.env.VITE_AMAP_API_KEY || 'your-amap-api-key'
})

// Emits
const emit = defineEmits<{
  confirm: [location: LocationData]
  cancel: []
}>()

// 响应式数据
const mapContainer = ref<HTMLDivElement>()
const searchKeyword = ref('')
const loading = ref(true)
const mapLoaded = ref(false)
const gettingLocation = ref(false)
const locationError = ref('')
const selectedLocation = ref<LocationData>()
const selectedResult = ref<SearchResult>()
const searchResults = ref<SearchResult[]>([])

// 调试相关
const debugMode = ref(false) // 设为true启用调试信息
const clickCount = ref(0)

// 高德地图实例
let map: any = null
let marker: any = null
let geocoder: any = null
let placeSearch: any = null

// 初始化地图
async function initMap() {
  if (!mapContainer.value) return

  try {
    loading.value = true

    // 检查API密钥
    if (!props.apiKey || props.apiKey === 'your-amap-api-key' || props.apiKey === 'your_actual_amap_api_key_here') {
      throw new Error('高德地图API密钥未正确配置。请访问 https://lbs.amap.com/dev/key/app 申请Web端(JS API)密钥，并在frontend/.env文件中设置VITE_AMAP_API_KEY')
    }

    // 加载高德地图JS API
    const AMap = await AMapLoader.load({
      key: props.apiKey,
      version: '2.0',
      plugins: ['AMap.Geocoder', 'AMap.PlaceSearch', 'AMap.Geolocation']
    })

    // 创建地图实例 - 按照高德JS API官方文档最佳实践
    // 参考: https://lbs.amap.com/api/javascript-api-v2/tutorails/display-a-map
    map = new AMap.Map(mapContainer.value, {
      viewMode: '2D',              // 地图渲染模式: '2D'平面模式, '3D'带有俯仰角的3D模式
      zoom: 15,                    // 初始化地图层级，值越大放大比例越大
      center: [116.397428, 39.90923], // 初始化地图中心点经纬度（北京天安门坐标）
      mapStyle: 'amap://styles/normal' // 设置地图的显示样式，可使用官方主题或自定义样式
    })

    // 创建地理编码实例 - 用于地址和坐标转换
    geocoder = new AMap.Geocoder({
      city: '全国' // 搜索全国范围
    })

    // 创建地点搜索实例 - 用于地点搜索
    placeSearch = new AMap.PlaceSearch({
      city: '全国', // 搜索全国范围
      pageSize: 10, // 每页显示10个结果
      pageIndex: 1  // 第一页
    })

    // 设置Canvas观察器以监控动态创建的Canvas元素
    await nextTick(); // 确保DOM已更新
    setupCanvasObserver();
    
    // 监听地图事件
    map.on('complete', () => {
      console.log('高德地图加载完成')
      mapLoaded.value = true
      loading.value = false // 地图加载完成后隐藏loading overlay

      // 在地图完全加载完成后绑定点击事件
      map.on('click', (e: any) => {
        clickCount.value++
        const lnglat = e.lnglat
        handleMapClick(lnglat)
      })
      
      // 延迟执行Canvas优化以确保地图Canvas元素已创建
      setTimeout(() => {
        optimizeCanvas();
        
        // 启动持续Canvas性能优化
        isCanvasOptimizationActive = true;
        continuousCanvasOptimization();
      }, 100);
    })

    // 如果有默认位置，设置标记
    if (props.defaultLocation) {
      setMarker(props.defaultLocation.lng, props.defaultLocation.lat)
      selectedLocation.value = props.defaultLocation
    }

  } catch (error) {
    console.error('高德地图加载失败:', error)
    mapLoaded.value = false

    // 显示用户友好的错误信息
    if (error instanceof Error && error.message.includes('API密钥')) {
      console.warn('请配置高德地图API密钥：', error.message)
    } else {
      console.error('地图初始化失败，请检查网络连接或API密钥配置')
    }
  } finally {
    loading.value = false
  }
}

// 地图点击处理
function handleMapClick(lnglat: any) {
  const lng = lnglat.lng
  const lat = lnglat.lat

  // 逆地理编码获取地址信息
  geocoder.getAddress([lng, lat], (status: string, result: any) => {
    if (status === 'complete' && result.info === 'OK') {
      const addressComponent = result.regeocode.addressComponent
      const formattedAddress = result.regeocode.formattedAddress
  
      const location: LocationData = {
        name: addressComponent.building || addressComponent.neighborhood || '选定位置',
        address: formattedAddress,
        lat,
        lng
      }
  
      setMarker(lng, lat)
      selectedLocation.value = location
      selectedResult.value = undefined
      locationError.value = '' // 清除错误信息
    } else {
      // 前端地理编码失败，尝试使用后端地理编码服务
      console.warn('前端地理编码失败，尝试使用后端服务')
              
      // 使用智能逆地理编码，自动降级处理
      import('../utils/map').then(({ smartReverseGeocode }) => {
        smartReverseGeocode(lng, lat)
          .then(smartResult => {
            setMarker(lng, lat)
            selectedLocation.value = smartResult
            selectedResult.value = undefined
            locationError.value = '' // 清除错误信息
            console.log('通过智能逆地理编码成功获取地址信息')
          })
          .catch(smartError => {
            console.warn('智能逆地理编码失败，使用默认位置信息', smartError)
            const location: LocationData = {
              name: '点击位置',
              address: `坐标: ${lng.toFixed(6)}, ${lat.toFixed(6)}`,
              lat,
              lng
            }
      
            setMarker(lng, lat)
            selectedLocation.value = location
            selectedResult.value = undefined
      
            // 显示友好的提示信息
            locationError.value = '地址解析失败，但您仍可以选择此位置。系统已尝试使用多种方式获取地址信息。'
          })
      })
    }
  })
}

// 设置标记
function setMarker(lng: number, lat: number) {
  if (marker) {
    map.remove(marker)
  }

  marker = new (window as any).AMap.Marker({
    position: [lng, lat],
    map: map
  })

  // 移动地图中心到标记位置
  map.setCenter([lng, lat])
}

// Canvas优化观察器
let canvasObserver: MutationObserver | null = null;

// 持续优化控制变量
let isCanvasOptimizationActive = false;

// 设置Canvas观察器以监控动态创建的Canvas元素
function setupCanvasObserver() {
  if (!mapContainer.value) return;
  
  // 创建观察器以监控地图容器中的变化
  canvasObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      // 检查是否有新的Canvas元素被添加
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element;
            
            // 如果添加的元素是Canvas，直接优化
            if (element.tagName === 'CANVAS') {
              optimizeCanvasElement(element as HTMLCanvasElement);
            }
            
            // 检查添加的元素内部是否包含Canvas元素
            const canvases = element.querySelectorAll('canvas');
            canvases.forEach(canvas => {
              optimizeCanvasElement(canvas);
            });
          }
        });
      }
    });
  });
  
  // 开始观察地图容器的变化
  canvasObserver.observe(mapContainer.value, {
    childList: true,
    subtree: true
  });
}

// 优化单个Canvas元素
function optimizeCanvasElement(canvas: HTMLCanvasElement) {
  try {
    const context = canvas.getContext('2d');
    if (context && !(context as any).isOptimized) {
      (context as any).willReadFrequently = true;
      (context as any).isOptimized = true; // 标记为已优化，避免重复优化
      console.log('Canvas element optimized for performance');
    }
  } catch (error) {
    console.warn('Failed to optimize canvas element:', error);
  }
}

// 优化Canvas性能
function optimizeCanvas() {
  // 由于高德地图内部使用Canvas，我们需要尝试优化Canvas性能
  // 通过查询地图容器内的canvas元素并设置willReadFrequently属性
  if (mapContainer.value) {
    const canvases = mapContainer.value.querySelectorAll('canvas');
    canvases.forEach(canvas => {
      optimizeCanvasElement(canvas);
    });
  }
  
  // 同时也检查全局的canvas元素
  const allCanvases = document.querySelectorAll('canvas');
  allCanvases.forEach(canvas => {
    optimizeCanvasElement(canvas as HTMLCanvasElement);
  });
}

// 持续Canvas性能优化
function continuousCanvasOptimization() {
  if (!isCanvasOptimizationActive) return;
  
  optimizeCanvas();
  
  // 使用requestAnimationFrame确保优化在每一帧都执行
  requestAnimationFrame(continuousCanvasOptimization);
}

// 搜索地点
function searchPlaces() {
  console.log('开始搜索地点:', searchKeyword.value)
  if (!searchKeyword.value.trim()) return

  if (!placeSearch) {
    console.error('placeSearch未初始化')
    return
  }

  placeSearch.search(searchKeyword.value, (status: string, result: any) => {
    console.log('地点搜索结果:', status, result)
    if (status === 'complete' && result.info === 'OK') {
      searchResults.value = result.poiList.pois.map((poi: any, index: number) => ({
        id: poi.id || `result-${index}`,
        name: poi.name,
        address: poi.address,
        location: poi.location
      }))
      console.log('搜索到', searchResults.value.length, '个结果')
      locationError.value = '' // 清除之前的错误信息
    } else {
      searchResults.value = []
      console.warn('地点搜索失败:', status, result)

      // 显示用户友好的错误提示
      if (status === 'no_data') {
        locationError.value = `未找到包含"${searchKeyword.value}"的地点，请尝试其他关键词`
      } else if (result.info === 'INVALID_USER_SCODE') {
        locationError.value = '地点搜索服务未开通，请在高德地图控制台开通"地点搜索"服务'
      } else {
        locationError.value = '地点搜索暂时不可用，请稍后重试或直接点击地图选择位置'
      }
    }
  })
}

// 选择搜索结果
function selectResult(result: SearchResult) {
  selectedResult.value = result

  const [lng, lat] = result.location
  const location: LocationData = {
    name: result.name,
    address: result.address,
    lat,
    lng
  }

  setMarker(lng, lat)
  selectedLocation.value = location
}

// 获取当前位置
function getCurrentLocation() {
  gettingLocation.value = true
  locationError.value = '' // 清除之前的错误信息

  const geolocation = new (window as any).AMap.Geolocation({
    enableHighAccuracy: true,     // 是否使用高精度定位，默认：true
    timeout: 15000,               // 增加超时时间到15秒，默认：无穷大
    maximumAge: 60000,            // 允许使用1分钟内的缓存位置，默认：0
    convert: true,                 // 自动偏移坐标，偏移后的坐标为高德坐标，默认：true
    showButton: false,             // 显示定位按钮，默认：true
    buttonPosition: 'LB',          // 定位按钮停靠位置，默认：'LB'，左下角
    buttonOffset: new (window as any).AMap.Pixel(10, 20), // 定位按钮与设置的停靠位置的偏移量，默认：Pixel(10, 20)
    showMarker: false,             // 定位成功后在定位到的位置显示点标记，默认：true
    showCircle: false,             // 定位成功后用圆圈表示定位精度范围，默认：true
    panToLocation: false,          // 定位成功后将定位到的位置作为地图中心点，默认：true
    zoomToAccuracy: false          // 定位成功后调整地图视野范围使定位位置及精度范围视野内可见，默认：false
  })

  geolocation.getCurrentPosition((status: string, result: any) => {
    gettingLocation.value = false

    if (status === 'complete') {
      const lng = result.position.lng
      const lat = result.position.lat

      // 逆地理编码获取地址信息
      geocoder.getAddress([lng, lat], (status: string, result: any) => {
        if (status === 'complete' && result.info === 'OK') {
          const addressComponent = result.regeocode.addressComponent
          const formattedAddress = result.regeocode.formattedAddress

          const location: LocationData = {
            name: addressComponent.building || addressComponent.neighborhood || '当前位置',
            address: formattedAddress,
            lat,
            lng
          }

          setMarker(lng, lat)
          selectedLocation.value = location
          selectedResult.value = undefined
        } else {
          // 前端地理编码失败，尝试使用后端地理编码服务
          console.warn('前端地理编码失败，尝试使用后端服务获取当前位置')
          
          // 使用智能逆地理编码，自动降级处理
          import('../utils/map').then(({ smartReverseGeocode }) => {
            smartReverseGeocode(lng, lat)
              .then(smartResult => {
                setMarker(lng, lat)
                selectedLocation.value = smartResult
                selectedResult.value = undefined
                console.log('通过智能逆地理编码成功获取当前位置信息')
              })
              .catch(smartError => {
                console.warn('智能逆地理编码失败，使用默认位置信息', smartError)
                const location: LocationData = {
                  name: '当前位置',
                  address: `坐标: ${lng.toFixed(6)}, ${lat.toFixed(6)}`,
                  lat,
                  lng
                }
                setMarker(lng, lat)
                selectedLocation.value = location
                selectedResult.value = undefined
              })
          })
        }
      })
    } else {
      console.error('获取当前位置失败:', result)

      // 显示用户友好的错误提示
      let errorMessage = '获取当前位置失败'
      let errorSuggestion = ''

      switch (result.status) {
        case 1:
          errorMessage = '地理定位超时'
          errorSuggestion = '网络连接较慢，请稍候重试或手动点击地图选择位置'
          break
        case 2:
          errorMessage = '位置信息不可用'
          errorSuggestion = '您的浏览器不支持地理定位功能，请手动点击地图选择位置'
          break
        case 3:
          errorMessage = '地理定位被拒绝'
          errorSuggestion = '请点击浏览器地址栏左侧的定位图标，允许网站访问您的位置'
          break
        default:
          errorSuggestion = '定位服务暂时不可用，请手动点击地图选择位置'
      }

      // 设置错误信息供用户查看
      locationError.value = `${errorMessage}。${errorSuggestion}`

      // 同时在控制台显示详细信息
      console.warn(`${errorMessage}: ${errorSuggestion}`, result)
    }
  })
}

// 重置地图
function resetMap() {
  if (marker) {
    map.remove(marker)
    marker = null
  }
  selectedLocation.value = undefined
  selectedResult.value = undefined
  searchResults.value = []
  searchKeyword.value = ''
  locationError.value = '' // 清除错误信息

  // 重置到默认中心点
  map.setZoom(15)
  map.setCenter([116.3974, 39.9093])
}

// 清除搜索结果
function clearSearch() {
  searchResults.value = []
  searchKeyword.value = ''
  locationError.value = '' // 清除错误信息
}

// 确认选择
function confirmSelection() {
  if (selectedLocation.value) {
    emit('confirm', selectedLocation.value)
  }
}

// 取消选择
function cancelSelection() {
  emit('cancel')
}

// 打开配置指南
function openConfigGuide() {
  const guide = `🔧 高德地图API配置步骤：

1️⃣ 访问控制台：
   https://lbs.amap.com/dev/key/app

2️⃣ 注册/登录账号

3️⃣ 创建应用：
   - 应用名称：顺路带校园互助平台
   - 应用类型：Web应用(JS API) ⭐重要！

4️⃣ 添加API Key：
   - Key名称：地图选址功能
   - 服务平台：Web端(JS API)

5️⃣ 配置到项目：
   编辑 frontend/.env 文件：
   VITE_AMAP_API_KEY=你的真实API密钥

6️⃣ 重启前端服务：
   cd frontend && npm run dev

📖 详细文档：查看项目根目录的 MAP_API_SETUP.md

❓ 常见问题：
   - 确保应用类型是"Web应用(JS API)"
   - 检查API Key是否正确复制
   - 等待5分钟后重试（密钥生效需要时间）
  `
  alert(guide)
}

// 生命周期
onMounted(async () => {
  await nextTick()
  await initMap()
})

onUnmounted(() => {
  // 销毁地图实例，释放资源
  if (map) {
    map.destroy()
    map = null
  }

  // 清理其他地图相关实例
  marker = null
  geocoder = null
  placeSearch = null
  
  // 清理Canvas优化设置
  const canvases = document.querySelectorAll('canvas');
  canvases.forEach(canvas => {
    try {
      const context = canvas.getContext('2d');
      if (context) {
        (context as any).willReadFrequently = false;
        (context as any).isOptimized = false; // 移除优化标记
      }
    } catch (error) {
      console.warn('Failed to cleanup canvas element:', error);
    }
  })
  
  // 停止Canvas观察器
  if (canvasObserver) {
    canvasObserver.disconnect();
    canvasObserver = null;
  }
  
  // 停止持续Canvas优化
  isCanvasOptimizationActive = false;
})
</script>

<style scoped>
.map-selector {
  display: flex;
  flex-direction: column;
  height: 600px;
  border-radius: var(--radius-medium);
  overflow: hidden;
}

.debug-info {
  padding: 0.5rem;
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
  font-size: 12px;
  color: #666;
}

.debug-info p {
  margin: 0.25rem 0;
}

.search-bar {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.map-search-input {
  width: 100%;
}

.map-container {
  flex: 1;
  position: relative;
  min-height: 400px;
  cursor: crosshair; /* 显示十字光标表示可点击 */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
}

.map-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
}

.search-results {
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.result-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s;
}

.result-item:hover {
  background: var(--bg-hover);
}

.result-item:last-child {
  border-bottom: none;
}

.result-info {
  flex: 1;
}

.result-info strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.result-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.map-actions {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.location-error {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.selected-info {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.location-details p {
  margin: 0.25rem 0;
}

.coordinates {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-family: monospace;
}
</style>

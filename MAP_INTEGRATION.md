# 地图SDK集成指南

本文档详细说明如何配置和使用高德地图SDK实现精确选址功能。

## 📋 功能概述

项目已集成高德地图SDK，提供以下功能：
- 📍 地图选址：在任务发布时精确选择取件/送达地点
- 🔍 地址搜索：支持地点名称搜索快速定位
- 📍 当前位置：一键获取当前位置
- 🎯 坐标存储：自动保存经纬度信息到数据库

## 🔧 配置步骤

### 1. 申请高德地图API密钥

1. 访问 [高德地图开放平台](https://lbs.amap.com/dev/key/app)
2. 注册账号并创建应用
3. 选择"Web端(JS API)"类型
4. 申请API Key（密钥）

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 高德地图API配置
VITE_AMAP_API_KEY=your_actual_api_key_here

# 其他配置
VITE_API_PROXY=http://localhost:8000
```

### 3. 安装依赖

```bash
cd frontend
npm install  # 会自动安装 @amap/amap-jsapi-loader
```

## 🚀 使用方法

### 发布任务时的地图选址

1. **配置API密钥**：
   ```bash
   # 在 frontend/.env 文件中
   VITE_AMAP_API_KEY=你的高德地图API密钥
   ```

2. **使用地图选址**：
   - 在任务发布页面点击"地图选址"按钮
   - 在弹出的地图界面中：
     - **直接点击地图**：选择任意位置
     - **搜索地点**：在搜索框输入地点名称
     - **获取当前位置**：点击"我的位置"按钮
   - 确认选择后，地点信息和坐标会自动填入表单

### 地图功能说明

- **地图显示**：基于高德地图JS API 2.0，显示标准地图样式
- **坐标系**：使用GCJ-02坐标系（高德坐标）
- **精度**：支持精确到小数点后6位的坐标精度
- **响应式**：地图容器自适应不同屏幕尺寸
- **地点搜索**：POI搜索功能，支持地点名称快速定位（需要开通地点搜索服务）
- **地理定位**：支持高精度GPS定位，超时自动降级为手动选择
- **地址解析**：逆地理编码获取详细地址信息（需要开通地理编码服务）
- **错误处理**：完善的搜索失败、定位失败处理和用户友好的错误提示

### 服务开通要求

为了获得最佳的地图体验，请确保在高德地图控制台中开通以下服务：

- ✅ **地图显示** - 基础地图显示
- ✅ **地点搜索** - 支持地点名称搜索
- ✅ **地理编码** - 地址转坐标
- ✅ **逆地理编码** - 坐标转地址 ⭐ 重要！
- ✅ **定位** - GPS定位服务

### 技术实现细节

#### 组件结构

```
frontend/src/
├── components/
│   └── MapSelector.vue      # 地图选择器组件
├── utils/
│   └── map.ts              # 地图工具类
└── views/
    └── TaskCreateView.vue  # 任务发布页面（已集成地图组件）
```

#### 数据模型

数据库中的任务表已包含经纬度字段：

```sql
-- 取件地点坐标
pickup_lat FLOAT,
pickup_lng FLOAT,

-- 送达地点坐标
dropoff_lat FLOAT,
dropoff_lng FLOAT
```

## 🛠️ 核心组件说明

### MapSelector.vue

基于[高德地图JS API 2.0官方文档](https://lbs.amap.com/api/javascript-api-v2/tutorails/display-a-map)实现的地图选择器组件：

```vue
<MapSelector
  :api-key="amapApiKey"
  :default-location="existingLocation"
  @confirm="handleLocationSelect"
  @cancel="closeModal"
/>
```

**技术实现特点：**
- ✅ 使用 `@amap/amap-jsapi-loader` 异步加载JS API
- ✅ 地图初始化参数完全符合官方最佳实践
- ✅ 支持 `viewMode: '2D'` 平面模式显示
- ✅ 正确的事件监听和资源清理
- ✅ 官方推荐的地理定位配置

**Props:**
- `apiKey`: 高德地图API密钥
- `defaultLocation`: 默认选中的位置（可选）

**Events:**
- `confirm`: 用户确认选择位置时触发
- `cancel`: 用户取消选择时触发

### map.ts 工具类

提供地图相关的基础功能：

```typescript
import { geocode, reverseGeocode, getCurrentLocation } from '@/utils/map'

// 地址转坐标
const coords = await geocode('北京市朝阳区')

// 坐标转地址
const address = await reverseGeocode(116.3974, 39.9093)

// 获取当前位置
const currentPos = await getCurrentLocation()
```

## 🔧 自定义配置

### 修改地图样式

在 `MapSelector.vue` 中修改地图配置：

```javascript
map = new AMap.Map(mapContainer.value, {
  zoom: 15,
  center: [116.3974, 39.9093], // 默认中心点
  mapStyle: 'amap://styles/normal' // 地图样式
})
```

### 添加更多地图控件

```javascript
// 添加缩放控件
map.addControl(new AMap.Scale())
map.addControl(new AMap.ToolBar())
```

## 🐛 常见问题

### 1. 地图不显示

**原因：** API密钥未配置或无效
**解决：**
- 检查 `.env` 文件中的 `VITE_AMAP_API_KEY`
- 确认密钥在高德地图控制台中有效
- 检查网络是否能访问高德地图服务

### 2. 搜索无结果

**原因：** 搜索关键词不准确或网络问题
**解决：**
- 使用更具体的地点名称
- 检查网络连接
- 确认API密钥权限包含"地点搜索"功能

### 3. 定位失败

**原因：** 浏览器权限或网络问题
**解决：**
- 允许浏览器定位权限
- 在HTTPS环境下使用定位功能
- 检查网络连接

## 📚 更多资源

- [高德地图JS API文档](https://lbs.amap.com/api/javascript-api/guide/abc/prepare)
- [高德地图开发者控制台](https://lbs.amap.com/dev/key/app)
- [Vue 3 + 高德地图集成示例](https://lbs.amap.com/api/javascript-api/example/map-lifecycle/map-show)

## 🔄 后续扩展

基于当前架构，可以轻松扩展以下功能：

- 📏 距离计算和路线规划
- 🚗 实时位置跟踪
- 🔔 地理围栏提醒
- 📊 热力图展示
- 🗺️ 离线地图支持

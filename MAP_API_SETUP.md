# 高德地图API配置指南

## 概述

本项目集成了高德地图API，包括：

- **前端**：Web端JS API，用于地图显示、选址、搜索等功能
- **后端**：Web服务API，用于地理编码、距离计算等功能

## API Key类型说明

根据高德地图官方文档，不同功能需要使用不同类型的API Key：

### Web端(JS API) Key
- **用途**：前端地图显示、选址、搜索等交互功能
- **绑定服务**：JavaScript API
- **配置位置**：前端环境变量 `VITE_AMAP_API_KEY`

### Web服务API Key
- **用途**：后端地理编码、距离计算、路径规划等服务
- **绑定服务**：Web服务API
- **配置位置**：后端环境变量 `AMAP_WEB_SERVICE_KEY`

## 配置步骤

### 1. 申请API Key

1. 访问 [高德地图开放平台](https://lbs.amap.com/dev/key/app)
2. 注册/登录账号
3. 创建新应用

#### 创建Web端应用
- 应用名称：顺路带校园互助平台
- 应用类型：Web端(JS API)
- 绑定服务：选择"JavaScript API"

#### 创建Web服务应用
- 应用名称：顺路带校园互助平台
- 应用类型：Web服务
- 绑定服务：选择需要的服务（如地理编码、路径规划等）

### 2. 前端配置

编辑 `frontend/.env` 文件：

```bash
# 高德地图API配置
VITE_AMAP_API_KEY="your_web_js_api_key_here"
```

### 3. 后端配置

编辑 `backend/.env` 文件：

```bash
# 高德地图Web服务API
AMAP_WEB_SERVICE_KEY="your_web_service_api_key_here"
```

## 功能说明

### 前端功能
- 地图显示与交互
- 地点搜索与定位
- 精确选址功能
- 当前位置获取

### 后端功能
- 地理编码：地址 → 经纬度
- 逆地理编码：经纬度 → 地址
- 距离计算：两点间距离和时间
- 路径规划（未来扩展）

## 使用示例

### 前端使用
```typescript
// 在组件中使用
<MapSelector 
  :api-key="amapApiKey" 
  @confirm="onLocationSelected"
/>
```

### 后端使用
```python
from app.utils.map_service import amap_service

# 地理编码
result = await amap_service.geocode("北京市朝阳区")

# 距离计算
origins = [(116.1, 39.1)]
destinations = [(116.2, 39.2)]
distances = await amap_service.get_distance(origins, destinations)
```

## 注意事项

1. **域名绑定**：Web端JS API需要绑定域名，开发时可绑定 `localhost`
2. **安全设置**：建议设置HTTP Referer白名单以增强安全性
3. **配额管理**：注意API调用次数限制，避免超出免费额度
4. **错误处理**：当API Key配置错误时，系统会使用模拟数据保证基本功能

## 常见问题

### 1. 地图无法显示
- 检查 `VITE_AMAP_API_KEY` 是否正确配置
- 确认API Key已绑定JavaScript API服务
- 检查域名是否在白名单中

### 2. 后端API调用失败
- 检查 `AMAP_WEB_SERVICE_KEY` 是否正确配置
- 确认API Key已绑定Web服务API
- 检查网络连接是否正常

### 3. 地理编码精度不够
- 尝试提供更详细的地址信息
- 检查API Key是否有地理编码服务权限

### 4. 地点搜索失败 (INVALID_USER_SCODE)
- 登录高德地图开放平台控制台
- 进入应用管理 -> 我的应用
- 选择对应的Web端(JS API)应用
- 点击"设置" -> "服务管理"
- 确保开通了以下服务：
  - 地理编码API
  - 逆地理编码API
  - 地点搜索服务
  - 路径规划服务
- 保存设置后等待5-10分钟生效

### 5. 前端地理编码失败，后端服务作为备用
- 本项目已实现前后端结合的地理编码方案
- 当前端JS API无法完成地理编码时，会自动调用后端API
- 请确保后端 `AMAP_WEB_SERVICE_KEY` 配置正确且已开通相应服务
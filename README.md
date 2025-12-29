## 顺路带 · 校园即时互助平台

基于 **Vue 3 + TypeScript + Vite (H5)** 与 **FastAPI + SQLAlchemy** 实现的校园"顺路带"互助平台，覆盖注册登录、任务发布/接单/状态流转、信用评分、任务管理等核心功能。

### 技术栈

**前端**
- Vue 3 + TypeScript + Vite
- Pinia（状态管理）
- Vue Router（路由）
- Naive UI（UI组件库）
- Axios（HTTP客户端）
- 高德地图SDK（地图显示、选址、搜索）

**后端**
- FastAPI（异步Web框架）
- SQLAlchemy（异步ORM）
- SQLite / MySQL（数据库，开发环境默认SQLite）
- JWT（身份认证）
- Redis（可选，已包含依赖）
- 高德地图Web服务API（距离计算、地理编码等）

### 项目结构

```
deliverapp/
├── frontend/          # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── api/       # API接口封装
│   │   ├── components/ # 组件（包含MapSelector地图组件）
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # Pinia状态管理
│   │   ├── utils/     # 工具函数（包含地图工具类）
│   │   └── views/     # 页面视图
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── core/      # 核心配置
│   │   ├── db/        # 数据库配置
│   │   ├── models/    # 数据模型（已包含经纬度字段）
│   │   ├── schemas/   # Pydantic模式
│   │   └── services/  # 业务逻辑服务
│   └── requirements.txt
├── start-app.bat      # 一键启动前后端
├── start-backend.bat  # 仅启动后端
└── start-frontend.bat # 仅启动前端
```

### 核心功能

- ✅ 用户注册/登录（JWT认证）
- ✅ 任务发布（支持分类、紧急程度、地点、酬金等）
- ✅ 任务大厅（多条件筛选：关键字、状态、酬金、地点、时间范围、分类、紧急程度）
- ✅ 任务接单/取消
- ✅ 任务状态流转（pending → accepted → picked → delivering → confirming → completed）
- ✅ 任务详情查看
- ✅ 用户个人中心（信息查看/编辑）
- ✅ 任务管理（我的任务、任务历史）
- ✅ 信用评分系统（自动计算和更新）
- ✅ 定时任务清理（自动取消过期任务）
- ✅ 开发模式支持（简化登录流程）
- ✅ **地图SDK集成（高德地图）**：精确选址、地址搜索、地理编码、当前位置获取

### 快速启动

#### 方式一：一键启动（推荐）

Windows 系统可直接运行：

```bash
start-app.bat
```

该脚本会自动：
1. 创建并激活Python虚拟环境
2. 安装后端依赖
3. 启动后端服务（端口 9800）
4. 安装前端依赖
5. 启动前端服务（端口 5173）

#### 方式二：分别启动

**前端启动**

```bash
cd frontend
npm install  # 安装依赖，包括新添加的高德地图SDK
npm run dev
```

前端默认运行在 `http://localhost:5173`，开发服务器已配置代理，API请求会自动转发到后端。

**后端启动**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set SECRET_KEY=change-me
set DATABASE_URL=sqlite+aiosqlite:///./test.db
set DEVELOPMENT_MODE=true
uvicorn app.main:app --reload --host 127.0.0.1 --port 9800
```

**数据库配置**

- **开发环境（默认）**：使用 SQLite，数据库文件为 `backend/test.db`
- **生产环境**：使用 MySQL，设置环境变量：
  ```bash
  set DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/deliverapp
  ```

### API 接口

**认证相关**
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录（返回JWT Token）

**任务相关**
- `GET /api/tasks` - 获取任务列表（支持多条件筛选和排序）
  - 查询参数：`keyword`, `status`, `min_reward`, `max_reward`, `pickup_location`, `dropoff_location`, `time_range`, `category`, `urgency`, `sort_by`, `sort_order`
- `GET /api/tasks/{id}` - 获取任务详情
- `POST /api/tasks` - 发布任务（需认证）
- `POST /api/tasks/{id}/accept` - 接取任务（需认证）
- `POST /api/tasks/{id}/cancel` - 取消任务（需认证）
- `POST /api/tasks/{id}/status` - 更新任务状态（需认证）

**用户相关**
- `GET /api/users/me` - 获取当前用户信息（需认证）
- `PUT /api/users/me` - 更新当前用户信息（需认证）

**系统相关**
- `GET /healthz` - 健康检查

### 前端页面

- `/` - 任务大厅
- `/tasks/create` - 发布任务
- `/tasks/:id` - 任务详情
- `/tasks/:id/status` - 任务状态管理
- `/management/tasks` - 任务管理
- `/management/history` - 任务历史
- `/management/users` - 用户管理
- `/login` - 登录
- `/register` - 注册
- `/forgot-password` - 忘记密码
- `/profile` - 个人中心

### 开发模式

设置环境变量 `DEVELOPMENT_MODE=true` 后：
- 登录时如果用户不存在会自动创建测试用户
- 登录时跳过密码验证（方便开发测试）

### 任务状态流转

```
pending（待接单）
  ↓
accepted（已接单）
  ↓
picked（已取件）
  ↓
delivering（配送中）
  ↓
confirming（确认中）
  ↓
completed（已完成）
```

任务可在 `pending`、`accepted`、`picked`、`delivering`、`confirming` 状态下取消，变为 `cancelled`。

### 环境变量

**后端**
- `SECRET_KEY` - JWT密钥（必填）
- `DATABASE_URL` - 数据库连接URL（可选，默认SQLite）
- `DEVELOPMENT_MODE` - 开发模式开关（可选，默认false）
- `CORS_ORIGINS` - CORS允许的源（可选，默认 `http://localhost:5173`）
- `AMAP_WEB_SERVICE_KEY` - 高德地图Web服务API密钥（可选，用于距离计算、地理编码等）

**前端**
- `VITE_AMAP_API_KEY` - 高德地图API密钥（必填，用于地图功能）
- `VITE_API_PROXY` - API代理目标地址（可选，默认 `http://localhost:9800`）

### 地图功能说明

项目已集成高德地图SDK，提供以下功能：

**地图选址**
- 在发布任务时点击"地图选址"按钮打开地图选择器
- 支持点击地图直接选择位置
- 支持搜索地点名称进行快速定位
- 支持获取当前位置作为默认选择

**技术实现**
- 前端使用 `@amap/amap-jsapi-loader` 动态加载高德地图JS API
- 封装了 `MapSelector` 组件提供统一接口
- 提供 `map.ts` 工具类封装地图相关功能
- 后端数据模型已包含经纬度字段（`pickup_lat/lng`, `dropoff_lat/lng`）

**配置要求**
1. 前往 [高德地图开放平台](https://lbs.amap.com/dev/key/app) 申请API密钥
2. 设置环境变量：`VITE_AMAP_API_KEY=your_api_key`
3. 确保网络可访问高德地图服务

### 后续扩展

可在此基础上接入：
- 即时通讯（WebSocket）
- 支付网关（微信支付/支付宝）
- 路线规划和距离计算优化
- 校方认证系统
- 消息推送
- 文件上传（OSS）

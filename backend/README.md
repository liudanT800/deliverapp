## 顺路带后端（FastAPI + MySQL）

### 快速开始

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set SECRET_KEY=your-secret
set DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/deliverapp
uvicorn app.main:app --reload
```

- 默认 API 前缀 `http://localhost:9800/api`
- 依赖 MySQL 8，若未准备数据库，可暂时使用 `sqlite+aiosqlite:///./deliverapp.db`

### 目录说明

- `app/core` 配置、加密
- `app/models` ORM 模型
- `app/schemas` Pydantic 模型
- `app/api/routes` 业务接口
- `app/services` 领域服务逻辑

### 首次初始化

```sql
CREATE DATABASE deliverapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deliverapp'@'%' IDENTIFIED BY 'deliverapp';
GRANT ALL ON deliverapp.* TO 'deliverapp'@'%';
```

首次运行会自动创建数据表。生产环境请使用 Alembic 做迁移。*** End Patch


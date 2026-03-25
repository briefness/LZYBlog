# Python 全栈实战（十八）—— FastAPI（三）：部署与生产化

开发环境跑通了不代表能上线。生产部署要解决多 Worker 并发、Docker 容器化、日志收集、限流和 CORS，这些基础设施是 API 稳定运行的前提。

> **环境：** Python 3.14.3, Uvicorn 0.34+, Docker

---

## 1. Uvicorn 生产配置

开发用 `--reload`，生产用 Gunicorn + Uvicorn Workers：

```bash
# 开发环境
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境：Gunicorn 管理多个 Uvicorn Worker
uv run gunicorn main:app \
  -w 4 \                          # Worker 数 = CPU 核数 × 2 + 1
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

Worker 数的经验公式：`CPU 核数 × 2 + 1`。4 核 CPU 用 9 个 Worker。每个 Worker 是独立进程，崩溃不影响其他 Worker。

### 生产部署架构

```mermaid
flowchart LR
    Client["📱 客户端"] --> Nginx["Nginx\n反向代理"]
    Nginx --> G["Gunicorn\n进程管理器"]
    G --> W1["Uvicorn Worker 1"]
    G --> W2["Uvicorn Worker 2"]
    G --> W3["Uvicorn Worker 3"]
    G --> W4["Uvicorn Worker 4"]
    W1 --> DB[("PostgreSQL")]
    W2 --> DB
    W3 --> Redis[("Redis 缓存")]
    W4 --> DB

    style G fill:#fff3cd,stroke:#ffc107
    style DB fill:#d4edda,stroke:#28a745
    style Redis fill:#d4edda,stroke:#28a745
```

## 2. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.14-slim AS base

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev       # 只安装生产依赖

# 再复制源码
COPY src/ src/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "my_api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/myapp
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:17
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      retries: 5

volumes:
  pgdata:
```

```bash
docker compose up -d
docker compose logs -f api
```

### 多阶段构建优化

```dockerfile
# 生产优化版 Dockerfile
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ src/
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "my_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

多阶段构建让最终镜像不包含 uv 和构建工具，体积缩小 40-60%。

## 3. 环境变量与配置管理

```python
# src/my_api/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，自动从环境变量和 .env 文件读取"""
    database_url: str = "sqlite+aiosqlite:///./app.db"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
```

```bash
# .env（不提交到 Git）
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/myapp
SECRET_KEY=super-secret-random-key-here
```

```bash
# .env.example（提交到 Git，说明需要什么配置）
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=change-me
```

`pydantic-settings` 自动读取环境变量和 `.env` 文件，类型错误在启动时就报错——不用等到运行时才发现配置写错了。

## 4. CORS 跨域

```python
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 5. 速率限制

```bash
uv add slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("10/minute")              # 每分钟最多 10 次
async def get_data(request: Request):
    return {"data": "sensitive"}
```

## 6. 结构化日志

```python
import logging
import sys

def setup_logging(debug: bool = False) -> None:
    """配置结构化日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

# 在 main.py 中调用
from .config import settings
setup_logging(settings.debug)

logger = logging.getLogger(__name__)
logger.info("API 启动", extra={"port": 8000})
```

生产环境推荐用 `structlog` 或 JSON 格式日志，方便 ELK / Loki 等日志平台收集和查询。

## 7. 健康检查

```python
@app.get("/health", tags=["运维"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查接口，供 Docker/K8s 探测"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(exc)},
        )
```

Docker Compose 和 Kubernetes 的 liveness/readiness probe 都指向这个接口。数据库连不上时返回 503，编排系统会自动重启容器。

## 8. 启动与关闭事件

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("应用启动，初始化连接池")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时
    logger.info("应用关闭，释放资源")
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

`lifespan` 是 FastAPI 推荐的生命周期管理方式（替代了旧的 `@app.on_event`），跟上下文管理器的思路一致。

## 常见坑点

**1. 生产环境不要用 SQLite**

SQLite 不支持并发写入。多个 Worker 同时写入会触发锁冲突。生产环境用 PostgreSQL：

```bash
uv add asyncpg           # PostgreSQL 异步驱动
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

**2. SECRET_KEY 必须随机且保密**

```python
# 生成密钥
import secrets
print(secrets.token_hex(32))
# a1b2c3...（64 字符的随机十六进制字符串）
```

泄露 SECRET_KEY 意味着攻击者可以伪造任意 JWT Token。

## 总结

- Gunicorn + Uvicorn Worker 实现多进程生产部署
- Docker 多阶段构建缩小镜像体积
- `pydantic-settings` 从环境变量和 `.env` 读取配置，启动时校验
- CORS、速率限制、健康检查是生产 API 的基础设施
- `lifespan` 管理应用启动/关闭的资源初始化和清理

下一篇进入**内存模型与性能调优**——引用计数、分代 GC、火焰图分析。

## 参考

- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [FastAPI Docker 部署](https://fastapi.tiangolo.com/deployment/docker/)
- [pydantic-settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

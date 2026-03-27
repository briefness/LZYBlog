# Python 全栈实战：从语法到生产

有编程基础但没写过 Python？这个系列用最短路径带你跨过语法关，直达真实项目。基于 Python 3.14（2026 年最新稳定版），搭配 uv 现代工具链和 FastAPI Web 框架，21 篇文章覆盖从语法迁移到全栈项目交付的完整链路。

> **环境：** Python 3.14.3, uv 0.11+, Ruff 0.15+, FastAPI 0.135+

## 📚 目录导航

### 第一阶段：极速上手

- **[01. 环境搭建与现代工具链](./01_Environment_and_Toolchain.md)**
  - uv 0.11：一个工具替代 pip + venv + pyenv + pipx
  - Ruff 0.15：格式化 + Lint 二合一（替代 Black + Flake8）
  - Pyright：类型检查与 IDE 集成
  - 10 分钟写出第一个可运行的 Python 程序

- **[02. 语法速通：从其他语言迁移](./02_Syntax_Speedrun.md)**
  - 缩进即作用域、动态类型、一切皆对象
  - 推导式、解包、切片、f-string、海象运算符
  - Python 与 JavaScript/TypeScript 的关键差异对照

- **[03. 函数与装饰器](./03_Functions_and_Decorators.md)**
  - 一等公民函数、`*args` / `**kwargs`
  - 闭包原理与装饰器的本质（高阶函数）
  - `functools.wraps` 与参数化装饰器

### 第二阶段：Python 范式

- **[04. 数据结构深入](./04_Data_Structures.md)**
  - list / dict / set / tuple 的底层实现与性能特征
  - 推导式进阶与 `collections` 模块（`defaultdict`、`Counter`、`deque`）
  - 哈希表原理：为什么 dict 查找是 O(1)

- **[05. 面向对象：Python 风格](./05_OOP_Python_Style.md)**
  - class 基础、`dataclass` 与 `__slots__`
  - 魔术方法（`__repr__`、`__eq__`、`__hash__`）
  - 多继承与 MRO（C3 线性化算法）

- **[06. 类型系统与静态分析](./06_Type_System.md)**
  - Type Hints 全面指南：`Union`、`Optional`、泛型
  - `Protocol`：鸭子类型的形式化（PEP 544）
  - Pyright 实战配置与 `strict` 模式

- **[07. 错误处理与上下文管理器](./07_Error_Handling.md)**
  - Python 异常体系与自定义异常类
  - `with` 语句原理：`__enter__` / `__exit__` 协议
  - `contextlib` 工具箱与异常链（`raise ... from`）

- **[08. 文件 IO 与数据序列化](./08_File_IO_and_Serialization.md)** 📁
  - `pathlib`：现代路径操作（替代 `os.path`）
  - 文件读写模式、编码处理与大文件流式读取
  - JSON / CSV / TOML 序列化与反序列化实战

### 第三阶段：核心机制

- **[09. 迭代器与生成器](./09_Iterators_and_Generators.md)** 🔥
  - 迭代协议：`__iter__` / `__next__`
  - `yield` 与惰性求值、生成器管道
  - `itertools`：组合、过滤与无限序列

- **[10. 异步编程：asyncio](./10_Asyncio.md)** ⚡
  - async/await 语法与事件循环原理
  - 并发任务：`gather`、`TaskGroup`、信号量
  - 异步上下文管理器与异步生成器

- **[11. 多线程与多进程：GIL 真相](./11_Concurrency_and_GIL.md)**
  - GIL 原理：为什么 CPU 密集型任务用多线程没用
  - `threading` vs `multiprocessing` vs `concurrent.futures`
  - Free-threaded Python（PEP 779, `--disable-gil`）实战

### 第四阶段：工程化实践

- **[12. 项目结构与模块系统](./12_Project_Structure.md)** 📦
  - import 机制与 `__init__.py` 的真实作用
  - `pyproject.toml` 完全指南
  - uv 工作流：依赖管理、锁文件与发布

- **[13. 测试驱动开发：pytest](./13_Testing_with_Pytest.md)**
  - pytest 9.x 核心：fixture、参数化、标记
  - Mock 与依赖隔离（`unittest.mock`、`pytest-mock`）
  - 覆盖率报告与 CI 集成

- **[14. 网络请求与自动化脚本](./14_HTTP_and_Automation.md)** 🌐
  - httpx 0.28：同步/异步 HTTP 请求
  - 正则表达式（`re` 模块）与文本处理
  - 实战：网页数据抓取与自动化脚本模式

- **[15. CLI 工具开发实战](./15_CLI_Development.md)** 🛠️
  - Typer 0.24 + Rich 14：构建专业的命令行应用
  - 参数解析、子命令、进度条与表格输出
  - 用 `uv tool` 打包为全局可执行工具

### 第五阶段：FastAPI Web 开发

- **[16. FastAPI（一）：构建 REST API](./16_FastAPI_Basics.md)** 🚀
  - FastAPI 0.135 vs Flask vs Django：为什么选 FastAPI
  - 路由、请求体、Pydantic v2.12 验证
  - 依赖注入系统与自动 OpenAPI 文档

- **[17. FastAPI（二）：数据库与认证](./17_FastAPI_Database_Auth.md)**
  - SQLAlchemy 2.0.48 异步 ORM + Alembic 1.18 迁移
  - JWT 认证与权限控制
  - 关联查询、事务与 N+1 问题

- **[18. FastAPI（三）：部署与生产化](./18_FastAPI_Production.md)**
  - Uvicorn + Gunicorn 多 Worker 部署
  - Docker 多阶段构建与健康检查
  - 中间件、CORS、速率限制与结构化日志

### 第六阶段：进阶与实战

- **[19. 内存模型与性能调优](./19_Memory_and_Performance.md)** 📊
  - 引用计数 + 分代垃圾回收机制
  - 内存分析工具：`tracemalloc`、`objgraph`
  - 性能优化策略与基准测试（`timeit`、`cProfile`）

- **[20. Python 3.14 新特性与生态全景](./20_Python314_and_Ecosystem.md)**
  - 延迟求值注解（PEP 649）、模板字符串 t-string（PEP 750）
  - Free-threaded 模式深入（PEP 779）与多解释器（PEP 734）
  - 零开销调试接口（PEP 768）、Zstandard 压缩（PEP 784）
  - 元编程入门与 Python 生态导览

- **[21. 综合实战：API 聚合服务](./21_Capstone_Project.md)** 🏗️
  - 从零构建一个聚合多个第三方 API 的生产级服务
  - 技术栈串联：FastAPI + SQLAlchemy + httpx + Typer + pytest
  - 缓存策略、定时刷新、CLI 管理工具
  - Docker Compose 部署、CI/CD 流水线、完整项目结构

## 🔧 技术栈版本锁定（2026 年 3 月）

| 工具 / 框架 | 版本 | 用途 |
|------------|------|------|
| Python | 3.14.3 | 运行时 |
| uv | 0.11+ | 包管理 + 虚拟环境 + Python 版本管理 |
| Ruff | 0.15.7 | 格式化 + Linting（替代 Black + Flake8） |
| Pyright | latest | 类型检查 |
| pytest | 9.0.2 | 测试框架 |
| FastAPI | 0.135.2 | Web 框架 |
| Pydantic | 2.12.5 | 数据验证 |
| SQLAlchemy | 2.0.48 | ORM |
| Alembic | 1.18.4 | 数据库迁移 |
| httpx | 0.28.1 | HTTP 客户端 |
| Typer | 0.24.1 | CLI 框架 |
| Rich | 14.3.3 | 终端美化 |

## 🌟 系列特色

- **跨语言视角**：有编程基础的读者不需要从零学循环和变量，直接聚焦 Python 特有的范式与陷阱
- **现代工具链**：全程使用 uv（替代 pip/venv/pyenv）、Ruff（替代 Black/Flake8）、Pyright（类型检查）
- **Mermaid 图解 + CSS 动画组件**：GIL、事件循环、内存管理等复杂原理用流程图和交互动画可视化
- **FastAPI 全栈**：三篇完整覆盖从 API 开发到生产部署
- **版本锁定**：所有依赖版本精确到 2026 年 3 月最新稳定版，确保代码可复现
- **综合实战收官**：第 21 篇把前 20 篇的知识全部串联成一个生产级项目
- **共 21 篇**：从语法迁移到生产部署的完整路径

---

> 系列持续更新中。

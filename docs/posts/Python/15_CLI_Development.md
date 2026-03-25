# Python 全栈实战（十五）—— CLI 工具开发实战

命令行工具是 Python 的传统强项。Typer + Rich 这套组合让你用极少的代码写出带自动补全、参数校验、彩色输出的专业 CLI。

> **环境：** Python 3.14.3, Typer 0.24.1, Rich 14.3.3

---

## 1. 为什么用 Typer

Python 标准库的 `argparse` 能写 CLI，但代码又臭又长。`click` 改善了体验，但仍需手写装饰器参数。Typer 直接利用 Type Hints 推断参数类型——函数签名就是 CLI 接口。

```bash
uv add typer rich
```

```python
# cli.py
import typer

app = typer.Typer()

@app.command()
def greet(name: str, count: int = 1):
    """向指定的人打招呼"""
    for _ in range(count):
        print(f"你好，{name}！")

if __name__ == "__main__":
    app()
```

```bash
uv run python cli.py --help
# Usage: cli.py [OPTIONS] NAME
#
#   向指定的人打招呼
#
# Arguments:
#   NAME  [required]
#
# Options:
#   --count INTEGER  [default: 1]
#   --help           Show this message and exit.

uv run python cli.py 张三 --count 3
# 你好，张三！
# 你好，张三！
# 你好，张三！
```

Type Hints `name: str` 变成了必填参数，`count: int = 1` 变成了带默认值的 `--count` 选项。帮助文档、类型校验全部自动生成。

## 2. 参数与选项

```python
import typer
from pathlib import Path
from typing import Optional
from enum import Enum

app = typer.Typer(help="文件处理工具")


class OutputFormat(str, Enum):
    json = "json"
    csv = "csv"
    table = "table"


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="输入文件路径", exists=True),
    output_dir: Path = typer.Option("./output", "--output", "-o", help="输出目录"),
    format: OutputFormat = typer.Option(OutputFormat.json, "--format", "-f"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="最大处理行数"),
):
    """转换文件格式"""
    if verbose:
        print(f"输入：{input_file}")
        print(f"输出：{output_dir}")
        print(f"格式：{format.value}")

    output_dir.mkdir(parents=True, exist_ok=True)
    # ... 转换逻辑
    print(f"✅ 转换完成 → {output_dir}")
```

```bash
uv run python cli.py convert data.json -o ./result -f csv -v
# 输入：data.json
# 输出：./result
# 格式：csv
# ✅ 转换完成 → ./result
```

- `typer.Argument`：位置参数，`exists=True` 自动校验文件是否存在
- `typer.Option`：命名选项，支持短选项 `-o`、`-f`
- `Enum` 类型自动限制可选值，输入错误时 Typer 报错并提示有效选项

## 3. 子命令

```python
import typer

app = typer.Typer(help="项目管理 CLI")
db_app = typer.Typer(help="数据库管理")
app.add_typer(db_app, name="db")

@app.command()
def init(name: str):
    """初始化新项目"""
    print(f"创建项目：{name}")

@db_app.command()
def migrate():
    """运行数据库迁移"""
    print("执行迁移...")

@db_app.command()
def seed(count: int = 100):
    """填充测试数据"""
    print(f"插入 {count} 条测试数据")
```

```bash
uv run python cli.py --help       # 显示顶级命令
uv run python cli.py init my-app  # 初始化项目
uv run python cli.py db migrate   # 数据库迁移
uv run python cli.py db seed --count 500
```

## 4. Rich：终端美化

Rich 把终端变成画布——表格、进度条、Markdown 渲染、语法高亮，全部支持。

### 表格输出

```python
from rich.console import Console
from rich.table import Table

console = Console()

def show_deps():
    """展示项目依赖"""
    table = Table(title="项目依赖", show_header=True, header_style="bold cyan")
    table.add_column("包名", style="green")
    table.add_column("版本", justify="center")
    table.add_column("用途")

    table.add_row("fastapi", "0.135.2", "Web 框架")
    table.add_row("httpx", "0.28.1", "HTTP 客户端")
    table.add_row("sqlalchemy", "2.0.48", "ORM")
    table.add_row("pydantic", "2.12.5", "数据验证")

    console.print(table)
```

### 进度条

```python
import time
from rich.progress import Progress, SpinnerColumn, TextColumn

def process_files(files: list[str]):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("处理文件...", total=len(files))
        for file in files:
            time.sleep(0.3)    # 模拟处理
            progress.update(task, advance=1, description=f"处理 {file}")

    console.print("[bold green]✅ 全部完成！[/]")
```

### 日志与状态

```python
from rich.console import Console

console = Console()

console.print("[bold red]错误：[/] 文件不存在")
console.print("[yellow]警告：[/] 配置项缺失，使用默认值")
console.print("[green]成功：[/] 部署完成")

# 面板
from rich.panel import Panel
console.print(Panel("🚀 部署成功\n版本: v2.1.0\n环境: production", title="状态"))
```

## 5. 完整 CLI 工具示例

把 Typer 和 Rich 结合，构建一个实用的项目脚手架工具：

```python
# scaffold.py
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="🐍 Python 项目脚手架工具")
console = Console()


@app.command()
def new(
    name: str = typer.Argument(..., help="项目名称"),
    with_fastapi: bool = typer.Option(False, "--fastapi", help="包含 FastAPI 模板"),
    with_docker: bool = typer.Option(False, "--docker", help="生成 Dockerfile"),
):
    """创建新的 Python 项目"""
    project_dir = Path(name)

    if project_dir.exists():
        console.print(f"[red]错误：目录 {name} 已存在[/]")
        raise typer.Exit(code=1)

    # 创建目录结构
    dirs = [
        project_dir / "src" / name.replace("-", "_"),
        project_dir / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True)
        (d / "__init__.py").touch()

    # 创建 pyproject.toml
    pyproject = project_dir / "pyproject.toml"
    deps = '    "httpx>=0.28.1",\n'
    if with_fastapi:
        deps += '    "fastapi>=0.135.2",\n    "uvicorn[standard]>=0.34.0",\n'

    pyproject.write_text(f"""[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
{deps}]

[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "ruff>=0.15.7",
]
""", encoding="utf-8")

    # 创建 .python-version
    (project_dir / ".python-version").write_text("3.14\n")

    # 创建 .gitignore
    (project_dir / ".gitignore").write_text(".venv/\n__pycache__/\n*.pyc\n")

    if with_docker:
        dockerfile = project_dir / "Dockerfile"
        dockerfile.write_text("""FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "python", "-m", "{pkg}"]
""".format(pkg=name.replace("-", "_")))

    # 结果展示
    tree_lines = [f"📁 {name}/"]
    for p in sorted(project_dir.rglob("*")):
        depth = len(p.relative_to(project_dir).parts)
        icon = "📁" if p.is_dir() else "📄"
        tree_lines.append(f"{'  ' * depth}{icon} {p.name}")

    console.print(Panel(
        "\n".join(tree_lines),
        title=f"[bold green]✅ 项目 {name} 创建成功[/]",
    ))
    console.print(f"\n下一步：\n  cd {name}\n  uv sync\n  uv run pytest")


if __name__ == "__main__":
    app()
```

```bash
uv run python scaffold.py new my-app --fastapi --docker
```

## 6. 打包为全局工具

把 CLI 工具打包后，可以在任何地方直接调用：

```toml
# pyproject.toml 中添加入口点
[project.scripts]
scaffold = "scaffold:app"
```

```bash
# 安装为全局工具
uv tool install .

# 现在可以直接在终端调用
scaffold new awesome-project --fastapi
```

`uv tool install` 类似 `npm install -g`——把 CLI 安装到全局路径，之后无需 `uv run` 前缀。

## 常见坑点

**1. Typer 的 Annotated 语法**

Typer 0.9+ 推荐用 `Annotated` 替代 `typer.Argument()` / `typer.Option()` 作为默认值：

```python
from typing import Annotated

@app.command()
def greet(
    name: Annotated[str, typer.Argument(help="用户名")],
    count: Annotated[int, typer.Option("--count", "-c")] = 1,
):
    ...
```

两种写法功能一致，但 `Annotated` 更符合 Python 类型注解的标准用法，Pyright 的类型推断也更准确。

**2. Windows 终端颜色**

Windows CMD 默认不支持 ANSI 颜色码。Rich 会自动检测终端能力并降级，但在老版 CMD 上可能显示乱码。推荐用 Windows Terminal 或 PowerShell 7+。

## 总结

- Typer 通过 Type Hints 自动生成 CLI 接口，函数签名即命令定义
- 位置参数用 `typer.Argument`，命名选项用 `typer.Option`，Enum 限制可选值
- 子命令通过 `add_typer` 组织多级命令结构
- Rich 提供表格、进度条、面板等终端美化能力
- `uv tool install` 把 CLI 打包为全局可执行工具

下一篇进入 **FastAPI（一）：构建 REST API**——路由、Pydantic 验证、依赖注入。

## 参考

- [Typer 官方文档](https://typer.tiangolo.com/)
- [Rich 官方文档](https://rich.readthedocs.io/)
- [uv tool 文档](https://docs.astral.sh/uv/concepts/tools/)

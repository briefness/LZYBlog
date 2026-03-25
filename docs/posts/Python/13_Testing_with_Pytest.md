# Python 全栈实战（十三）—— 测试驱动开发：pytest

代码没有测试就等于没有文档。pytest 是 Python 生态的测试标准——语法简洁、插件丰富、fixture 机制强大。

> **环境：** Python 3.14.3, pytest 9.0.2

---

## 1. 快速上手

```bash
uv add --dev pytest
```

```python
# tests/test_math.py
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -2) == -3

def test_add_zero():
    assert add(0, 0) == 0
```

```bash
uv run pytest
# ========================= test session starts ==========================
# tests/test_math.py ...                                           [100%]
# ========================= 3 passed in 0.01s ===========================
```

pytest 自动发现 `test_` 开头的文件和函数。不需要继承类、不需要 `self.assertEqual`——一个 `assert` 搞定，失败时 pytest 会自动展示详细的差异信息。

## 2. 断言与错误信息

pytest 重写了 `assert` 语句，失败时自动展示中间值：

```python
def test_string_contains():
    greeting = "Hello, Python"
    assert "Java" in greeting
    # AssertionError: assert 'Java' in 'Hello, Python'
```

### 检测异常

```python
import pytest

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError, match="除数不能为 0"):
        divide(10, 0)

def test_divide_normal():
    assert divide(10, 2) == 5.0
```

### 近似比较（浮点数）

```python
def test_float_precision():
    assert 0.1 + 0.2 == pytest.approx(0.3)          # ✅
    assert 3.14159 == pytest.approx(3.14, abs=0.01)  # ✅ 允许 0.01 误差
```

## 3. Fixture：依赖注入

fixture 是 pytest 的核心特色——用函数定义可复用的测试依赖，pytest 自动注入：

```python
# tests/conftest.py（全局共享 fixture）
import pytest

@pytest.fixture
def sample_user() -> dict:
    return {"name": "张三", "age": 25, "email": "z@test.com"}

@pytest.fixture
def sample_users() -> list[dict]:
    return [
        {"name": "张三", "age": 25},
        {"name": "李四", "age": 30},
        {"name": "王五", "age": 28},
    ]
```

```python
# tests/test_user.py
def test_user_name(sample_user):           # pytest 自动注入 sample_user
    assert sample_user["name"] == "张三"

def test_users_count(sample_users):
    assert len(sample_users) == 3
```

### fixture 的作用域

```python
@pytest.fixture(scope="function")    # 默认：每个测试函数重新创建
def db_connection(): ...

@pytest.fixture(scope="module")      # 每个测试文件共享一个
def db_connection(): ...

@pytest.fixture(scope="session")     # 整个测试会话共享一个
def db_connection(): ...
```

### fixture 的 teardown

```python
@pytest.fixture
def temp_database():
    """创建临时数据库，测试后清理"""
    db = create_test_database()
    yield db                          # yield 之前 = setup，之后 = teardown
    db.drop_all()
    db.close()
```

`yield` 机制跟上下文管理器一样——yield 之前是 setup，yield 之后是 teardown，无论测试成功还是失败都会执行。

## 4. 参数化

一组测试逻辑，多组输入输出：

```python
import pytest

def is_palindrome(s: str) -> bool:
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

@pytest.mark.parametrize("input_str, expected", [
    ("racecar", True),
    ("hello", False),
    ("A man a plan a canal Panama", True),
    ("", True),
    ("ab", False),
])
def test_is_palindrome(input_str: str, expected: bool):
    assert is_palindrome(input_str) == expected
```

```bash
uv run pytest -v
# test_palindrome.py::test_is_palindrome[racecar-True]         PASSED
# test_palindrome.py::test_is_palindrome[hello-False]           PASSED
# test_palindrome.py::test_is_palindrome[A man a plan...-True]  PASSED
# test_palindrome.py::test_is_palindrome[-True]                 PASSED
# test_palindrome.py::test_is_palindrome[ab-False]              PASSED
```

5 组数据生成 5 个独立的测试用例，其中任何一个失败都能精确定位。

## 5. Mock：隔离外部依赖

测试不应该依赖真实的网络请求、数据库或文件系统。用 `unittest.mock` 替换外部依赖：

```python
# src/my_api/services/weather.py
import httpx

def get_temperature(city: str) -> float:
    """调用天气 API 获取温度"""
    response = httpx.get(f"https://api.weather.com/v1/{city}")
    response.raise_for_status()
    return response.json()["temperature"]
```

```python
# tests/test_weather.py
from unittest.mock import patch, MagicMock
from my_api.services.weather import get_temperature

def test_get_temperature():
    # 构造模拟响应
    mock_response = MagicMock()
    mock_response.json.return_value = {"temperature": 22.5}
    mock_response.raise_for_status = MagicMock()

    # 替换 httpx.get 为模拟对象
    with patch("my_api.services.weather.httpx.get", return_value=mock_response):
        temp = get_temperature("beijing")
        assert temp == 22.5

def test_get_temperature_error():
    with patch("my_api.services.weather.httpx.get") as mock_get:
        mock_get.side_effect = httpx.ConnectError("连接失败")
        with pytest.raises(httpx.ConnectError):
            get_temperature("beijing")
```

**`patch` 的路径原则**：patch 的是**使用**该对象的模块路径，不是**定义**该对象的路径。`weather.py` 里写了 `import httpx`，所以 patch `my_api.services.weather.httpx.get`。

### pytest-mock 简化写法

```bash
uv add --dev pytest-mock
```

```python
def test_get_temperature(mocker):
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"temperature": 22.5}

    mocker.patch(
        "my_api.services.weather.httpx.get",
        return_value=mock_response,
    )
    assert get_temperature("beijing") == 22.5
```

`mocker` 是 pytest-mock 提供的 fixture，比手动 `with patch(...)` 更简洁。

## 6. 标记（Markers）

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    """标记为慢速测试"""
    result = sum(range(100_000_000))
    assert result > 0

@pytest.mark.skipif(
    condition=sys.platform == "win32",
    reason="Windows 上不支持",
)
def test_unix_only():
    ...

@pytest.mark.xfail(reason="已知 Bug，等待修复")
def test_known_bug():
    assert 1 + 1 == 3
```

```bash
# 跳过慢速测试
uv run pytest -m "not slow"

# 只运行慢速测试
uv run pytest -m slow
```

在 `pyproject.toml` 中注册自定义标记：

```toml
[tool.pytest.ini_options]
markers = [
    "slow: 标记为慢速测试",
    "integration: 集成测试（需要外部服务）",
]
```

## 7. 覆盖率

```bash
uv add --dev pytest-cov
```

```bash
uv run pytest --cov=src/my_api --cov-report=term-missing
# Name                          Stmts   Miss  Cover   Missing
# -----------------------------------------------------------
# src/my_api/__init__.py            2      0   100%
# src/my_api/services/weather.py    8      1    88%   15
# -----------------------------------------------------------
# TOTAL                            10      1    90%
```

`Missing` 列显示未覆盖的行号——第 15 行没有被测试执行到。

在 CI 中设置最低覆盖率门槛：

```bash
uv run pytest --cov=src/my_api --cov-fail-under=80
```

覆盖率低于 80% 时命令返回非零退出码，CI 流水线会失败。

## 8. 测试组织最佳实践

```
tests/
├── conftest.py                    # 全局 fixtures
├── unit/                          # 单元测试（不依赖外部服务）
│   ├── test_models.py
│   └── test_utils.py
├── integration/                   # 集成测试（依赖数据库等）
│   └── test_api.py
└── fixtures/                      # 测试数据文件
    └── sample_response.json
```

```bash
# 只运行单元测试
uv run pytest tests/unit/

# 只运行集成测试
uv run pytest tests/integration/
```

## 常见坑点

**1. fixture 依赖的顺序**

fixture 可以依赖其他 fixture，pytest 自动解析依赖图。但如果 fixture A 依赖 fixture B，B 的 scope 不能比 A 更窄（如 A 是 `session`，B 不能是 `function`）。

**2. 测试之间的状态泄露**

```python
# ❌ 全局可变状态导致测试之间互相影响
registry = []

def test_add():
    registry.append("a")
    assert len(registry) == 1    # 单独运行 ✅，但执行顺序不同可能 ❌

# ✅ 用 fixture 隔离状态
@pytest.fixture
def fresh_registry():
    return []
```

## 总结

- pytest 用 `assert` 断言、自动发现测试函数，失败时展示详细差异
- fixture 是可复用的测试依赖，用 `yield` 实现 setup/teardown
- 参数化用 `@pytest.mark.parametrize`，一组逻辑 N 组数据
- Mock 隔离外部依赖，patch 路径指向**使用**该对象的模块
- `pytest-cov` 生成覆盖率报告，CI 中设置 `--cov-fail-under` 门槛

下一篇进入**网络请求与自动化脚本**——httpx 实战、正则表达式、网页数据抓取。

## 参考

- [pytest 官方文档](https://docs.pytest.org/en/stable/)
- [pytest-mock 文档](https://pytest-mock.readthedocs.io/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)

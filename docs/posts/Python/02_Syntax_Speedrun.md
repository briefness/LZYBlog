# Python 全栈实战（二）—— 语法速通：从其他语言迁移

已经会写 JavaScript 或 TypeScript？Python 的语法没什么魔法，但有几个地方跟你的直觉完全相反。这篇把关键差异一次理清。

> **环境：** Python 3.14.3

---

## 1. 缩进即作用域

Python 没有花括号 `{}`。代码块靠缩进（4 个空格）界定，缩进错一格就是语法错误。

```python
# Python
if score >= 60:
    grade = "及格"       # 缩进 4 格 = 属于 if 块
    print(grade)
else:
    grade = "不及格"
    print(grade)

print("判定结束")        # 回到顶层缩进 = 退出 if/else 块
```

对比 JavaScript：

```javascript
// JavaScript
if (score >= 60) {
    grade = "及格";      // 花括号界定作用域
    console.log(grade);
} else {
    grade = "不及格";
}
```

**注意**：Python 的 `if` 条件不需要括号，行尾用冒号 `:` 而不是花括号。混着写前几天会频繁忘记冒号——Ruff 会提醒。

## 2. 变量与类型

Python 是**强类型、动态类型**语言。变量不声明类型，但一旦赋值就有明确的类型，不会做隐式转换。

```python
name = "张三"          # str（不需要 let/const/var）
age = 25               # int
height = 1.75          # float
is_student = True      # bool（注意大写 T）

# 强类型：不会隐式转换
print("年龄：" + str(age))    # 必须显式转换
# print("年龄：" + age)       # ❌ TypeError: can only concatenate str to str
```

JavaScript 对比：`"年龄：" + 25` 会自动转成 `"年龄：25"`。Python 不干这事——类型不匹配直接报错。这算是优点，减少了隐式转换导致的诡异 Bug。

### 没有 const

Python 没有 `const` 关键字。社区约定用**全大写命名**表示常量：

```python
MAX_RETRIES = 3        # 约定：全大写 = 不要修改
API_BASE_URL = "https://api.example.com"

# 但语法上没有任何阻止你修改它
MAX_RETRIES = 5        # 不会报错，只是违反约定
```

如果需要运行时不可变，用 `Final` 类型注解（第 6 篇详解）：

```python
from typing import Final

MAX_RETRIES: Final = 3
# MAX_RETRIES = 5      # Pyright 会报类型错误
```

## 3. 字符串与 f-string

Python 的字符串操作比 JavaScript 更直观：

```python
name = "Python"
version = 3.14

# f-string（类似 JS 模板字面量 ${}，但用 f 前缀和 {} ）
greeting = f"Hello, {name} {version}!"

# 表达式求值
print(f"2 + 3 = {2 + 3}")          # 2 + 3 = 5
print(f"大写：{name.upper()}")      # 大写：PYTHON

# 格式化数字
price = 1234567.89
print(f"价格：{price:,.2f}")        # 价格：1,234,567.89
print(f"百分比：{0.856:.1%}")       # 百分比：85.6%

# 多行字符串（三引号）
sql = """
SELECT id, name
FROM users
WHERE age > 18
"""
```

### Python 3.14 新增：t-string（模板字符串）

Python 3.14 引入了 `t""` 模板字符串（PEP 750），类似 JavaScript 的 Tagged Template Literals：

```python
from string.templatelib import Template

name = "O'Malley"

# f-string 直接插值（有 SQL 注入风险）
query_bad = f"SELECT * FROM users WHERE name = '{name}'"
# SELECT * FROM users WHERE name = 'O'Malley'  ← 单引号破坏 SQL

# t-string 产生 Template 对象，而非字符串
template = t"SELECT * FROM users WHERE name = '{name}'"
# template 是一个 Template 对象，包含静态部分和插值部分
# 可以安全地处理转义、参数化查询等
print(type(template))  # <class 'string.templatelib.Template'>
```

t-string 的价值不在于替代 f-string，而是让框架和库拿到**结构化的模板数据**，在最终渲染前做安全处理（防注入、HTML 转义等）。日常打印用 f-string 就够了。

## 4. 数据容器一览

Python 的四种核心容器对应不同场景：

| 类型 | 语法 | 可变 | 有序 | 重复 | 对标 JS |
|------|------|------|------|------|---------|
| `list` | `[1, 2, 3]` | ✅ | ✅ | ✅ | `Array` |
| `tuple` | `(1, 2, 3)` | ❌ | ✅ | ✅ | `Object.freeze([...])` |
| `dict` | `{"a": 1}` | ✅ | ✅ | 键唯一 | `Object` / `Map` |
| `set` | `{1, 2, 3}` | ✅ | ❌ | ❌ | `Set` |

```python
# list：有序、可变
languages = ["Python", "JavaScript", "Rust"]
languages.append("Go")          # 追加
languages[0] = "CPython"        # 修改
print(languages[-1])            # "Go"（-1 = 倒数第一）

# tuple：有序、不可变（创建后不能增删改）
point = (3, 4)
x, y = point                   # 解包

# dict：键值对
user = {"name": "张三", "age": 25}
user["email"] = "z@test.com"    # 新增
print(user.get("phone", "无"))  # 安全取值，不存在返回默认值

# set：去重、无序
tags = {"python", "web", "python"}
print(tags)                     # {"python", "web"}（自动去重）
```

### 切片（Slicing）

JavaScript 有 `Array.prototype.slice()`，Python 的切片语法更强大：

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

numbers[2:5]      # [2, 3, 4]        从索引 2 到 5（不含 5）
numbers[:3]       # [0, 1, 2]        从开头到索引 3
numbers[7:]       # [7, 8, 9]        从索引 7 到末尾
numbers[-3:]      # [7, 8, 9]        倒数 3 个
numbers[::2]      # [0, 2, 4, 6, 8]  步长为 2（隔一个取一个）
numbers[::-1]     # [9, 8, ..., 0]   反转列表
```

切片语法 `[start:stop:step]` 在字符串上也能用：`"Hello"[::-1]` 得到 `"olleH"`。

## 5. 推导式（Comprehension）

推导式是 Python 最具特色的语法之一——用一行代码生成新的列表、字典或集合。

```python
# 列表推导式（List Comprehension）
squares = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带过滤条件
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# 字典推导式
word = "hello"
char_count = {ch: word.count(ch) for ch in set(word)}
# {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# 集合推导式
unique_lengths = {len(name) for name in ["Alice", "Bob", "Charlie", "Dan"]}
# {3, 5, 7}
```

对比 JavaScript 的 `.map().filter()` 链式调用：

```javascript
// JavaScript
const evenSquares = Array.from({length: 10}, (_, x) => x)
  .filter(x => x % 2 === 0)
  .map(x => x ** 2);
```

Python 推导式更短，可读性也更好（前提是不要嵌套太深——超过两层就应该改用 for 循环）。

## 6. 解包（Unpacking）

Python 的解包比 JavaScript 的解构更灵活：

```python
# 基础解包（类似 JS 的数组解构）
first, second, third = [1, 2, 3]

# 星号解包：捕获剩余元素（类似 JS 的 ...rest）
head, *tail = [1, 2, 3, 4, 5]
# head = 1, tail = [2, 3, 4, 5]

first, *middle, last = [1, 2, 3, 4, 5]
# first = 1, middle = [2, 3, 4], last = 5

# 交换变量（不需要临时变量）
a, b = 1, 2
a, b = b, a    # a = 2, b = 1

# 字典解包
defaults = {"timeout": 30, "retries": 3}
overrides = {"timeout": 10, "debug": True}
config = {**defaults, **overrides}
# {"timeout": 10, "retries": 3, "debug": True}（后者覆盖前者）
```

函数返回多个值时，解包特别好用：

```python
def get_user_stats(user_id: int) -> tuple[int, int, float]:
    """返回文章数、粉丝数、活跃度"""
    return 42, 1500, 0.85

posts, followers, activity = get_user_stats(1)
```

## 7. 控制流

### 条件语句

```python
# Python 用 elif，不是 else if
score = 85
if score >= 90:
    level = "A"
elif score >= 80:       # <--- elif，不是 else if
    level = "B"
elif score >= 60:
    level = "C"
else:
    level = "D"

# 三元表达式（跟 JS 的 ? : 不同）
status = "成年" if age >= 18 else "未成年"
# JavaScript 写法：const status = age >= 18 ? "成年" : "未成年"
```

### 循环

```python
# for 循环（Python 的 for 只有 for...in，没有 C 风格的 for(i=0;i<n;i++)）
for fruit in ["苹果", "香蕉", "橙子"]:
    print(fruit)

# 需要索引时用 enumerate（不要用 range(len(...))）
for index, fruit in enumerate(["苹果", "香蕉", "橙子"]):
    print(f"{index}: {fruit}")

# range 生成数字序列
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

# 遍历字典
user = {"name": "张三", "age": 25}
for key, value in user.items():
    print(f"{key}: {value}")

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1           # Python 没有 count++
```

**注意**：Python 没有 `++` 和 `--` 运算符，只能用 `+= 1` 和 `-= 1`。

### 模式匹配（match-case）

Python 3.10 引入的 `match-case`，功能比 JavaScript 的 `switch-case` 强大很多——支持解构、类型匹配、守卫条件：

```python
def handle_response(response: dict) -> str:
    match response:
        case {"status": 200, "data": data}:
            return f"成功：{data}"
        case {"status": 404}:
            return "资源不存在"
        case {"status": status} if status >= 500:     # 守卫条件
            return f"服务器错误：{status}"
        case _:                                       # 默认分支
            return "未知响应"

print(handle_response({"status": 200, "data": "hello"}))
# 成功：hello
print(handle_response({"status": 503}))
# 服务器错误：503
```

`case {"status": 200, "data": data}` 同时做了**结构匹配**和**变量绑定**——检查 dict 里有没有 `status=200`，如果有就把 `data` 字段绑定到变量 `data` 上。JavaScript 的 `switch` 做不到这一点。

## 8. 函数基础

```python
# 基本函数（def 关键字，不是 function）
def greet(name: str) -> str:
    return f"你好，{name}！"

# 默认参数
def connect(host: str, port: int = 8080, timeout: float = 30.0) -> None:
    print(f"连接 {host}:{port}，超时 {timeout}s")

connect("localhost")                    # 使用默认端口和超时
connect("localhost", port=3000)         # 关键字参数（可跳过中间参数）
connect("localhost", timeout=5.0)       # 只改超时

# lambda 表达式（匿名函数，只能写单行表达式）
square = lambda x: x ** 2
# 等价于：
# def square(x): return x ** 2

# 实际中 lambda 多用在 sorted、filter 这类高阶函数里
users = [{"name": "张三", "age": 30}, {"name": "李四", "age": 25}]
sorted_users = sorted(users, key=lambda u: u["age"])
```

### 关键字参数 vs 位置参数

Python 区分参数的传递方式。这个概念在 JavaScript 中不存在：

```python
def divide(a: float, b: float) -> float:
    return a / b

divide(10, 3)           # 位置参数：a=10, b=3
divide(b=3, a=10)       # 关键字参数：顺序无所谓
divide(10, b=3)         # 混合：位置参数必须在前
```

## 9. None、真值与比较

```python
# None（等价于 JS 的 null，Python 没有 undefined）
result = None

# 判空
if result is None:       # <--- 用 is，不用 ==
    print("无结果")

# Python 的假值（Falsy）
# False, None, 0, 0.0, "", [], {}, set()
if not []:               # 空列表是假值
    print("列表为空")

# Python 只有 and / or / not，没有 && || !
if age >= 18 and age <= 65:
    print("工作年龄")

# 链式比较（Python 独有，很优雅）
if 18 <= age <= 65:      # 等价于上面的 and 写法
    print("工作年龄")
```

**`is` vs `==` 的区别**：`==` 比较值是否相等，`is` 比较是否是同一个对象（内存地址）。判断 `None` 必须用 `is None`，这是 PEP 8 的硬性规定。

## 10. 海象运算符（:=）

Python 3.8 引入的赋值表达式，用 `:=` 在表达式内部赋值：

```python
# 传统写法：读取一行，检查是否为空
line = input("输入：")
while line != "quit":
    print(f"你输入了：{line}")
    line = input("输入：")      # 重复调用

# 海象运算符：赋值和判断合二为一
while (line := input("输入：")) != "quit":
    print(f"你输入了：{line}")

# 在推导式中也很实用
import re
raw_data = ["user:123", "invalid", "admin:456", "bad"]
results = [
    m.group(1)
    for item in raw_data
    if (m := re.match(r"(\w+):(\d+)", item))   # <--- 赋值并过滤
]
# ["user", "admin"]
```

不要滥用海象运算符——只有在"赋值+判断"确实减少重复代码时用。

## 11. 关键差异速查表

| 概念 | JavaScript / TypeScript | Python |
|------|------------------------|--------|
| 代码块 | `{ }` | 缩进（4 空格） |
| 变量声明 | `let` / `const` / `var` | 直接赋值 |
| 常量 | `const` | 全大写命名约定 + `Final` |
| 空值 | `null` / `undefined` | `None` |
| 布尔值 | `true` / `false` | `True` / `False` |
| 逻辑运算 | `&&` `\|\|` `!` | `and` `or` `not` |
| 字符串模板 | `` `${expr}` `` | `f"{expr}"` |
| 三元表达式 | `a ? b : c` | `b if a else c` |
| 数组/列表 | `[1, 2, 3]` | `[1, 2, 3]` |
| 对象/字典 | `{key: value}` | `{"key": value}`（键必须加引号） |
| 遍历 | `for...of` | `for item in iterable` |
| 箭头函数 | `(x) => x * 2` | `lambda x: x * 2` |
| 自增 | `i++` | `i += 1` |
| 打印 | `console.log()` | `print()` |
| 导入 | `import x from 'y'` | `from y import x` |
| 注释 | `//` 单行 `/* */` 多行 | `#` 单行，`"""` 多行（文档字符串） |
| 相等判断 | `===`（严格相等） | `==`（值相等） |
| 同一对象 | 无对应 | `is` |
| switch | `switch-case` | `match-case`（3.10+） |

## 常见坑点

**1. 可变默认参数陷阱**

这是 Python 最经典的坑，几乎每个新手都会踩：

```python
# ❌ 错误写法
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))   # ["a"]
print(add_item("b"))   # ["a", "b"] ← 预期是 ["b"]！
```

问题出在 `items=[]` ——这个默认值在函数**定义时**只创建一次，后续调用共享同一个列表对象。

```python
# ✅ 正确写法：用 None 作默认值
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**2. 整数缓存**

```python
a = 256
b = 256
print(a is b)    # True（CPython 缓存了 -5 到 256 的整数）

a = 257
b = 257
print(a is b)    # False（超出缓存范围，两个不同对象）
```

比较值用 `==`，判断 `None` 用 `is`。除此之外别用 `is` 比较其他东西。

**3. 缩进混用 Tab 和空格**

Python 3 不允许混用 Tab 和空格。Ruff 的 formatter 会自动统一为空格，配置好了就不用操心这个问题。

## 总结

- Python 用缩进界定作用域，强类型但动态类型，没有变量声明关键字
- f-string 是字符串格式化的标准方式，Python 3.14 新增 t-string 用于框架级安全处理
- 推导式、解包、切片、链式比较是 Python 的核心语法糖，写出来比 JS 更简洁
- `match-case` 比 `switch-case` 强大，支持结构匹配和变量绑定
- 可变默认参数是最常见的坑，用 `None` 替代可变对象作默认值

下一篇深入**函数与装饰器**——Python 的函数是一等公民，装饰器是 Python 元编程的入口。

## 参考

- [Python 官方教程 - 数据结构](https://docs.python.org/3.14/tutorial/datastructures.html)
- [PEP 750 - Template Strings](https://peps.python.org/pep-0750/)
- [PEP 572 - Assignment Expressions (海象运算符)](https://peps.python.org/pep-0572/)
- [PEP 636 - Structural Pattern Matching Tutorial](https://peps.python.org/pep-0636/)

# Python 全栈实战（十九）—— 内存模型与性能调优

Python 的"慢"是相对的。多数场景下瓶颈在 IO，不在 CPU。真正需要优化时，先定位问题（profiling），再对症下药——盲目优化是浪费时间。

> **环境：** Python 3.14.3

---

## 1. 引用计数 + 分代垃圾回收

CPython 的内存管理由两层机制协作：

**引用计数（Reference Counting）**：每个对象维护一个计数器，记录有多少引用指向它。引用数归零，立即释放。

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))   # 2（a 自身 + getrefcount 的参数）

b = a                        # 引用计数 +1
print(sys.getrefcount(a))   # 3

del b                        # 引用计数 -1
print(sys.getrefcount(a))   # 2
```

引用计数的限制：**循环引用**无法处理。

```python
class Node:
    def __init__(self):
        self.ref = None

a = Node()
b = Node()
a.ref = b
b.ref = a        # a → b → a 循环引用

del a
del b            # 引用计数不会归零，内存泄漏！
```

**分代垃圾回收（Generational GC）**：定期扫描对象，检测循环引用并破环释放。对象分为三代：

```mermaid
flowchart LR
    G0["第 0 代\n（新创建的对象）"] -->|存活| G1["第 1 代\n（经历过 1 次 GC）"]
    G1 -->|存活| G2["第 2 代\n（长期存活对象）"]

    style G0 fill:#d4edda,stroke:#28a745
    style G1 fill:#fff3cd,stroke:#ffc107
    style G2 fill:#f8d7da,stroke:#dc3545
```

新创建的对象放在第 0 代，GC 最频繁扫描第 0 代。多次 GC 后仍存活的对象晋升到更高代——高代扫描频率低，因为长寿命对象大概率继续存活。

```python
import gc

# 查看 GC 阈值
print(gc.get_threshold())    # (700, 10, 10)
# 第 0 代每 700 次分配触发一次 GC
# 第 0 代 GC 10 次后触发第 1 代 GC
# 第 1 代 GC 10 次后触发第 2 代 GC

# 手动触发 GC
gc.collect()

# 查看 GC 统计
print(gc.get_stats())
```

## 2. 内存分析：tracemalloc

`tracemalloc` 是标准库内置的内存追踪工具，定位内存消耗大户：

```python
import tracemalloc

tracemalloc.start()

# 运行业务代码
data = [{"id": i, "value": f"item_{i}"} for i in range(100_000)]

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("内存消耗 Top 5：")
for stat in top_stats[:5]:
    print(f"  {stat}")
```

```
内存消耗 Top 5：
  memory_test.py:6: size=15.3 MiB, count=100000, average=161 B
  memory_test.py:6: size=7.6 MiB, count=100000, average=80 B
```

精确看到哪一行代码消耗了多少内存。对比两个快照可以检测内存泄漏：

```python
snapshot1 = tracemalloc.take_snapshot()

# ... 运行一段代码 ...

snapshot2 = tracemalloc.take_snapshot()
diff = snapshot2.compare_to(snapshot1, "lineno")

print("内存增长 Top 5：")
for stat in diff[:5]:
    print(f"  {stat}")
```

## 3. 性能分析：cProfile

```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(1_000_000):
        total += i ** 2
    return total

# 方式一：命令行
# uv run python -m cProfile -s cumulative my_script.py

# 方式二：代码中分析
profiler = cProfile.Profile()
profiler.enable()
slow_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)          # 打印耗时 Top 10
```

输出示例：
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1000000    0.523    0.000    0.523    0.000 script.py:4(slow_function)
```

`tottime` 是函数自身耗时，`cumtime` 是包含子调用的总耗时。优先优化 `tottime` 高的函数。

## 4. 基准测试：timeit

```python
import timeit

# 对比两种实现
result_list = timeit.timeit(
    "[x**2 for x in range(1000)]",
    number=10_000,
)

result_map = timeit.timeit(
    "list(map(lambda x: x**2, range(1000)))",
    number=10_000,
)

print(f"列表推导：{result_list:.3f}s")   # ~2.1s
print(f"map+lambda：{result_map:.3f}s")  # ~2.8s
```

列表推导比 `map + lambda` 快约 25%——因为推导式是 Python 内部优化过的字节码操作，少了函数调用的开销。

## 5. 常见优化策略

### 选对数据结构

```python
# ❌ 在 list 中查找：O(n)
if user_id in user_list:
    ...

# ✅ 换成 set：O(1)
user_set = set(user_list)
if user_id in user_set:
    ...
```

### 避免不必要的对象创建

```python
# ❌ 每次循环创建新字符串
result = ""
for word in words:
    result += word + " "         # 每次 += 创建新字符串对象

# ✅ join 一次性拼接
result = " ".join(words)
```

### __slots__ 减少内存

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float
# 比普通 dataclass 节省 30-40% 内存
```

### 生成器替代列表

```python
# ❌ 创建完整列表再求和
total = sum([x ** 2 for x in range(10_000_000)])

# ✅ 生成器表达式，内存恒定
total = sum(x ** 2 for x in range(10_000_000))
```

### functools.lru_cache 缓存计算结果

```python
import functools

@functools.lru_cache(maxsize=256)
def expensive_query(user_id: int) -> dict:
    # 相同参数只计算一次，后续直接返回缓存
    ...
```

## 6. 何时不该优化

**Donald Knuth**："过早优化是万恶之源。"

优化前必须回答三个问题：
1. **瓶颈在哪？** 用 cProfile / tracemalloc 定位，不要靠猜
2. **该优化的是 Python 代码还是架构？** 很多时候加个缓存或改数据结构就解决了
3. **性能目标是什么？** "足够快"就行，不需要极致优化

如果 Python 代码确实是瓶颈（通常出现在科学计算、图像处理场景），考虑：
- 换用 NumPy / Pandas（底层是 C 实现，数量级的提升）
- 用 C 扩展或 PyO3（Rust）重写热点函数
- 用 Free-threaded Python 利用多核并行

## 常见坑点

**1. 循环引用导致 __del__ 不执行**

有循环引用的对象，`__del__` 析构方法可能永远不被调用（GC 不确定先销毁哪一个）。不要在 `__del__` 里放关键的清理逻辑——用 `with` 语句或 `contextlib.contextmanager` 替代。

**2. 全局变量阻止垃圾回收**

全局列表、全局字典如果持续追加数据又不清理，就是内存泄漏。定期清理或用 `deque(maxlen=N)` 限制大小。

## 总结

- CPython 用引用计数（即时释放）+ 分代 GC（处理循环引用）管理内存
- `tracemalloc` 定位内存消耗大户，对比快照检测内存泄漏
- `cProfile` 找出 CPU 耗时最高的函数，`timeit` 做微基准测试
- 优化顺序：选对数据结构 → 减少对象创建 → 缓存计算结果 → 考虑 C 扩展
- 先 profiling 再优化，盲目优化是反模式

下一篇进入 **Python 3.14 新特性与生态全景**——t-string、延迟注解、Free-threaded 深入、生态导览。

## 参考

- [Python 官方文档 - gc](https://docs.python.org/3.14/library/gc.html)
- [Python 官方文档 - tracemalloc](https://docs.python.org/3.14/library/tracemalloc.html)
- [Python 官方文档 - cProfile](https://docs.python.org/3.14/library/profile.html)

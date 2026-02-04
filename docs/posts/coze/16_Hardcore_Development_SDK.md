# Coze 零基础精通系列 16：硬核开发 —— Python SDK 与 IDE 深度编程指南

> **上一篇回顾**：已掌握用罗盘进行科学的 DevOps 管理。
> **本篇目标**：作为系列终章，本篇面向**程序员**。脱离拖拉拽的舒适区，深入 **Coze API** 和 **Python SDK**，探索如何通过代码构建更强大的业务逻辑。

---

## 1. 为什么需要写代码？

虽然 Coze 的低代码 (Low-Code) 已具备强大能力，但部分场景仍需代码介入：
1.  **复杂的加密运算**：例如需使用 AES-256 算法解密数据，低代码节点难以实现。
2.  **自定义业务逻辑**：某些逻辑（如“VIP 生日打 8 折，否则 9 折”）使用代码编写远比拖拽连线高效。
3.  **自有前端集成**：将 Bot 集成至自研的 Vue/React 网站，而非使用 Coze 原生网页。

此时，需要使用 **Coze SDK** 和 **IDE 编程**。

---

## 2. 场景一：IDE 深度编程 (Code Node 进阶)

工作流中的 **Code Node (代码节点)** 在 IDE 模式下威力倍增。

### 引入第三方库 (Python)
Coze 云端环境预装了 `requests`, `numpy`, `pandas` 等常用库。
这意味着可直接在 Coze 内进行数据分析。

**示例：计算股票均线 (MA)**
```python
import pandas as pd

async def main(args: Args) -> Output:
    params = args.params
    # 假设 Input 传入了一个包含最近 30 天价格的 list
    prices = params['history_prices']
    
    # 直接用 pandas 计算
    df = pd.DataFrame(prices, columns=['price'])
    ma5 = df['price'].rolling(window=5).mean().iloc[-1]
    
    return {"ma5": float(ma5)}
```
将此代码置于工作流中，即构建了一个强力计算器。

---

## 3. 场景二：使用 Python SDK 对接 Bot

若需在 Python 后端服务（如 Django/FastAPI）中调用 Coze Bot，请使用官方 SDK。

### 1. 安装
```bash
pip install coze-api
```

### 2. 初始化 (Auth)
需先在 Coze 个人中心申请 **PAT (Personal Access Token)**。

```python
from coze_api import CozeAPI

# 初始化客户端
coze = CozeAPI(api_key="你的_PAT_Token")
```

### 3. 流式对话 (Streaming Chat)
Web 开发中常需“打字机效果”以减少用户等待。SDK 完美支持此功能。

```python
def chat_with_bot(query):
    # 发起对话
    chat_stream = coze.chat.stream(
        bot_id="你的_BOT_ID",
        user_id="user_123",
        query=query
    )
    
    print(f"User: {query}\nBot: ", end="")
    
    # 实时接收每一个字
    for event in chat_stream:
        if event.event == "message":
            print(event.message.content, end="", flush=True)
            
    print("\n[对话结束]")

chat_with_bot("帮我写一首关于秋天的诗")
```

### 4. 各种高级操作
SDK 除聊天功能外，还支持：
*   **上传文件**：`coze.file.upload()`，让 Bot 读取 PDF。
*   **管理会话**：`coze.conversation.create()`，让 Bot 记住上下文。
*   **触发工作流**：可绕过 Bot，直接运行指定 Workflow。

---

## 4. 场景三：将 Bot 封装为微服务

结合 FastAPI + Coze SDK，十分钟内即可构建一个 AI 微服务。

```python
from fastapi import FastAPI
from coze_api import CozeAPI

app = FastAPI()
coze = CozeAPI(api_key="xxx")

@app.post("/chat")
async def chat(query: str):
    # 调用 Coze
    response = coze.chat.create(
        bot_id="xxx",
        user_id="web_user",
        query=query
    )
    return {"reply": response.messages[0].content}

# 运行服务：uvicorn main:app --reload
```
内部系统只需访问该本地 API，即可获取 Coze 能力。

---

## 5. 总结：低代码 + 纯代码 = 全能

Coze 的核心优势在于**弹性**。
*   **对于产品经理**：拖拉拽即可实现 PMF (Product-Market Fit) 产品。
*   **对于程序员**：提供完整的 API/SDK 接口，支持深度定制与集成。

**第 16 篇完结寄语**：
若将 AI 开发比作 **“炼金术”**：
*   **Workflows** 是炼金阵。
*   **Prompt** 是咒语。
*   **Code** 是贤者之石。

装备已集齐，去创造奇迹吧！

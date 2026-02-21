# Coze 零基础精通系列 16：硬核开发 —— API 深度集成与 SDK 指南

> **上一篇回顾**：已掌握罗盘 (AgentOps) 的使用。
> **本篇目标**：脱离 Coze 的图形界面，以**程序员**的视角，通过 **API** 和 **SDK** 将 Bot 植入到任何应用（网站、APP、智能硬件）中。

---

## 1. 为什么需要 API 开发？

虽然 Coze 的 Web 界面很方便，但真正的商业落地往往需要：
1.  **自定义 UI**：可能拥有自己的 React/Vue 网站，想把 Bot 作为一个聊天窗口嵌入其中。
2.  **数据隐私**：不想让用户直接访问 Coze，而是通过自己的服务器中转。
3.  **复杂逻辑**：Bot 只是业务链条中的一环（例如：用户下单 -> 触发 Bot 分析 -> 写入数据库）。

此时，需要 **Coze API**。

---

## 2. 场景一：IDE 模式下的 Code Node (Python)

在工作流 (Workflow) 中，**Code Node** 是处理复杂数据的神器。
Coze 云端环境预装了 `numpy`, `pandas`, `requests` 等常用库。

**示例：用 Pandas 计算股票均线**
```python
import pandas as pd
from runtime import Args

async def main(args: Args) -> dict:
    params = args.params
    # 假设 input 传入了一个包含价格的 list: [10, 12, 11, ...]
    prices = params.get('history_prices', [])
    
    if not prices:
        return {"ma5": 0}
    
    # 使用 Pandas 极速计算
    df = pd.DataFrame(prices, columns=['price'])
    ma5 = df['price'].rolling(window=5).mean().iloc[-1]
    
    return {"ma5": float(ma5) if not pd.isna(ma5) else 0.0}
```
**技巧**：尽量使用 `pandas` 或 `numpy` 进行向量化运算，避免在 Python 中写通过 `for` 循环处理大量数据，以节省运行时间 (Timeout)。

---

## 3. 场景二：使用 Python SDK 对接 (官方推荐)

Coze 提供了官方 Python SDK，简化了鉴权和流式处理。

### 1. 安装
```bash
pip install cozepy  # 请认准官方 SDK 名称
```

### 2. 初始化
需先在 Coze 个人中心 (Personal Access Token) 申请令牌。

```python
from cozepy import Coze, TokenAuth

# 初始化客户端 (以 Coze.com 为例，若是 Coze.cn 请查阅对应文档)
coze = Coze(auth=TokenAuth(token="你的_PAT_Token"))
```

### 3. 流式对话 (Streaming Chat)
这是最核心的功能。让 AI 的回复像打字机一样逐字蹦出来。

```python
def chat_stream(bot_id, user_id, query):
    # 发起流式对话
    stream = coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            {"role": "user", "content": query, "content_type": "text"}
        ]
    )
    
    print(f"User: {query}\nBot: ", end="")
    
    # 实时接收事件
    for event in stream:
        if event.event == "conversation.message.delta":
            # 打印增量内容
            print(event.data.content, end="", flush=True)
            
    print("\n[对话结束]")

chat_stream("bot_123456", "user_001", "用 Python 写个冒泡排序")
```

---

## 4. 场景三：前端直接调用 (Node.js / Browser)

如果是前端开发者，想在网页里直接调用 Coze API (注意保护 Token 安全，建议通过后端转发)。

Coze API 兼容标准的 HTTP SSE (Server-Sent Events) 协议。

**使用原生 Fetch API 调用：**

```javascript
async function chatWithCoze(query) {
  const BOT_ID = '你的_BOT_ID';
  const TOKEN = 'Bearer 你的_PAT_TOKEN';

  const response = await fetch('https://api.coze.com/v3/chat', {
    method: 'POST',
    headers: {
      'Authorization': TOKEN,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      bot_id: BOT_ID,
      user_id: 'web_user_01',
      stream: true, // 开启流式
      additional_messages: [
        { role: 'user', content: query, content_type: 'text' }
      ]
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    // 解析 SSE 数据
    const chunk = decoder.decode(value);
    console.log('收到数据片:', chunk);
    // 实际项目中需要处理 buffer 拼接和 event 解析
  }
}
```

---

## 5. 常见坑点 (Gotchas)

1.  **超时设置**：如果 Bot 包含长 Workflow（如画图、联网搜索），HTTP 请求可能会超过 60秒。务必在客户端设置更长的 `timeout`。
2.  **会话持久化**：API 默认是无状态的。若需“记住”用户上下文，请在调用时传入相同的 `conversation_id`。
3.  **流式解析**：SSE 数据可能会被截断（一个 JSON 分两段发）。在生产环境中，建议使用成熟的 SSE Parser 库，不要手动用 `split` 去切分字符串。

---

## 总结

掌握了 API 开发，就打通了 **Coze -> 真实世界** 的最后一公里。
*   **Prompt** 赋予了灵魂。
*   **Workflow** 赋予了逻辑。
*   **API** 赋予了触达用户的能力。

至此，**Coze 零基础精通系列** (Part 1 & Part 2) 圆满通过！
用这些知识，创造出真正改变效率的 AI 应用。
Happy Coding! 🚀

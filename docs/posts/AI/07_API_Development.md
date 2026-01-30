# 07. API 开发进阶：Token 算法与流式传输 (SSE)

> [!NOTE]
> **生产级开发**
> 
> 会调 API 只是入门。在生产环境中，需要关心：
> *   **Token 计算**: 怎么精准计费，防止 Context Overflow？
> *   **流式传输 (Streaming)**: 怎么实现 ChatGPT 那种“打字机”效果？
> *   **Function Calling 原理**: 其实是 XML/JSON Schema 的注入。

## 1. Token 计数算法与 Context Window

### Context Window (上下文窗口)
每个模型都有窗口限制（如 GPT-4-128k）。这限制了 `Input + Output`的总长度。
很多人以为超了会报错，其实更危险的是 **Truncation (截断)**：模型默默地丢掉了最早的 Prompt，导致它忘了人设。

### Tiktoken 原理
OpenAI 使用 `tiktoken` 库进行 BPE 编码。在 Python 中通过 API 计算 Token 是不对的（因为要发请求，慢），应该在本地算。

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

text = "Hello, world!"
print(count_tokens(text)) 
# encoding.encode(text) 可能会返回 [9906, 11, 1917, 0] 这样的 ID 列表
```

**System Prompt 的 Token 陷阱**:
在 ChatML 格式中，每条消息还有额外的 overhead（比如 `<|im_start|>` 和换行符）。
官方公式：
$$ \text{Total} = \sum (\text{ContentTokens} + 4) + 3 $$
如果不把这 4 个 token 算进去，当 context 塞满时，API 请求会把 prompt 截断导致报错。

## 2. 流式传输 (Streaming) 与 SSE 协议

为什么 ChatGPT 能一个字一个字蹦？
这用的是 **Server-Sent Events (SSE)** 协议，而不是 WebSocket。

### SSE 协议详解
SSE 是基于 HTTP 的单向长连接。
*   **Content-Type**: `text/event-stream`
*   **数据格式**: 每条数据以 `data: ` 开头，双换行结束。

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"choices": [{"delta": {"content": "Hello"}}]}

data: {"choices": [{"delta": {"content": " world"}}]}

data: [DONE]
```

### Python 实现流式接收

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "写首诗"}],
    stream=True  # 关键开关
)

for chunk in stream:
    # chunk 不是完整的 json，而是 fragment
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True) # 实时打印，不换行
```

## 3. Function Calling 的底层原理

Function Calling 感觉很神奇，其实本质是 **Prompt Injection**。

当你定义了 `tools = [...]` 时，OpenAI 后台其实把这些 Schema 转成了类似 TypeScript 类型定义的文本，注入到了 System Prompt 里。

**System Prompt (Hidden)**:
```markdown
# Tools
You have access to the following functions:

namespace functions {
  type get_weather = (_: {
    location: string,
    unit?: "celsius" | "fahrenheit",
  }) => any;
}

## Instructions
If the user asks something that requires a tool, output a JSON object like:
{"function_name": "get_weather", "arguments": "{\"location\": \"Beijing\"}"}
```

模型被微调过，倾向于在特定场景下输出这种 JSON 格式，而不是普通文本。
这就是为什么有时候它会输出错误的 JSON（幻觉），因为它本质上还是在做文本生成的概率预测。

## 4. 性能指标：TTFT 与 TPS

在 AI 工程化中，关注两个核心指标：

1.  **TTFT (Time to First Token)**: 首字延迟。
    *   用户发出问题 -> 看到第一个字的时间。
    *   主要受 **Prefill (预填充)** 阶段影响。Prompt 越长，TTFT 越慢（因为计算 Attention 矩阵是 $O(N^2)$）。

2.  **TPS (Tokens Per Second)**: 生成速度。
    *   看到第一个字后 -> 哒哒哒打字的速度。
    *   主要受 **Decode (解码)** 阶段影响。受显存带宽限制。

## 小结

做 AI 应用开发，不能只把 API 当黑盒。
1.  **Tiktoken**: 必须在本地精确计算 Token 消耗。
2.  **SSE**: 必须掌握流式处理，否则用户体验会很卡。
3.  **Function Calling**: 理解它是 Prompt 注入，就要做好容错（JSON 解析失败重试）。

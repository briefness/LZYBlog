# 02. 大模型逻辑：从 Transformer 到 Mamba (2026 版)

> [!WARNING]
> **架构演进**
> 
> 虽然 Transformer 统治了 AI 十年，但到了 2026 年，单纯的 Attention 机制已经遇到瓶颈。
> 面对 **无限长上下文 (Infinite Context)** 的需求，**SSM (State Space Models)** 和 **Hybrid 架构** 成为了新标准。

## 1. Transformer 的阿喀琉斯之踵

前文中讲到 Self-Attention 的公式：
$$Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d_k}})V$$

这里的 $QK^T$ 是一个 $N \times N$ 的矩阵。
*   **计算复杂度**: $O(N^2)$。
*   **内存占用**: $O(N^2)$。
*   **KV Cache**: 推理时需要显存缓存所有的 Key 和 Value。一个 128k 窗口的请求，光 KV Cache 就要吃掉几十 G 显存。

这意味着：Transformer **越长越慢，越长越贵**。

## 2. 复古与革新：SSM (State Space Models)

SSM (如 Mamba) 的灵感来自 60 年代的控制理论（卡尔曼滤波）和 RNN。
它的核心思想是：**不要记下所有历史，而是把历史压缩成一个状态 $h_t$**。

### 核心公式 (线性递归)
$$ h_t = A h_{t-1} + B x_t $$
$$ y_t = C h_t $$

*   $h_t$: 当前的隐状态 (Hidden State)。
*   $x_t$: 当前输入。
*   $y_t$: 当前输出。

**优势**：
1.  **线性复杂度 $O(N)$**: 无论序列多长，计算量只和长度成线性关系。
2.  **推理恒定显存**: 不需要 KV Cache。只需要存一个固定大小的 $h_t$。
3.  **极速推理**: 生成速度比 Transformer 快 5-10 倍。

## 3. 2026 标准：Hybrid Architecture (混合架构)

纯 Mamba 模型在“回忆具体细节”（Recall）上不如 Transformer。
所以，2026 年的主流模型（如 Jamba, Griffin）采用了 **Hybrid (混合)** 策略：

```mermaid
graph TD
    Input --> Block1[Mamba Block]
    Block1 --> Block2[Mamba Block]
    Block2 --> Block3[Mamba Block]
    Block3 --> Attn[Attention Layer (Sliding Window)]
    Attn --> Block4[Mamba Block]
    
    style Attn fill:#ffccbc
    style Block1 fill:#e1f5fe
```

*   **90% 层使用 Mamba**: 处理海量日常信息，保持高效。
*   **10% 层使用 Attention**: 在关键时刻“睁开眼”查阅历史，保证精准度。

这种架构兼顾了无限长度处理和高精度召回。

## 4. Tokenization (BPE) ... (保留原始内容)
## 5. Inference (Temperature) ... (保留原始内容)

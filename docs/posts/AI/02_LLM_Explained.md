# 02. 大模型架构深度解析：从 Transformer 到 Mamba Hybrid

> [!NOTE]
> **Evolution of Architecture**
> 
> 大模型的架构演进史，本质上是 **"Memory vs Efficiency" (记忆力 vs 效率)** 的权衡。
> **The Science**: 数学原理（Attention, SSM 离散化）。
> **The Art**: 架构设计（Hybrid 策略，如何像搭积木一样混合使用它们）。

---

## 第一部分：Deep Dive 原理 (The Science)

### 1. Transformer：暴力美学的 $O(N^2)$

Transformer 的核心设计理念为：**Don't Compress (不压缩)**。
它把历史上的每一个 Token 都完完整整地存在显存里 (KV Cache)。

#### 数学直觉：Attention 的物理意义
$$ \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V $$

*   **$QK^T$**: 这是一个 $N \times N$ 的相似度矩阵。
    *   $N=1k$ 时，矩阵大小是 $10^6$。
    *   $N=100k$ 时，矩阵大小是 $10^{10}$ (100亿)。
*   导致 Transformer 处理长文本成本极高。它的计算量随着长度 **平方级爆炸**。

#### 为什么是 $\sqrt{d_k}$? (梯度稳定性)
如果不除以 $\sqrt{d_k}$，点积结果会随着维度增加变得巨大。这会导致 Softmax 函数进入“饱和区”，梯度趋近于 0（梯度消失），导致模型无法训练。这是一个为了**数值稳定性**而设计的数学补丁。

### 2. Mamba (SSM)：回归 RNN 的线性复杂度

为了解决 $O(N^2)$ 问题，Mamba (State Space Model) 沿用了 RNN 的思想：**Compress (压缩)**。
它将无限的历史，压缩进一个固定大小的状态 $h_t$ 中。

#### 核心公式：选择性状态空间 (Selective SSM)
Mamba 具有动态性。它引入了 **"Selection Mechanism" (选择机制)**：
$$ h_t = (1 - \Delta_t) h_{t-1} + \Delta_t x_t $$
*(注：这是简化版理解，实际是离散化 ODE)*

这里的 $\Delta_t$ 是关键。它是**动态的**，由当前输入 $x_t$ 决定：
*   如果 $x_t$ 是垃圾广告 $\rightarrow$ $\Delta_t \approx 0$ (忽略，保持 $h_{t-1}$)。
*   如果 $x_t$ 是关键人名 $\rightarrow$ $\Delta_t \approx 1$ (遗忘旧的，写入新的)。

这种**由输入决定遗忘门**的机制，使得 Mamba 具备 Transformer 级别的推理能力，却只需要 $O(1)$ 的推理显存。

---

## 第二部分：实战架构 (The Architecture)

纯 Mamba 在处理“查电话簿”这种任务时表现不佳（因为状态被压缩了，细节丢失）。
2026 年的主流架构是 **"Jamba-Style" Hybrid**。

### 1. 混合架构设计 (Hybrid Design)

就像计算机有 RAM (大而慢) 和 L1 Cache (小而快) 一样。
现代 LLM 也是分层的：

*   **主体 (Body)**: 90% 的层是 **Mamba/SSM**。
    *   **作用**: 快速吞噬海量文本，建立宏观的世界观。
    *   **优势**: $O(N)$ 训练，极低显存占用。
*   **关键点 (Heads)**: 10% 的层是 **Attention** (通常是 Sliding Window)。
    *   **作用**: 这几层用来“精准查阅”最近的上下文，保证细节不瞎编。
    *   **优势**: 找回精准的“Copy-Paste”能力。

### 2. 显存救星：KV Cache Quantization
Transformer 虽然强大，但在推理时面临巨大的**显存瓶颈**。
为了生成下一个 token，必须把之前所有 token 的 Key 和 Value 记在显存里 (KV Cache)。
*   **问题**: 对于 128k 上下文，KV Cache 会占用大量 A100 显存。
*   **解法 (2026)**: **KV Cache 量化**。
    *   不像权重需要 int8/int4，KV Cache 对精度不那么敏感。
    *   2026 年的主流是用 **FP4** 甚至 **Binary** 格式存储 KV Cache。这就让显存占用下降了 4-8 倍，使得在单张显卡上跑 100k context 成为可能。

### 2. PyTorch 实现：Scaled Dot-Product Attention

保留 Attention 作为关键组件时，理解它的代码实现依然至关重要。

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(query, key, value, mask=None):
    """
    Args:
        query: [Batch, Heads, Len_Q, Dim]
        key:   [Batch, Heads, Len_K, Dim]
        value: [Batch, Heads, Len_K, Dim]
    """
    d_k = query.size(-1)
    
    # 1. 计算相似度分数 (The "Search")
    # [Len_Q, Dim] @ [Dim, Len_K] -> [Len_Q, Len_K]
    scores = torch.matmul(query, key.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k))
    
    # 2. 掩码 (Masking): 遮住未来，或者遮住 Padding
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # 3. 归一化 (Softmax): 变成概率分布
    p_attn = F.softmax(scores, dim=-1)
    
    # 4. 加权求和 (The "Retrieval")
    # [Len_Q, Len_K] @ [Len_K, Dim] -> [Len_Q, Dim]
    return torch.matmul(p_attn, value), p_attn
```

---

## 小结

*   **Transformer**: 是豪宅。住得舒服（效果好），但太贵（显存爆炸）。适合短上下文高精度任务。
*   **Mamba**: 是胶囊旅馆。极度高效，虽然有点挤（压缩损失），但能住很多人（几百万 Token）。
*   **Hybrid (2026)**: 是**豪宅+胶囊**的混合体。
    *   大部分时候住胶囊（用 Mamba 处理长文档）。
    *   关键时刻住豪宅（用 Attention 提取关键信息）。
    *   这是目前实现 **无限上下文 (Infinite Context)** 的最佳工程解。

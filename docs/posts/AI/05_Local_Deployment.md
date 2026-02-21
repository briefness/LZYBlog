# 05. 本地部署原理：从量化算法到 vLLM

> [!NOTE]
> **Why Local?**
>
> 本地部署不仅关乎省钱。它是关于**隐私 (Privacy)** 和 **延迟 (Latency)** 的战争。
> 本文剖析让大模型在本地飞起来的核心技术：**Quantization (量化)**, **PagedAttention (显存管理)** 和 **NPU 架构**。

## 1. 瓶颈在哪？(Memory Bound)

GPU 虽强，但 LLM 推理是典型的 **Memory Bound (显存受限)** 任务。

*   **算术强度**: $\frac{\text{FLOPs (计算量)}}{\text{Bytes (访存量)}}$。
*   **现状**: 每生成 1 个 Token，就要把几十 GB 的参数从显存搬运一遍到计算单元。
*   **结果**: Tensor Core 算得飞快，但大部分时间在等显存带宽 (High Bandwidth Memory)。

这也是为什么 Apple Silicon (M系列芯片) 在推理上能打平甚至超越部分独显——它的**统一内存带宽 (United Memory Bandwidth)** 高达 800GB/s。

## 2. 量化技术 (Quantization)

既然搬运数据慢，那就把数据变小。
量化的本质是将高精度浮点数 (`FP16`) 映射到低精度整数 (`INT4` 甚至 `INT2`)。

### 线性量化 (Affine Quantization)
最通用的方案。
$$ Q = \text{round}(S \cdot (R - Z)) $$
把参数映射到 0-15 (INT4) 的整数区间。

### 离群点挑战 (The Outlier Problem)
LLM 的激活值中存在极端的 **Outliers (离群点)**，比平均值大 100 倍。直接截断会让模型变傻。
*   **SmoothQuant / AWQ**: 数学上的 trick。既然激活值难量化，就把激活值的难度转移到权重上（等价变换）。

## 3. 推理加速引擎：vLLM & PagedAttention

只有量化还不够。当前生产环境部署，**vLLM** 是绝对的标准。

### 显存碎片化问题
传统推理引擎就像乱停车。一个 Request 来了，分配一块连续显存。产生的 Token 长度不确定，预分配太少会溢出，太多会浪费。
结果：显存利用率极其低下，明明有空闲显存却跑不了新请求。

### PagedAttention
受操作系统 **虚拟内存 (Virtual Memory)** 的启发。
*   把显存切成一个个小的 **Blocks** (比如 16MB)。
*   KV Cache 不需连续，可以分散存储。
*   通过查表 (Page Table) 逻辑映射。

**效果**: 显存浪费率从 60% 降到 <4%。吞吐量 (Throughput) 提升 20 倍。

## 4. Context Caching (上下文缓存)

这是近年最重要的优化之一 (DeepSeek/Anthropic/Google 均支持)。

**场景**: 同样一份 50页 的 PDF，你问了 10 个不同的问题。
**传统**: 每次提问，都要把这 50页 PDF 重新计算一遍 KV Cache。
**Caching**: 计算一次，把 KV Cache 存到显存/内存里。下次直接复用。

*   **延迟**: 首字延迟 (TTFT) 降低 90%。
*   **成本**: 价格降低 90%（API 提供商通常对 Cache 命中部分打折）。

## 5. 工程实践：GGUF 与本地运行

大众用户不需要折腾 vLLM，**GGUF** 格式是最佳选择。

### GGUF & mmap
曾经的模型加载需要把文件读进 RAM，再拷进 VRAM。
GGUF 支持 **mmap (Memory Mapping)**:
*   操作系统直接把硬盘文件映射到虚拟地址。
*   **零拷贝**: 需要哪块数据，OS 自动从硬盘搬运。
*   **秒开**: 几十 GB 的模型，点击即用。

### 推荐工具
*   **Ollama**: 命令行神器，后端基于 llama.cpp。
*   **LM Studio**: 图形界面，适合新手。
*   **vLLM** (Python): 适合企业级、高并发服务部署。

## 小结

1.  **量化** 是为了解决带宽瓶颈。
2.  **vLLM (PagedAttention)** 彻底解决了显存碎片化。
3.  **Context Caching** 让长文档对话不再昂贵。
4.  **NPU/LPU** 正在取代通用 GPU 成为推理主力。

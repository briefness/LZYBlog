# 05. 本地部署原理：从量化算法到 NPU 架构

> [!NOTE]
> **Why Local?**
> 
> 本地部署不仅仅是省钱。它是关于**隐私 (Privacy)** 和 **延迟 (Latency)** 的战争。
> 本文剖析让大模型跑在你的 MacBook/手机上的两大核心技术：**Quantization (量化)** 和 **NPU (专用架构)**。

---

## 第一部分：Deep Dive 原理 (The Science)

### 1. 为什么 GPU 不是最优解？(Memory Bound)

GPU 是为了计算密集型任务（渲染）设计的，而 LLM 推理是典型的 **Memory Bound (内存受限)** 任务。

*   **算术强度 (Arithmetic Intensity)**: $\frac{\text{FLOPs (计算量)}}{\text{Bytes (访存量)}}$。
*   **LLM 推理特性**: 每生成 1 个 Token，就要把几十 GB 的权重全部从显存搬运一遍到计算单元。
*   **瓶颈**: 计算单元 (Tensor Core) 算得飞快，但大部分时间在等显存带宽 (HBM Bandwidth) 搬数据。

这就是为什么 **LPU (Language Processing Unit)** 和 **Apple Silicon** 甚至比某些独显还快——因为它们不仅有算力，更有恐怖的**统一内存带宽**。

### 2. 量化技术 (Quantization)：精度的艺术

大模型本来全是 `FP16` (16-bit 浮点数)。但我们真的需要小数点后这么多位吗？
量化的本质是将高精度浮点数映射到低精度整数 (如 `INT4`，甚至 `1.58-bit`)。

#### 线性量化公式 (Affine Quantization)
这是目前最通用的量化数学基础。
$$ Q = \text{round}(S \cdot (R - Z)) $$
$$ R = S^{-1} \cdot (Q + Z) $$
*   $R$ (Real): 真实的 FP16 数值。
*   $Q$ (Quantized): 量化后的 INT8/INT4 整数。
*   $S$ (Scale): 缩放因子（步长）。
*   $Z$ (Zero Point): 零点偏移（确保 0 能被精确表示）。

#### 离群点挑战 (The Outlier Problem)
如果参数分布是完美的高斯分布，那就简单了。
但研究发现，LLM 的激活值中存在极端的 **Outliers (离群点)**，某些通道的值比平均值大 100 倍。
*   如果强行量化，这些大值会被截断 (Clip)，模型瞬间变傻。
*   **SmoothQuant / AWQ** 算法的核心思想：**把激活值的难度转移到权重上**。既然激活值很难量化，那我就在数学上把激活值除以一个系数，同时把权重乘以这个系数。
$$ X \cdot W = (X/s) \cdot (W \cdot s) $$

---

## 第二部分：实战架构 (The Engineering)

### 1. 2026 新物种：LPU 与专有 NPU

*   **LPU (Language Processing Unit)**: 如 Groq。抛弃 HBM，全用超高速 SRAM。确定性数据流设计，杜绝 Cache Miss。
*   **NPU (Neural Processing Unit)**: 手机端（Apple A系列/骁龙/麒麟）。针对矩阵乘法优化的专用电路，能耗比极高，让 10B 模型在手机上只耗 3W 电。

### 2. GGUF 格式：mmap 的胜利

曾经我们用 `.bin` 或 `.pth`。现在 `GGUF` 统一了江湖。
GGUF 的杀手锏是完美支持 **mmap (Memory Mapping)**。

*   **传统加载**: Read file -> RAM -> VRAM。这就需要消耗双倍内存，且启动慢。
*   **mmap 加载**: 操作系统直接把硬盘文件映射到虚拟内存地址。
    *   **零拷贝**: 写代码时感觉像是在读内存，实际上 OS 在后台按需从硬盘搬运数据 (Page Fault)。
    *   **瞬间启动**: 几十 GB 的模型，双击即用，无需漫长的 Loading 进度条。

### 3. BitNet b1.58：1-bit LLM 的革命

2026 年最震撼的工程突破之一。
微软提出的 BitNet 证明了：我们将不再需要矩阵乘法 (Mul-Add)。
参数只有三个值：`{-1, 0, +1}`。

*   **计算**: 所有的乘法变成了 **加减法 (Addition/Subtraction)**。
*   **能耗**: 降低 70%。这让手机端跑 100B 模型成为可能。
*   **原理**: 训练时就加入量化噪声 (Quantization Aware Training, QAT)，强迫模型适应低精度。

---

## 小结

*   **Roofline Model**: 决定了 LLM 推理是拼带宽，而不是拼算力。
*   **Quantization**: 从 Affine 到 SmoothQuant，是为了在降低显存的同时保留离群点信息。
*   **GGUF**: 利用 OS 的 mmap 机制实现了模型的分发与秒开。
*   **NPU**: 让 AI 从云端回到了掌心。

# 04. 视觉生成原理：从 Diffusion 数学到 Sora 架构

> [!NOTE]
> **Generating Reality**
> 
> 如果说 GPT 理解了人类语言的**语法 (Syntax)**。
> 那么 Sora 则理解了物理世界的**规律 (Physics)**。
> 本文将带你深入理解视觉生成的底层数学原理 (Diffusion) 和最新的架构演进 (DiT)。

---

## 第一部分：Deep Dive 原理 (The Science)

### 1. 扩散模型 (Diffusion)：拆解上帝的画笔

Diffusion 的本质不是“绘画”，而是**受控的去噪**。
它受非平衡热力学的启发：一杯墨水滴入水中会自然扩散（从有序到无序），而生成过程就是逆转这个时间轴（从无序到有序）。

#### 数学直觉：Reparameterization Trick
我们不需要一步步加噪。利用高斯分布的性质，我们可以一步直接算出任意时刻 $t$ 的坏图像 $x_t$：
$$ x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon $$
*   $\sqrt{\bar{\alpha}_t} x_0$: 原始信号的残留（Signal）。
*   $\sqrt{1 - \bar{\alpha}_t} \epsilon$: 添加的噪声（Noise）。
*   **任务**：随着 $t$ 增大，信号越来越弱，噪声越来越强。模型的任务就是在给定 $t$ 的时刻，把 $\epsilon$ 预测出来并减掉。

#### 为什么 Loss 这么简单？
令人惊讶的是，尽管背后的变分推导（ELBO）极其复杂，最终的 Loss 函数却退化为了简单的 **MSE (均方误差)**：
$$ Loss = \| \epsilon_{True} - \epsilon_{Predicted} \|^2 $$
这就好比给模型看一张“雪花点图”，问它：“请指出这里面哪部分是刚才人为加进去的噪点？”

### 2. DiT (Diffusion Transformer)：架构的范式转移

在 Stable Diffusion 时代，霸主是 **U-Net**（基于卷积 CNN）。
但到了视频生成时代 (Sora/Kling)，**DiT** 成为了唯一标准。

#### 为什么要抛弃 U-Net？
*   **CNN 的局限**：卷积只能看到局部（Local Receptive Field）。在视频中，第1帧的鸟可能飞到第100帧，CNN 很难捕捉这种长距离的时空依赖。
*   **Transformer 的优势**：Attention 机制天生具有**全局视野 (Global Context)**。

#### DiT 核心机制：AdaLN (Adaptive Layer Norm)
DiT 如何理解“画一只猫”这个指令？
它通过 **AdaLN** 机制，将 Condition（提示词/时间步）注入到了网络的每一层。

*   **标准 LayerNorm**: 归一化 $\rightarrow$ 乘 $\gamma$ 加 $\beta$ (静态参数)。
*   **AdaLN**: 归一化 $\rightarrow$ **根据提示词动态生成** $\gamma(c)$ 和 $\beta(c)$。
    *   如果提示词是“白天”，$\gamma$ 可能放大亮度通道。
    *   如果提示词是“夜晚”，$\gamma$ 可能抑制亮度通道。
    *   **本质**：Prompt 实际上是在动态修改神经网络的**层参数**。

---

## 第二部分：实战演进 (The Evolution)

### 1. 3D VAE：时空压缩机

视频的数据量是惊人的 (1分钟 1080p ≈ 1440张图)。直接在像素空间 (Pixel Space) 算 Diffusion 会算死显卡。
解决方案是 **3D VAE (Variational Autoencoder)**。

*   **2D 压缩**: 将一张 $1024 \times 1024$ 的图压缩成 $128 \times 128$ 的 Latent。
*   **3D 压缩**: 将连续的 10 帧画面，压缩成 1 帧 Latent。

这意味着 Sora 看到的不是“视频”，而是一个个高度浓缩的**时空立方体 (Spacetime Patches)**。

### 2. World Simulator：物理规律的涌现

这是最让人兴奋的地方。
我们没有给 DiT 写过一行物理代码（没有 `gravity = 9.8`）。
但通过学习海量视频，DiT 在 Latent Space 中**自发涌现**了物理常识：

*   **物体恒存性**: 人走到树后面，不会凭空消失，走出来时还在。
*   **流体动力学**: 咖啡倒在桌子上，会根据液体粘度自然铺开。
*   **光影反射**: 墨镜里会反射出对面的霓虹灯。

这证明了：当模型足够大、数据量足够多时，**预测下一个 Frame** 等价于 **模拟世界运行的规律**。

---

## 小结

*   **Diffusion**：利用高斯分布的逆过程，从噪声中重构信号。
*   **DiT 架构**：用 Transformer 取代 U-Net，获得处理长时序视频的能力。
*   **AdaLN**：让 Prompt 动态控制神经网络的层参数，实现精准生成。
*   **终局**：视频生成模型不仅仅是做特效，它是通往 **General World Model (通用世界模型)** 的必经之路。

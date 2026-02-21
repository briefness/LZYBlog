# 04. 视觉生成原理：从 Diffusion 数学到 Flux/Sora

> [!NOTE]
> **Generating Reality**
> 
> 如果说 GPT 理解了人类语言的**语法 (Syntax)**。
> 那么 Sora 和 Flux 则理解了物理世界的**规律 (Physics)**。
> 本文解析视觉生成的底层数学 (Diffusion) 和最新架构演进 (DiT & Flow Matching)。

## 1. 扩散模型 (Diffusion)

Diffusion 的本质并非“绘画”，而是**去噪 (Denoising)**。
一杯红墨水滴入水中会扩散开（有序 -> 无序），生成过程就是逆转这个时间轴（无序 -> 有序）。

### 数学直觉
无需逐步加噪。利用高斯分布性质，可以直接算出任意时刻 $t$ 的坏图像 $x_t$。
模型的任务就是在给定 $t$ 时刻，把添加的噪声 $\epsilon$ 预测出来并减掉。

尽管背后的 ELBO 推导极其复杂，最终的 Loss 函数却退化为简单的 **MSE (均方误差)**：
$$ Loss = \| \epsilon_{True} - \epsilon_{Predicted} \|^2 $$
这就好比给模型看一张电视雪花屏，让它“猜”出原本的信号是什么。

## 2. DiT (Diffusion Transformer) 架构

在 Stable Diffusion 时代，U-Net（CNN 架构）是霸主。
但到了 Sora 和 Flux 时代，**DiT** 成了标准。

*   **CNN 的局限**: 卷积只能看到局部。视频里第1帧的鸟飞到第100帧，CNN 很难捕捉这种长距离依赖。
*   **Transformer**: Attention 机制天生具有**全局视野**。

### 核心机制：AdaLN
DiT 如何理解“画一只猫”的指令？
通过 **AdaLN (Adaptive Layer Norm)**。

*   Prompt 不仅仅是 Embedding，它直接通过 AdaLN 动态修改了神经网络每一层的**缩放参数** ($\gamma, \beta$)。
*   如果是“晴天”，参数会调整以增强亮度通道；如果是“雨天”，则抑制。
*   **本质**: Prompt 在动态重构神经网络的权重分布。

## 3. 新标杆：Flux 与 Flow Matching

Stable Diffusion 3 和 **Flux.1** (目前最強开源模型) 抛弃了传统的 DDPM，转向了 **Flow Matching**。

### 什么是 Flow Matching？
传统的 Diffusion 像是在雾中漫步（随机游走），慢慢找到目标图片。路径是曲折的。
Flow Matching 则试图在“噪声分布”和“图像分布”之间建立一条**直线路径 (Straight Path)**。

*   **采样步数更少**: 以前需要 50 步，现在 4-8 步就能出极高质量的图。
*   **指令跟随性 (Prompt Adherence)**: 对复杂指令的理解能力大幅提升（Flux 甚至能精准生成文字，这是 SDXL 的弱项）。

## 4. 视频生成：时空压缩 (3D VAE)

视频数据量巨大。Sora 的解法是 **3D VAE**。

*   **时空压缩**: 不仅压缩空间（像素），还压缩时间。把连续 10 帧画面，压缩成 1 帧 Latent。
*   这意味着模型看到的不是“视频”，而是一个个高度浓缩的**时空立方体 (Spacetime Patches)**。

### 物理规律的涌现
模型未被灌输物理公式（没有 `gravity = 9.8`）。
但通过学习海量视频，DiT 在 Latent Space 中**涌现**了物理常识：
*   **物体恒存**: 人走到树后面，不会凭空消失。
*   **流体模拟**: 咖啡倒在桌上会自然铺开。

这证明了：**预测下一个 Frame** $\approx$ **模拟世界运行的规律**。

## 小结

1.  **Diffusion** 是去噪过程。
2.  **DiT** 用 Transformer 取代 U-Net，解决了长时序依赖。
3.  **Flux (Flow Matching)** 是当前的架构最优解，实现了更直的生成路径。
4.  **World Model**: 视频生成不只是做特效，它是通往通用世界模型的必经之路。

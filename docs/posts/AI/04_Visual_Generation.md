# 04. 视觉生成：从 UNet 图片到 DiT 视频

> [!WARNING]
> **这不只是画画**
> 
> 生成式 AI 的视觉能力已经从 2D 静态图进化到了 3D 动态视频。
> 本篇将剖析 **Stable Diffusion (图片)** 和 **Sora/Kling (视频)** 背后的两套核心架构：**U-Net** 与 **DiT**。

## 1. 扩散模型的本质：加噪与去噪

Stable Diffusion 的核心思想源于非平衡热力学。
它包含两个过程：**前向扩散的过程 (Forward)** 和 **逆向去噪的过程 (Reverse)**。
(这部分原理前文已讲，此处略，重点看架构演进)

## 2. 图片霸主：U-Net 架构

Stable Diffusion 使用的是 **U-Net**。
它因为长得像字母 "U" 而得名。

```mermaid
graph TD
    subgraph Encoder [下采样 (Downsampling)]
        L1[Conv + ResNet] --> P1[Pool]
        P1 --> L2[Conv + ResNet] --> P2[Pool]
        P2 --> L3[Conv + ResNet]
    end
    
    subgraph Bottleneck [中间层]
        L3 --> BN[Self-Attention / Cross-Attention]
    end
    
    subgraph Decoder [上采样 (Upsampling)]
        BN --> UP1[UpConv]
        UP1 --> R1[Concat + Conv]
        R1 --> UP2[UpConv]
        UP2 --> R2[Concat + Conv]
    end
    
    L2 -.->|Skip Connection| R1
    L1 -.->|Skip Connection| R2
    
    style U-Net fill:#e1f5fe
```

*   **卷积网络 (CNN)**：U-Net 的核心是卷积层 (Conv)。卷积极其擅长处理局部特征（纹理、边缘）。
*   **归纳偏置 (Inductive Bias)**：CNN 假设像素之间有局部相关性。这对图片很有效。

## 3. 视频新皇：DiT (Diffusion Transformer)

当要生成视频时，U-Net 就力不从心了。
视频不光是连续的图片，它包含**时间维度 (Temporal)** 的连贯性。
Sora, Kling (可灵), Luma 等视频模型，抛弃了 U-Net，全面拥抱 **DiT**。

### 为什么选择 Transformer?
1.  **Patches (切片)**: DiT 把图片/视频切成一个个小方块 (Patches)，就像 GPT 把文字切成 Token。
2.  **Global Attention (全局注意力)**: CNN 只能看局部，Transformer 能看全局。对于视频来说，第 1 帧的物体可能在第 100 帧再次出现，必须有全局视野。
3.  **Scaling Law**:Transformer 已经被证明了，堆越多算力，效果越好（大力出奇迹）。

### DiT 架构图解

```mermaid
graph LR
    Input[视频/图片 Noise] --> Patchify[切分成 Patches]
    Patchify --> Linear[线性投影 (Embedding)]
    Linear --> Transformer[标准 Transformer Block<br/>(Self-Attention + MLP)]
    Transformer --> Unpatchify[还原成像素]
    Unpatchify --> Output[生成结果]
    
    Condition[文本 Prompt / 物理规律] -.->|Cross-Attention| Transformer
```

### 3D VAE：时空压缩
生成视频的数据量太大了（1分钟视频 = 1440 帧图片）。
所以 Sora 使用了 **3D VAE**。
*   不仅在空间上压缩（把 1080p 压成小图）。
*   还在**时间上压缩**（把连续 10 帧压成 1 帧 Latent）。
这意味着 DiT 处理的不是“视频”，而是高度浓缩的“时空立方体”。

## 4. 物理世界模拟器

为什么说视频生成是“物理模拟器”？
因为 DiT 没有任何关于“重力”、“碰撞”的预设代码。
但通过学习海量视频，它**涌现**出了物理常识：
*   扔出的球会画抛物线。
*   水倒在桌子上会流开。
*   这是因为在 Latent Space 中，它学会了 $s_{t+1} = f(s_t, physics)$ 的隐式规律。

## 小结

视觉生成的演进路线：
1.  **Pixel Space -> Latent Space**: 引入 VAE，解决计算量问题。
2.  **U-Net (CNN) -> DiT (Transformer)**: 引入 Transformer，解决时空长程依赖问题。

现在的视频模型，本质上是一个**懂得物理规律的图形渲染引擎**。

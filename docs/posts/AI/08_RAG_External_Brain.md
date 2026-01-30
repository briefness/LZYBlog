# 08. RAG：向量检索与重排序算法详解

> [!NOTE]
> **从应用到内核**
> 
> 前一篇 RAG 文章讲了流程。这一篇本文拆解内核，探讨：
> *   高维向量的距离计算数学原理。
> *   为什么线性搜索太慢？**HNSW 索引算法**详解。
> *   **Cross-Encoder vs Bi-Encoder** 的架构差异与重排序 (Re-ranking) 策略。

## 1. 向量相似度数学原理

RAG 的核心是“找相似”。在数学上，就是计算两个向量在多维空间中的距离。

设查询向量为 $\mathbf{q}$，文档向量为 $\mathbf{d}$，两者都是 $n$ 维向量。

### 余弦相似度 (Cosine Similarity)
最常用的度量。它关注的是向量的**方向**，而不是长度。

$$ \text{similarity} = \cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|} = \frac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_{i=1}^{n} q_i^2} \sqrt{\sum_{i=1}^{n} d_i^2}} $$

*   值域 $[-1, 1]$。1 表示方向完全相同，0 表示正交（无关），-1 表示相反。
*   适用于文本语义检索，因为文本长度（向量模长）通常不影响语义核心。

### 欧几里得距离 (L2 Distance)
关注两点之间的**直线距离**。

$$ d(\mathbf{q}, \mathbf{d}) = \|\mathbf{q} - \mathbf{d}\| = \sqrt{\sum_{i=1}^{n} (q_i - d_i)^2} $$

*   需要事先归一化 vectors，否则长文本（模长大的向量）会受惩罚。

## 2. 向量索引：近似最近邻 (ANN) 算法

如果有 100 万个文档，每次查询都遍历计算 100 万次余弦相似度（KNN, K-Nearest Neighbors），速度会极慢。
这需要 **ANN (Approximate Nearest Neighbor)** 算法：牺牲一点点精度，换取极快的速度。

### HNSW (Hierarchical Navigable Small World)
目前业界最强的向量索引算法。

**通俗类比：高铁站 vs 公交站**
*   **Linear Search**: 像坐公交车。从第 1 站坐到第 100 站，一站站停。太慢。
*   **HNSW**: 建立了**多级交通网络**。
    *   **Layer 2 (高铁)**: 只有几个大站（北京、上海、广州）。先飞到离目的地最近的大站（比如到了上海）。
    *   **Layer 1 (地铁)**: 从上海站坐地铁，到了静安区（范围缩小）。
    *   **Layer 0 (单车)**: 在静安区骑车找具体的门牌号（精确搜索）。

通过这种“跳跃式”逼近，原本需要遍历 100 万次，现在可能只要跳 5-6 次就能找到邻居。

*   **复杂度**：从线性 $O(N)$ 降到了对数级 $O(\log N)$。

## 3. 检索架构：Bi-Encoder vs Cross-Encoder

检索通常分为两步：**召回 (Retrieval)** 和 **精排 (Re-ranking)**。这两步使用了不同的模型架构。

### 3.1 Bi-Encoder (双编码器) - 用于召回
*   **架构**：两个独立的 BERT 模型（可以共享参数）。
*   **计算**：
    *   Document 预先运算成向量 $\mathbf{d}$ 存库。
    *   Query 实时运算成向量 $\mathbf{q}$。
    *   计算 $\mathbf{q} \cdot \mathbf{d}$ (点积)。
*   **优点**：速度极快。适合在海量数据中快速捞出 Top 100。
*   **缺点**：Query 和 Document 没有深层交互，只能捕获粗粒度语义。

### 3.2 Cross-Encoder (交叉编码器) - 用于精排
*   **架构**：单个 BERT 模型。
*   **输入**：将 Query 和 Document 拼接在一起：`[CLS] Query [SEP] Document [SEP]`。
*   **计算**：让 Self-Attention 机制同时处理 Query 和 Doc 的所有 Token。
*   **输出**：一个 0-1 之间的相关性分数。
*   **优点**：精度极高。全量的 Attention 交互能捕获复杂的逻辑关系。
*   **缺点**：速度慢。无法预计算，必须实时 Inference。

### 工业界标准流程 (Pipeline)

```mermaid
graph TD
    Query[用户提问]
    
    subgraph Stage1 [第一阶段: 快速召回]
        Bi[Bi-Encoder / 向量索引]
        KW[BM25 / 关键词搜索]
    end
    
    subgraph Stage2 [第二阶段: 精准重排]
        Cross[Cross-Encoder (Re-ranker)]
    end
    
    Query --> Bi --> Top100[粗排 Top 100]
    Query --> KW --> Top100
    
    Top100 --> Cross --> Top5[精排 Top 5]
    
    Top5 --> LLM[大模型 Prompt]
```

## 4. Chunking (切分) 策略

切分不光是 `split('\n')`。不同的策略直接影响检索效果。

1.  **Fixed-size (固定大小)**：
    *   比如每 500 tokens 切一段，重叠 (Overlap) 50 tokens。
    *   问题：可能把一句话腰斩切断，丢失语义。

2.  **Semantic Chunking (语义切分)**：
    *   计算相邻句子的 Embedding 相似度。
    *   如果相似度突降（说明话题转换了），就在这里切一刀。

3.  **Recursive Character (递归字符)**：
    *   这是 LangChain 默认策略。
    *   优先按 `\n\n` 切，切出来太大就按 `\n` 切，还大就按 `.` 切。
    *   尽可能保留段落结构的完整性。

## 小结

要想 RAG 效果好，不能只靠 LLM，功夫在诗外：
1.  **嵌入模型**：选择 MTEB 榜单分数高的 Embedding 模型。
2.  **索引算法**：理解 HNSW 的图结构。
3.  **精排机制**：引入 Cross-Encoder 把关，大幅提升 Top 1 准确率。
4.  **切分策略**：保证语义块的完整性。

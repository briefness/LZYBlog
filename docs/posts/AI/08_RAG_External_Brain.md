# 08. RAG：向量检索与重排序算法详解

> [!NOTE]
> **从应用到内核**
> 
> 前文跑通了 RAG 的基本流程。这里我们拆解内核：
> *   高维向量的距离计算。
> *   HNSW 索引算法原理。
> *   Cross-Encoder vs Bi-Encoder 的架构差异。
> *   **GraphRAG**：如何用知识图谱解决“全库归纳”难题。

## 1. 向量相似度数学原理

RAG 的核心是相似度匹配。在数学上，就是计算两个向量在多维空间中的距离。

设查询向量为 $\mathbf{q}$，文档向量为 $\mathbf{d}$，两者都是 $n$ 维向量。

### 余弦相似度 (Cosine Similarity)
最常用的度量。关注向量的**方向**，而非长度。

$$ \text{similarity} = \cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|} = \frac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_{i=1}^{n} q_i^2} \sqrt{\sum_{i=1}^{n} d_i^2}} $$

*   值域 $[-1, 1]$。1 表示方向相同，0 表示正交（无关），-1 表示相反。
*   适用于文本语义检索，因为文本长度（向量模长）通常不影响语义核心。

### 欧几里得距离 (L2 Distance)
关注两点之间的**直线距离**。

$$ d(\mathbf{q}, \mathbf{d}) = \|\mathbf{q} - \mathbf{d}\| = \sqrt{\sum_{i=1}^{n} (q_i - d_i)^2} $$

*   **注意**：使用 L2 距离前必须对向量做归一化 (L2 Normalization)，否则长文本（模长大的向量）会被判定为不相似。

## 2. 向量索引：HNSW 算法

如果库里有 100 万个文档，暴力计算 100 万次余弦相似度（KNN）太慢。
需要 **ANN (Approximate Nearest Neighbor)** 算法：牺牲微小的精度，换取数量级的速度提升。

### HNSW (Hierarchical Navigable Small World)
目前业界标准的向量索引算法。

**原理：多级跳表**
*   **Layer 2 (高速路)**: 只有几个关键节点。
*   **Layer 1 (主干道)**: 节点变多，范围缩小。
*   **Layer 0 (毛细血管)**: 包含所有节点，做精确搜索。

查询时，先在顶层找到最近的节点，然后下沉到下一层继续找。
通过这种“跳跃式”逼近，原本 $O(N)$ 的复杂度降到了 $O(\log N)$。

## 3. 检索架构：Bi-Encoder vs Cross-Encoder

检索通常分为两步：**召回 (Retrieval)** 和 **精排 (Re-ranking)**。

### 3.1 Bi-Encoder (双编码器) - 用于召回
*   **架构**：两个独立的 BERT 模型（通常共享参数）。
*   **机制**：Query 和 Document 分别计算向量，然后算点积。
*   **优点**：速度极快。Document 向量可以预计算存库。
*   **缺点**：语义交互浅，精度一般。

### 3.2 Cross-Encoder (交叉编码器) - 用于精排
*   **架构**：单个 BERT 模型。
*   **机制**：输入 `[CLS] Query [SEP] Document [SEP]`，全量 Attention 交互。
*   **优点**：精度极高。能捕获复杂的逻辑关系。
*   **缺点**：慢。必须实时推理，无法预计算。

### 3.3 Late Interaction (ColBERT) - 折中方案
*   **机制**：Jina AI 和 ColBERT 采用的方案。保留 Token 级别的向量（MaxSim 操作），而不是把整个文档压成一个向量。
*   **优势**：兼顾了 Bi-Encoder 的预计算速度和 Cross-Encoder 的细粒度交互。

### 工业界标准 Pipeline

```mermaid
graph TD
    Query[用户提问]
    
    subgraph Stage1 [召回: Top 100]
        Bi[向量检索 (HNSW)]
        KW[关键词检索 (BM25)]
    end
    
    subgraph Stage2 [精排: Top 5]
        Cross[Cross-Encoder (Re-ranker)]
    end
    
    Query --> Bi & KW
    Bi & KW --> Top100[混合召回结果]
    Top100 --> Cross --> Top5
    Top5 --> LLM
```

## 4. Chunking (切分) 策略

切分直接影响检索效果。

1.  **Fixed-size**：每 500 tokens 切一段。简单粗暴，容易切断语义。
2.  **Semantic Chunking**：计算相邻句子的相似度。如果相似度突降（话题转换），就在这里切分。
3.  **Recursive Character**：LangChain 默认。优先按 `\n\n` 切，再按 `\n` 切，最后按标点切。

## 5. RAG 的未来：GraphRAG

传统 RAG 有一个致命缺陷：**无法回答全局性问题**。
比如问：“这 100 篇文档主要在讨论什么趋势？” 传统 RAG 只会检索出几块具体的碎片，瞎子摸象。

**GraphRAG (微软)** 引入了知识图谱：

1.  **实体抽取**：用 LLM 所有的 Person, Org, Location 抽出来，建成图 (Entities & Relationships)。
2.  **社区发现 (Community Detection)**：使用 **Leiden 算法** 发现图中的紧密群体（比如“AI 伦理社区”、“芯片制造社区”）。
3.  **层级摘要**：对每个社区生成摘要。

**查询流程**：
*   **Local Search**: 查具体的节点。
*   **Global Search**: 查社区摘要。

GraphRAG 大幅解决了“全库归纳”问题，虽然构建成本（Token 消耗）高，但对复杂知识库是降维打击。

## 小结

1.  **HNSW** 是向量数据库的基石。
2.  **Cross-Encoder Re-ranking** 是提升准确率性价比最高的手段。
3.  **GraphRAG** 正在将 RAG 带入结构化数据的新时代。

# 08. RAG：向量检索与重排序算法详解

当你的知识库有 100 万条文档时，如何让 LLM 精准命中用户提问？答案是向量检索与重排序。

本文拆解 RAG 内核：
* 高维向量的距离计算原理
* HNSW 索引算法如何将 $O(N)$ 复杂度降到 $O(\log N)$
* Bi-Encoder / Cross-Encoder / ColBERT 的架构差异与选型权衡
* **HyDE**：用假答案引导检索
* **GraphRAG**：如何用知识图谱解决"全库归纳"难题
* 3 个常见陷阱与规避方法

## 1. 向量相似度数学原理

RAG 的核心是相似度匹配。在数学上，就是计算两个向量在多维空间中的距离。

设查询向量为 $\mathbf{q}$，文档向量为 $\mathbf{d}$，两者都是 $n$ 维向量。

### 余弦相似度 (Cosine Similarity)

最常用的度量。关注向量的**方向**，而非长度。

$$ \text{similarity} = \cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|} = \frac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_{i=1}^{n} q_i^2} \sqrt{\sum_{i=1}^{n} d_i^2}} $$

* 值域 $[-1, 1]$。1 表示方向相同，0 表示正交（无关），-1 表示相反。
* 适用于文本语义检索，因为文本长度（向量模长）通常不影响语义核心。

### 欧几里得距离 (L2 Distance)

关注两点之间的**直线距离**。

$$ d(\mathbf{q}, \mathbf{d}) = \|\mathbf{q} - \mathbf{d}\| = \sqrt{\sum_{i=1}^{n} (q_i - d_i)^2} $$

**注意**：使用 L2 距离前必须对向量做归一化（L2 Normalization），否则长文本（模长大的向量）会被判定为不相似。

### 权衡：选择哪种距离度量？

| 场景 | 推荐度量 | 原因 |
|------|---------|------|
| 语义相似度检索 | 余弦相似度 | 关注方向，不受长度影响 |
| 聚类 / 分类任务 | 欧几里得距离 | 关注绝对位置差异 |
| 需要归一化向量 | 两者皆可 | 归一化后等价 |

## 2. 向量索引：HNSW 算法

如果库里有 100 万个文档，暴力计算 100 万次余弦相似度（KNN）太慢。需要 **ANN (Approximate Nearest Neighbor)** 算法：牺牲微小的精度，换取数量级的速度提升。

### HNSW (Hierarchical Navigable Small World)

目前业界标准的向量索引算法。

**原理：多级跳表**

* **Layer 2 (高速路)**：只有几个关键节点，用于快速定位大致区域
* **Layer 1 (主干道)**：节点变多，范围缩小
* **Layer 0 (毛细血管)**：包含所有节点，做精确搜索

查询时，先在顶层找到最近的节点，然后下沉到下一层继续找。通过这种"跳跃式"逼近，原本 $O(N)$ 的复杂度降到了 $O(\log N)$。

**权衡：精度 vs 速度**

HNSW 有两个关键参数：
* `ef_construction`：构建时的候选集大小。值越大，索引越精确，但构建越慢
* `ef_search`：查询时的候选集大小。值越大，召回越精确，但查询越慢

典型配置：ef_construction = 200, ef_search = 100。在速度和精度之间取得平衡。

## 3. 检索架构：Bi-Encoder vs Cross-Encoder

检索通常分为两步：**召回 (Retrieval)** 和 **精排 (Re-ranking)**。

### 3.1 Bi-Encoder (双编码器) - 用于召回

* **架构**：两个独立的 BERT 模型（通常共享参数）
* **机制**：Query 和 Document 分别计算向量，然后算点积
* **优点**：速度极快。Document 向量可以预计算存库
* **缺点**：语义交互浅，精度一般

### 3.2 Cross-Encoder (交叉编码器) - 用于精排

* **架构**：单个 BERT 模型
* **机制**：输入 `[CLS] Query [SEP] Document [SEP]`，全量 Attention 交互
* **优点**：精度极高，能捕获复杂的逻辑关系
* **缺点**：慢，必须实时推理，无法预计算

### 3.3 Late Interaction (ColBERT) - 折中方案

Jina AI 和 ColBERT 采用的方案。保留 Token 级别的向量（MaxSim 操作），而不是把整个文档压成一个向量。

**优势**：兼顾了 Bi-Encoder 的预计算速度和 Cross-Encoder 的细粒度交互。

**权衡**：ColBERT 的向量存储是 Bi-Encoder 的 N 倍（每个 Token 一个向量），需要更多的存储空间和内存。

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

BM25 是关键词检索的经典算法，与向量检索形成互补。两者混合召回（RRF 融合）通常比单一方案效果更好。

## 4. HyDE (Hypothetical Document Embeddings)

传统的向量检索是用 Query 去匹配 Document 向量。但 Query 和 Document 的语义分布往往不同。

**HyDE 的核心思想**：让 LLM 先根据 Query 生成一个"假答案"，然后用这个假答案的向量去检索。

### 工作流程

1. **生成假答案**：用 LLM 根据用户问题生成一个假设性的回答
2. **向量化假答案**：将假答案通过 Bi-Encoder 编码成向量
3. **检索相似文档**：用假答案向量在向量库中检索相似文档
4. **返回真实文档**：将检索到的真实文档返回给 LLM

### 为什么有效？

假答案虽然可能包含错误信息，但它与真实文档处于同一语义空间。相比直接用 Query 向量检索，假答案向量通常能更好地捕捉文档的写作风格和内容结构。

**权衡**：HyDE 需要额外的 LLM 调用（生成假答案），会增加延迟和 Token 消耗。如果对延迟敏感，谨慎使用。

**适用场景**：
* Query 表述模糊时（用户不知道如何准确描述需求）
* Query 和 Document 语义分布差异大时
* 复杂的多跳问题

## 5. Chunking (切分) 策略

切分直接影响检索效果。

1. **Fixed-size**：每 500 tokens 切一段。简单，但容易切断语义
2. **Semantic Chunking**：计算相邻句子的相似度。如果相似度突降（话题转换），就在这里切分
3. **Recursive Character**：LangChain 默认。优先按 `\n\n` 切，再按 `\n` 切，最后按标点切

**权衡：chunk_size 的选择**

| chunk_size | 优点 | 缺点 |
|-----------|------|------|
| 太大 (> 1024 tokens) | 保留完整上下文 | 丢失细粒度，Top-K 稀释有效信息 |
| 太小 (< 256 tokens) | 细粒度精准 | 丢失上下文，关系割裂 |
| 适中 (512-768 tokens) | 平衡 | 需要反复调参 |

建议从 512 tokens 开始，根据召回效果迭代调整。

## 6. RAG 的未来：GraphRAG

传统 RAG 有一个致命缺陷：**无法回答全局性问题**。

比如问："这 100 篇文档主要在讨论什么趋势？" 传统 RAG 只会检索出几块具体的碎片。

**GraphRAG (微软)** 引入了知识图谱：

1. **实体抽取**：用 LLM 所有的 Person, Org, Location 抽出来，建成图（Entities & Relationships）
2. **社区发现 (Community Detection)**：使用 **Leiden 算法** 发现图中的紧密群体（比如"AI 伦理社区"、"芯片制造社区"）
3. **层级摘要**：对每个社区生成摘要

**查询流程**：
* **Local Search**：查具体的节点
* **Global Search**：查社区摘要

GraphRAG 解决了"全库归纳"问题，但构建成本（Token 消耗）高。对简单知识库是过度工程，对复杂知识库是必要投资。

## 7. 常见陷阱 (Common Pitfalls)

### 陷阱一：混合召回返回空结果

**问题**：向量检索和关键词检索的 RRF 融合，如果其中一个返回空，整个结果可能异常。

**规避**：
* 使用 `min(1, count(results))` 作为 RRF 分母
* 检查向量数据库是否正常，索引是否构建
* 设置兜底策略：单一检索模式失败时回退到备选方案

### 陷阱二：chunk_size 不匹配模型上下文窗口

**问题**：Top-K 检索返回的文档总长度超过了 LLM 的上下文窗口容量，导致截断或 OOM。

**规避**：
* 计算 `sum(chunk_size for k in Top_K) <= context_window * 0.8`
* 预留 20% 空间给 system prompt 和对话历史
* 根据 LLM 调整 chunk_size 和 Top-K 的组合

### 陷阱三：向量检索质量差但难以察觉

**问题**：Bi-Encoder 的检索错误通常是"看起来合理但实际不对"，难以通过人工 QA 发现。

**规避**：
* 建立 eval 数据集，定期跑召回率 (Recall@K)
* 监控 Cross-Encoder 的 Re-ranking 分数分布
* 记录检索失败的 Case，持续优化

## 小结

1. **HNSW** 是向量数据库的基石，参数调优在精度和速度间权衡
2. **Cross-Encoder Re-ranking** 是提升准确率性价比最高的手段
3. **HyDE** 适合 Query 表述模糊的场景，但增加延迟
4. **GraphRAG** 解决全局性问题，但构建成本高
5. **chunk_size** 和 **Top-K** 需要根据实际场景迭代调整

## References

1. Karpukhin, V., et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. *EMNLP 2020*.
2. Khattab, O., & Zaharia, M. (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction. *SIGIR 2020*.
3. Gao, L., & Callan, J. (2021). Unsupervised Corpus Aware Language Model Pre-training for Dense Passage Retrieval. *ACL 2021*.
4. Gao, L., et al. (2023). Precise Zero-Shot Dense Retrieval without Contrastive Learners. *arXiv:2309.03440* (HyDE).
5. Edge, D., et al. (2024). From Local to Global: A GraphRAG Approach to Query-Focused Summarization. *Microsoft Research*.
6. Malkov, Y. A., & Yashunin, D. (2018). Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. *IEEE TPAMI*.

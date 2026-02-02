# 11. 质量控制：LLMOps 与 Ragas 评测体系

> [!NOTE]
> **避免主观臆断**
> 
> 众多 AI 项目止步于 Demo 阶段，归因于无法量化效果。调整 Prompt 后性能可能出现波动。
> 需要科学的 **Evaluation (评测)** 体系。

## 1. 为什么 LLM 评测这么难？

传统的软件测试：`assert add(1, 1) == 2`。非黑即白。
LLM 测试：`assert chat("你好") == ???`。它是概率生成的，甚至含义相同但措辞不同。

通常有三种评测方法：
1.  **基于规则 (Rule-based)**: 检查是否包含关键字、JSON 格式是否合法。
2.  **基于模型 (Model-based)**: 用一个更强的模型 (GPT-4) 去给小模型打分。
3.  **基于人 (Human)**: 即 Chatbot Arena 模式，准确度最高但成本昂贵。

## 2. RAG 专属评测：Ragas 框架

对于 RAG 应用，业界有一套标准的 Metrics，称为 **RAG Triad (RAG 三元组)**。

### 核心指标
1.  **Faithfulness (忠实度)**:
    *   Answer 是否忠实于 Retrieved Context？
    *   检测：幻觉。如果 Answer 里说了 Context 里没提到的事，扣分。
2.  **Answer Relevancy (回答相关性)**:
    *   Answer 是否回答了 User Question？
    *   检测：答非所问。
3.  **Context Precision (上下文精度)**:
    *   Retrieved Context 是否真的包含有用的信息？
    *   检测：垃圾检索。

### Ragas 计算原理
Ragas (Retrieval Augmented Generation Assessment) 是一个使用 LLM 作为裁判的开源库。

比如计算 **Faithfulness**：
1.  让 LLM 从 Answer 中提取由事实陈述组成的 Statements $S$。
2.  对于每个 $s \in S$，检查它是否能被 Context 推导出来。
3.  $F = \frac{|S_{supported}|}{|S_{total}|}$

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

results = evaluate(
    dataset=my_dataset, # 包含 question, answer, contexts
    metrics=[faithfulness, answer_relevancy],
)
print(results)
# {'faithfulness': 0.92, 'answer_relevancy': 0.85}
```

## 3. LLMOps：生产环境的监控

上线不是结束，是开始。
你需要监控以下指标：

*   **Trace (链路追踪)**: 使用 LangSmith 或 LangFuse。记录每一次 LLM 调用，包括 Latency, Token Usage, Cost。
*   **Feedback (用户反馈)**: "点赞/点踩" 反馈机制至关重要。这是最真实的线上数据 (RLHF 的来源)。
*   **Red Teaming (红队测试)**: 专门攻击模型，看它会不会输出有害内容（Prompt Injection, Jailbreak）。

## 4. 完整的开发闭环

一个成熟的 AI 团队的工作流应该是这样的：

```mermaid
graph TD
    Dev[开发 Prompt/RAG] --> Evaluator[离线评测 (Ragas)]
    Evaluator -- 分数低 --> Dev
    Evaluator -- 分数高 --> Prod[生产环境上线]
    
    Prod --> Trace[LangSmith 监控]
    Prod --> User[用户反馈]
    
    Trace --> Dataset[构建新数据集]
    User --> Dataset
    
    Dataset --> FineTuning[微调 LoRA]
    FineTuning --> Dev
```

此即 **Data Flywheel (数据飞轮)**。

## 小结

Demo 依赖灵感，产品依赖体系。
1.  **Ragas** 提供了量化 RAG 质量的数学工具。
2.  **LLM-as-a-Judge** 是目前自动化测试的主流方案。
3.  **LLMOps** 保证了系统的可观测性和持续进化。

至此，已涵盖从原理 (Math) 到应用 (Agent) 再到运维 (Ops) 的全链路知识。
最后一篇将展望 AGI 的未来。

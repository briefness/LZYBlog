# 11. 质量控制：LLMOps 与 Ragas 评测体系

> [!NOTE]
> **拒绝玄学调参**
> 
> 众多 AI 项目死于 Demo 阶段，因为无法量化效果。改了一个 Prompt，A 场景好了，B 场景崩了。
> 你需要科学的 **Evaluation (评测)** 体系。

## 1. 为什么 LLM 评测这么难？

传统的软件测试：`assert add(1, 1) == 2`。非黑即白。
LLM 测试：`assert chat("你好") == ???`。它是概率生成的，甚至含义相同但措辞不同。

通常有三种评测方法：
1.  **基于规则 (Rule-based)**: 检查是否包含关键字、JSON 格式是否合法。
2.  **基于模型 (Model-based)**: 用一个更强的模型 (GPT-4) 去给小模型打分。
3.  **基于人 (Human)**: 即 Chatbot Arena 模式，准确度最高但成本极高。

## 2. RAG 专属评测：Ragas 框架

对于 RAG 应用，业界有一套标准的 **RAG Triad (RAG 三元组)** 指标。

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

### DeepEval：更像单元测试的框架
除了 Ragas，**DeepEval** 是另一个优秀的选择。它提供了类似 PyTest 的体验，不仅能测 RAG，还能测 Agent 的多轮对话能力。

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_answer_relevancy():
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="What if these shoes don't fit?",
        actual_output="We offer a 30-day full refund at no extra cost."
    )
    assert_test(test_case, [answer_relevancy_metric])
```

## 3. LLMOps：生产环境监控

上线不是结束，是开始。
需要监控以下指标：

*   **Trace (链路追踪)**: 使用 **LangSmith** 或 **LangFuse**。记录每一次 LLM 调用，包括 Latency, Token Usage, Cost。
*   **Prompt Management**: Prompt 是代码，需要版本控制。不要把 Prompt 硬编码在 Python 里，使用 LangSmith Hub 管理 Prompt 版本。
*   **Feedback (用户反馈)**: "点赞/点踩" 反馈是金矿。这是最真实的线上数据 (RLHF 的来源)。
*   **Red Teaming (红队测试)**: 专门攻击模型，看它会不会输出有害内容（Prompt Injection, Jailbreak）。

## 4. 完整的开发闭环

一个成熟的 AI 团队的工作流应该是这样的：

```mermaid
graph TD
    Dev[开发 Prompt/RAG] --> Evaluator[离线评测 (Ragas/DeepEval)]
    Evaluator -- 分数低 --> Dev
    Evaluator -- 分数高 --> Prod[生产环境上线]
    
    Prod --> Trace[LangSmith 监控]
    Prod --> User[用户反馈]
    
    Trace --> Dataset[构建新数据集]
    User --> Dataset
    
    Dataset --> FineTuning[微调 LoRA]
    FineTuning --> Dev
```

此即 **Data Flywheel (数据飞轮)**。没有评价体系，飞轮就转不起来。

## 小结

1.  **Ragas / DeepEval** 提供了量化 RAG 质量的数学工具。
2.  **LLM-as-a-Judge** 是目前自动化测试的主流方案。
3.  **LLMOps** (LangSmith) 保证了系统的可观测性和持续进化。

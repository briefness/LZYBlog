# 12. 推理模型：System 2 与强化学习 (DeepSeek R1 / o1)

> [!NOTE]
> **慢思考的力量**
> 
> 在 2024 年底，AI 界发生了一次范式转移。OpenAI o1 和 DeepSeek R1 的出现，标志着 LLM 从“快思考 (System 1)”进入了“慢思考 (System 2)”时代。
> 它们的特点是：**在回答之前，先进行长达数秒甚至数分钟的思考链 (Chain of Thought)。**

## 1. System 1 vs System 2

心理学家卡尼曼在《思考，快与慢》中提出：
*   **System 1 (快思考)**: 直觉、本能。比如“2+2=?”，脱口而出。传统的 LLM (GPT-4) 就是这种，它只是在做 Next Token Prediction。
*   **System 2 (慢思考)**: 逻辑、推理。比如“17 x 24 = ?”，需要一步步算。Reasoning Model 就是这种。

**区别**：
*   传统 LLM: `Input -> Answer`
*   推理模型: `Input -> <think>...长长的推理过程...</think> -> Answer`

## 2. 核心技术：强化学习 (RL)

DeepSeek R1 的训练未采用人工标注数据 (SFT)，而是主要依赖 **Reinforcement Learning (RL)**。

### GRPO (Group Relative Policy Optimization)
DeepSeek R1 的核心技术。它解决了一个根本问题：**推理过程很难标注**。
人工检查 AI 几千步的解题步骤，成本高昂且容易出错。

GRPO 采用了 **Outcome Supervision (结果监督)**：
*   **仅关注结果，不关注过程**。
*   数学题答案客观唯一，规则简单。
*   **群体验证**：让模型对同一题生成 64 个不同的解题过程。
    *   如果其中 5 个过程算出了正确答案，这 5 个过程就会受到奖励（强化）。
    *   模型将自动分析：得高分的过程具备何种特征（如多做了一次验算）。
    *   模型逐渐习得“自我反思”和“验算”等行为，因为这些行为能提高算对的概率。

因此 R1 无需人类教导如何思考，而是在几万亿次的自我博弈中，**涌现**出了思考能力。

通过这种大规模的自我博弈 (Self-Play)，模型学会了：
*   **自我反思**: “等等，这一步好像算错了，我重新算一下。”
*   **多角度尝试**: “这个方法行不通，换个思路。”

这也就是在 DeepSeek R1 的输出里经常看到的：`Wait, let me double check...`。

## 3. 为什么 CoT (思维链) 这么重要？

第 03 篇曾提及 CoT。但在 R1/o1 这里，CoT 不再是 Prompt 技巧，而是**训练目标**。

**Compute-Optimal Inference**:
过往观点认为，模型参数越大越聪明（Scaling Law）。
现研究发现，**推理时间越长越聪明 (Test-time Scaling)**。
只要给模型足够的时间去 `<think>`，一个小模型 (R1-Distill-7B) 也能在数学/代码任务上击败 GPT-4o。

## 4. 实战：如何使用推理模型？

多数 API (如 OpenAI, DeepSeek) 会隐藏 `<think>` 内容，仅给最终答案。但对于开发者，看到思考通过程非常重要。

```python
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[{"role": "user", "content": "9.11 和 9.8 哪个大？"}]
)

# 获取思考过程 (DeepSeek 特有字段)
print(response.choices[0].message.reasoning_content)
# 输出: "首先比较整数部分...都是9...然后比较小数部分...0.11 vs 0.8..."

# 获取最终答案
print(response.choices[0].message.content)
# 输出: "9.8 更大"
```

## 小结

推理模型的出现，标志着 AI 开始具备了**元认知 (Metacognition)** —— 也就是“对思考的思考”。
1.  **System 2**: 慢思考让 AI 攻克了复杂的逻辑和数学难题。
2.  **RL & Self-Play**: 只要有明确的验证规则（如数学答案、代码编译器），模型就能自我进化，不再依赖人类数据。
3.  **未来的方向**: 可能会出现思考时间长达几天几夜的模型，去解决癌症攻克、核聚变等人类科学难题。

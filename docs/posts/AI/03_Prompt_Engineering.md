# 03. 提示工程背后的原理：In-Context Learning

> [!NOTE]
> **Prompt 不是咒语**
> 
> 很多教程把 Prompt 讲成玄学。其实 Prompt Engineering 的有效性是有严格的学术支撑的。
> 它的学名叫 **In-Context Learning (ICL, 上下文学习)**。

## 1. ICL: 不需要梯度的“训练”

传统的微调 (Fine-tuning) 需要更新权重 $w$。
而 ICL 是在不改变 $w$ 的情况下，通过改变输入 $x$ 的 Context，激发模型内部已有的能力。

**数学直觉**：
Transformer 的 Attention 机制，本质上是在做**隐式的梯度下降**。
当提供 few-shot examples 时：
`User: apple -> red, banana -> yellow`
Attention Head 会捕获到 `input -> color` 这种映射模式 (Induction Head)，并把这种模式复制到当前的查询上。

## 2. 为什么 Chain-of-Thought (CoT) 有效？

$$ P(Answer | Question) < P(Answer | Reasoning, Question) $$

对于复杂逻辑，直接跳到 Answer 的概率路径 (Probability Path) 可能非常狭窄且崎岖。
CoT 强行插入了中间步骤 $Reasoning$。
每一句 reasoning 都在**收缩解空间 (Search Space)**，引导 Probability Mass 集中到正确的区域。

这就好比过河。直接跳过去（Zero-shot）很容易掉水里。CoT 就是在河中间放了几个垫脚石。

## 3. Attention Heads 的分工

研究发现，Transformer 内部不同的 Head 有明确分工：
*   **Name Mover Heads**: 负责把上文中出现的人名搬运到下文。
*   **Induction Heads**: 负责识别 `A -> B` 的模式，并预测下一个 A 后面也是 B。

好的 Prompt (结构化、举例) 其实是在辅助这些 Head 更容易地提取特征。

## 4. 实战：怎么写 Prompt 才好用？(CO-STAR 框架)

懂了原理后，来看怎么写。
仅有“Role + Task”是不够的。目前新加坡政府科技局提出的 **CO-STAR** 框架是非常好用的实践标准：

| 维度 | 英文 | 解释 | 例子 |
| :--- | :--- | :--- | :--- |
| **C** | **Context** | 背景信息 | "为了准备马拉松，正在制定饮食计划..." |
| **O** | **Objective** | 核心目标 | "帮生成一份一周的午餐食谱..." |
| **S** | **Style** | 写作风格 | "像一位专业的运动营养师，用鼓励的语气..." |
| **T** | **Tone** | 语调情感 | "幽默一点，不要太死板..." |
| **A** | **Audience** | 目标读者 | "给完全不懂烹饪的程序员看..." |
| **R** | **Response** | 输出格式 | "用 Markdown 表格，列出：食材、热量、做法。" |

### 进阶技巧：结构化提示词 (Structured Prompting)

对于复杂的企业级应用，不要写小作文，要写**伪代码**。
Claude 和 Antigravity 尤其喜欢这种 XML 风格：

```markdown
# Role
You are an expert Copywriter.

# Context
<product_details>
  Name: SuperVacuum X
  Price: $299
  Features: Wireless, 500W suction
</product_details>

# Task
Write a landing page headline.

# Constraints
- No more than 10 words.
- Must include the word "Clean".
- Output format: JSON.
```

这种写法利用了 LLM 对编程语言缩进和符号的敏感性，能让幻觉变少很多。

## 5. 终极技：Metaprompting (让 AI 写 AI)

不需要自己想破头。可以用第一性原理，让 AI 帮忙写 Prompt。

**Prompt 生成器模版**：
> "我是一个[职业]，我想做[任务]。
> 请作为 Prompt Engineering 专家，把这个简单的需求，改写成符合 CO-STAR 框架的完美 Prompt。
> 请通过提问来补全没提供的信息。"

这叫 **Interactive Metaprompting**。给它 60 分的输入，它吐出 100 分的 Prompt 工件。

## 小结

*   **Few-Shot** 利用了 Induction Heads 的复制能力。
*   **CoT** 利用了概率空间的逐步收敛特性。
*   写 Prompt 不是为了讨好 AI，而是为了**适配 Transformer 的注意力机制**。

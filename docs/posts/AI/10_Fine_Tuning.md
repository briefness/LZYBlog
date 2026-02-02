# 10. 模型微调：PEFT 与 LoRA 数学原理

> [!NOTE]
> **RAG 的尽头是 Fine-tuning**
> 
> RAG 就像给参加开卷考试的学生发了教科书。但若学生逻辑混乱，即便持有教科书也难以理解。
> 此时需引入 **Fine-tuning (微调)**：通过特训调整模型参数。
> 本篇核心：**Full Fine-tuning vs PEFT**，以及 **LoRA** 的矩阵分解数学原理。

## 1. 为什么需要微调？

*   **注入特定格式**：Prompt 难以确保 100% 稳定性，而微调能实现定向格式约束。
*   **注入隐性知识**：诸如医疗行业的隐性规则，难以文档化，但可通过大量病例数据微调学会。
*   **降低成本**：微调一个 7B 的小模型，在特定任务上性能常优于未微调的 GPT-4。

## 2. 全量微调 (Full Fine-tuning) vs PEFT

*   **FFT (Full Fine-tuning)**: 更新模型的所有参数（比如 70 亿个）。
    *   **缺点**：极贵。需要庞大的显存存梯度和优化器状态。容易出现 **Catastrophic Forgetting (灾难性遗忘)**，学了新知识，忘了旧知识。
    *   **优点**：上限最高。

*   **PEFT (Parameter-Efficient Fine-Tuning)**: 只训练一小部分参数。
    *   **Prefix Tuning / P-Tuning**: 在输入前加一串可训练的 embedding。
    *   **LoRA (Low-Rank Adaptation)**: 目前的主流霸主。

## 3. LoRA 数学原理：矩阵的低秩分解

LoRA 的核心观点为：**模型训练时的权重变化量 $\Delta W$ 是“低秩”的。**

假设预训练权重为 $W_0 \in \mathbb{R}^{d \times k}$。
在微调时，冻结 $W_0$，只训练增量 $\Delta W$。
$$ W = W_0 + \Delta W $$

LoRA 假设 $\Delta W$ 可以分解为两个小矩阵的乘积：
$$ \Delta W = B A $$

*   $B \in \mathbb{R}^{d \times r}$
*   $A \in \mathbb{R}^{r \times k}$
*   $r$ 是 **Rank (秩)**，通常选得很小（比如 8, 16, 32）。

**显存节省了多少？**
假设 $d=4096, k=4096, r=8$。
*   FFT 需要训练参数：$4096 \times 4096 \approx 16,000,000$。
*   LoRA 需要训练参数：$4096 \times 8 + 8 \times 4096 = 32,768 + 32,768 \approx 65,000$。
*   **压缩了 250 倍！** 因此单张 4090 显卡即可完成大模型微调。

**前向传播公式**：
$$ h = W_0 x + \Delta W x = W_0 x + B A x $$
训练完后，可以把 $BA$ 乘出来加回 $W_0$，推理时没有任何额外延时。

## 4. 实战：LLaMA-Factory

理论之外，实践层面推荐使用 **LLaMA-Factory**。

### 环境准备
```bash
git clone https://github.com/hiyouga/LLaMA-Factory.git
pip install -r requirements.txt
```

### 数据集准备 (Alpaca 格式)
```json
[
  {
    "instruction": "将这句话翻译成古文",
    "input": "今天天气真好",
    "output": "今日天朗气清"
  }
]
```

### 启动训练 (LoRA)
```bash
python src/train.py \
    --stage sft \
    --model_name_or_path meta-llama/Llama-2-7b-hf \
    --do_train \
    --dataset my_data \
    --finetuning_type lora \
    --lora_rank 8 \
    --lora_alpha 16 \
    --output_dir output/my_lora
```

*   **lora_rank**: 决定了微调的“容量”。简单任务选 8，复杂任务选 64。
*   **lora_alpha**: 缩放因子，通常设为 rank 的 2 倍。

## 小结

微调不再是科研机构的专利。
1.  **LoRA** 通过矩阵分解，降低了大模型微调的门槛。
2.  **LLaMA-Factory** 等工具让微调变成了“配置 config”的工作。
3.  **SFT (Supervised Fine-Tuning)** 是确保模型遵循指令的关键步骤。

掌握微调可构建领域专家模型。下一篇将探讨 **Evaluation (评测)**。

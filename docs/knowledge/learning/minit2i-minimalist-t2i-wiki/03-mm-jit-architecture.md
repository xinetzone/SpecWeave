---
id: "minit2i-wiki-03-architecture"
title: "MM-JiT架构深度解析：回归朴素Transformer"
source: "机器之心技术文章深度分析"
date: "2026-08-03"
category: "learning"
tags: ["MM-JiT", "MM-DiT", "架构设计", "Transformer", "文本适配器"]
---

# MM-JiT架构深度解析：回归朴素Transformer

MM-JiT（Multi-Modal Joint Transformer）是MiniT2I提出的核心架构创新。它不是在现有MM-DiT架构上做增量改进，而是从第一性原理出发重新思考多模态条件注入的方式，最终回归到接近标准预归一化Transformer的极简设计。

---

## 1. MM-DiT vs MM-JiT：8维度架构对比

SD3采用的MM-DiT（Multi-Modal Diffusion Transformer）是当前文生图领域的主流架构范式，其核心条件注入机制为AdaLN。MiniT2I提出的MM-JiT是对这一范式的根本性反思。

| 对比维度 | SD3 MM-DiT（AdaLN范式） | MiniT2I MM-JiT（朴素Transformer范式） |
|----------|-------------------------|----------------------------------------|
| **条件注入哲学** | 异质模态需要专门调制路径，通过AdaLN逐层注入时间步和全局文本 | 所有模态都是token，通过标准联合注意力平等交互，无需专门注入分支 |
| **时间步处理** | 显式时间步嵌入→MLP生成scale/shift/gate→逐层调制 | 隐式从噪声图像统计特征中感知，无显式注入路径（forward签名仅接收x和txt） |
| **文本处理** | 池化文本编码通过AdaLN全局注入；文本token参与联合注意力 | 冻结FLAN-T5-Large→线性投影→2个TextPreambleBlock独立Transformer→双流联合注意力，无全局池化注入 |
| **归一化方式** | LayerNorm + AdaLN仿射调制（scale/shift/gate） | RMSNorm（elementwise_affine=False，无可学习参数）+ QK-Norm（Q/K注意力前额外RMSNorm） |
| **MLP结构** | 标准Transformer MLP（线性→GELU→线性） | SwiGLU MLP（Swish激活+门控机制，w1/w2/w3三矩阵，mlp_ratio=8/3≈2.6667） |
| **位置编码** | 可能使用可学习位置编码 | RoPE旋转位置编码（文本1D RoPE + 图像2D RoPE）+ 图像额外固定2D sincos位置嵌入（不可学习）；文本无额外位置嵌入 |
| **Patch嵌入** | 简单线性投影 | BottleneckPatchEmbed瓶颈结构：stride=patch_size卷积→128维→1x1卷积投影到hidden_size（两层结构） |
| **输出层** | 标准线性投影 | FinalLayer：RMSNorm（无affine）+ 零初始化线性投影（weight/bias初始化为0） |
| **双流结构** | QKV共享/交叉注意力 | 图像文本各自独立QKV投影/MLP/RMSNorm，Q/K/V拼接后联合自注意力再拆分回各自分支，各自独立残差连接 |
| **架构复杂度** | 每个block包含调制MLP和门控机制，结构复杂 | 接近标准预归一化Transformer，结构简洁干净 |
| **参数效率** | AdaLN分支占用部分参数预算 | 节省的参数预算用于增加层数（12→17层，+41.7%） |
| **FID表现** | 基线18.7（相同算力预算） | 13.7（相同算力预算，提升26.7%） |
| **可复用性** | 定制化架构，迁移改进需理解AdaLN细节 | 标准Transformer架构，可直接复用NLP/CV领域成熟技术 |
| **理论假设** | 时间步和全局文本必须通过调制路径注入；图像本身不携带足够的时间步信息 | 噪声图像本身携带时间步信息；文本token通过注意力充分融合即可；逐层调制是冗余的 |

---

## 2. 核心设计一：两层文本适配器

MM-JiT并非盲目地直接拼接文本和图像token——它承认文本与图像特征存在分布差异，但用更轻量、更符合Transformer本质的方式处理这种差异。

### 设计动机

冻结的T5文本编码器输出的特征分布与去噪器主干期望的输入分布存在**域偏移（domain gap）**：
- T5是在大规模文本语料上预训练的语言模型，其特征空间是为语言理解优化的
- 去噪器是在像素空间做流匹配训练的图像生成模型，其特征空间是为图像生成优化的
- 如果直接将T5输出与图像patch token拼接进行联合注意力，可能导致融合效果不佳

### 实现方式

在文本token与图像patch token进入双流联合注意力计算之前，先经过线性投影和两个独立的TextPreambleBlock进行文本预处理：

1. **线性投影层**（txt_embedder）：冻结的FLAN-T5-Large输出维度为1024，通过无bias的线性层投影到与图像分支相同的hidden_size（B/16为768维，L/16为1248维）
2. **2个TextPreambleBlock**：这不是简单的MLP适配器，而是**2个完整的Transformer Block**，每个包含：
   - 自注意力层（仅处理文本token，图像token不参与）
   - SwiGLU MLP层
   - RMSNorm（无affine）+ QK-Norm
   - 1D RoPE位置编码
   - 独立残差连接
3. 这两个纯文本Transformer block专门学习将T5特征空间映射到去噪器的特征空间
4. 图像patch token不经过适配器，直接进入双流联合注意力
5. 预处理后的文本token与图像patch token进入17个双流MMJiTBlock做联合自注意力交互

### 设计考量

| 设计选择 | 考量 |
|---------|------|
| **仅对文本使用适配器** | 图像patch是去噪器直接处理的对象，其特征空间就是去噪器自己的空间；只有文本是"外来者"需要适配 |
| **适配器层数为两层** | 在表达能力（足够完成域对齐）和计算成本（轻量不占用过多预算）之间取得平衡 |
| **T5整体冻结** | T5已经是成熟的文本编码器，冻结可以节省训练显存和计算，避免过拟合，同时适配器提供足够的适配能力 |
| **不使用全局池化注入** | 全局池化会丢失文本的细粒度位置信息；通过token级注意力融合，每个图像patch可以直接关注到相关的文本token |

### 设计本质

> 承认文本特征与图像特征存在分布差异，但不采用全局调制的方式处理这种差异，而是通过轻量级适配层在token进入联合注意力前完成域对齐，随后让两种模态在标准注意力机制下平等交互。

这与AdaLN的哲学形成鲜明对比：AdaLN认为文本条件是"控制信号"，需要"调制"整个网络；MM-JiT认为文本是"语义上下文"，只需要作为"参考资料"让模型在生成时查阅即可。

---

## 3. 核心设计二：删除AdaLN分支

删除AdaLN是MM-JiT最激进也最有争议的设计决策，但它建立在坚实的实验证据和关键洞察之上。

### 删除的组件列表

移除AdaLN意味着从每个Transformer子块中删除以下组件：

| 被删除组件 | 原作用 |
|-----------|--------|
| 时间步嵌入MLP | 将时间步t映射为高维嵌入向量 |
| 文本池化投影MLP | 将池化后的全局文本特征投影到与时间步嵌入相同维度 |
| Scale/Shift/Gate生成MLP | 在每个block中根据时间步+文本嵌入生成调制参数 |
| AdaLN仿射变换 | 用生成的scale和shift对归一化后的特征做仿射变换 |
| 门控机制 | 用gate参数控制残差连接的信息流 |
| 所有相关的专用路径 | 时间步和文本从嵌入层到每个block的专用传递路径 |

### 删除依据

删除AdaLN不是"拍脑袋"决定，而是建立在两个关键洞察之上：

1. **被噪声污染的图像本身携带时间步信息**（详见下节详解）——模型不需要外部告诉它"现在是第几步"，它自己能从输入图像"看"出来
2. **文本信息已经通过适配器+联合注意力充分融合**——文本token就在序列中，每个图像patch在每一层都能通过注意力直接"看到"所有文本token，不需要再通过全局调制路径"广播"一次

---

## 4. 关键洞察详解："被噪声污染的图像本身携带时间步信息"

这是MiniT2I最核心的科学洞见，也是移除AdaLN的理论基础。

### 理论基础：扩散/流匹配前向过程回顾

在扩散模型和流匹配模型中，前向加噪/插值过程遵循统一的形式。对于时间步t∈[0,T]：

**xₜ = √(ᾱₜ)·x₀ + √(1-ᾱₜ)·ε**

其中：
- x₀是干净图像
- ε是高斯噪声
- ᾱₜ是随t单调递减的系数（t=0时ᾱ=1，xₜ=x₀；t=T时ᾱ→0，xₜ→ε）

这意味着xₜ的统计特性随t呈现**规律性、可预测的单调变化**：

| t值（时间步） | 信噪比（SNR） | 图像特征 | 高频成分 |
|--------------|--------------|---------|---------|
| t≈0（早/干净端） | 高 | 清晰的物体轮廓、纹理、细节 | 丰富 |
| t中等 | 中等 | 大尺度结构可见，细节模糊 | 中等 |
| t≈T（晚/噪声端） | 低 | 接近纯噪声，无明显结构 | 极少 |

### 通俗解释

想象你是一个去噪模型：
- 如果输入图像很清晰、有丰富细节、有明显的物体——你知道现在是在去噪的后期，只需要做精细修饰
- 如果输入图像很模糊、只有大尺度色块、细节不可辨——你知道现在是在去噪的中期，需要补充细节
- 如果输入图像基本是噪声、看不出任何结构——你知道现在是在去噪的早期，需要先构建大框架

你不需要有人在旁边告诉你"这是第50步"——你看一眼输入图像的噪声程度就知道了。

Transformer的自注意力机制具有强大的特征提取和模式识别能力，它完全可以从xₜ的这些统计特征中隐式推断出时间步信息。显式通过AdaLN注入时间步嵌入，对于具有足够表达能力的Transformer来说是**冗余**的。

### 对传统设计的反思

这一洞察迫使我们反思：为什么之前的模型都需要AdaLN显式注入时间步？

可能的原因：
1. **历史路径依赖**：扩散模型最早是用UNet做的，UNet的卷积结构局部感受野有限，难以从全局统计特征推断时间步，确实需要显式注入
2. **模型规模较小**：早期DiT模型规模较小（如DiT-S/XL等），表达能力有限，可能确实需要时间步嵌入的"帮助"
3. **没有人尝试移除**：AdaLN被视为"必需组件"，没有人认真做消融实验验证它是否可以去掉

MiniT2I的实验表明，当模型有足够深度（17层）且采用适当架构（文本适配器+联合注意力）时，模型确实可以隐式感知时间步，AdaLN是冗余的。

### 验证意义

这一洞察的意义远不止于"可以省掉AdaLN"：
1. **方法论价值**：它提醒我们，很多"被证明必需"的组件可能只是历史条件下的最优解，当其他条件变化时可能不再必要
2. **架构简化**：移除AdaLN后架构接近标准Transformer，大量NLP/CV领域的Transformer改进（位置编码、高效注意力、初始化策略等）可以直接复用
3. **理论启发**：它暗示生成模型的条件注入机制可能比我们想象的更简单——模型比我们认为的更"聪明"，能自己从数据中学到很多我们以为需要显式设计的东西

---

## 5. 架构简化的量化收益

删除AdaLN分支直接减少了模型参数和计算量，但MiniT2I并未将这部分算力预算"节省"下来，而是将其重新投入到更本质的模型能力扩展中——增加网络深度，实现了"减法变加法"。

| 指标 | 基线（有AdaLN，12层） | MM-JiT（无AdaLN，17层） | 变化幅度 |
|------|------------------------|--------------------------|----------|
| Transformer层数 | 12层 | 17层 | **+41.7%**（+5层） |
| FID分数 | 18.7 | 13.7 | **-26.7%**（FID越低越好，显著提升） |
| 单步计算量 | ~570 GFLOPs（B/16像素空间基线） | 与基线相当（算力预算重新分配） | 计算成本不变 |
| 架构复杂度 | 高（AdaLN调制分支+额外MLP） | 低（接近标准预归一化Transformer） | 大幅简化 |

### 收益分析

1. **深度增加带来表达能力提升**：从12层增加到17层，网络的非线性变换能力和特征抽象层次显著增强，这是FID大幅提升的主要来源
2. **计算预算优化配置**：AdaLN分支的参数和计算被重新分配给更多的Transformer层，展示了"做减法"本身就是"做加法"
3. **可理解性与可修改性提升**：接近标准Transformer的架构意味着研究者可以直接复用Transformer领域的大量成熟技术，降低了后续改进的门槛

---

## 6. MM-JiT架构图

下图完整展示了MM-JiT的架构流程，准确反映双流结构和代码实现细节：

```mermaid
graph TB
    subgraph Input["输入"]
        Text["文本提示<br/>'一只戴着帽子的猫'"]
        Image["噪声图像 xₜ<br/>（携带时间步信息，归一化到[-1,1]）"]
    end

    subgraph TextEncoder["文本编码器（冻结）"]
        T5["FLAN-T5-Large<br/>341M参数，冻结权重<br/>输出1024维文本token"]
        Text --> T5
    end

    subgraph TextPreprocess["文本预处理（可训练）"]
        TxtEmbed["线性投影 txt_embedder<br/>1024 → 768维，无bias"]
        Preamble1["TextPreambleBlock 1<br/>纯文本自注意力+SwiGLU<br/>RMSNorm+QK-Norm+1D RoPE"]
        Preamble2["TextPreambleBlock 2<br/>纯文本自注意力+SwiGLU<br/>RMSNorm+QK-Norm+1D RoPE"]
        T5 --> TxtEmbed --> Preamble1 --> Preamble2
    end

    subgraph PatchEmbed["图像Patch嵌入"]
        Bottleneck["BottleneckPatchEmbed<br/>stride=16卷积→128维→1x1卷积→768维<br/>（瓶颈两层结构，非简单线性）"]
        AddPos["+ 固定2D sincos位置嵌入<br/>（不可学习）"]
        Image --> Bottleneck --> AddPos
    end

    subgraph DoubleStream["双流MMJiTBlock（重复堆叠17次）"]
        direction TB
        BlockIn["Block输入"]
        
        subgraph ImageBranch["图像分支"]
            direction TB
            ImgNorm1["img_norm1: RMSNorm<br/>(elementwise_affine=False)"]
            ImgQKV["img_qkv: Q/K/V投影"]
            ImgQKNorm["q_norm/k_norm: QK-Norm"]
        end
        
        subgraph TextBranch["文本分支"]
            direction TB
            TxtNorm1["txt_norm1: RMSNorm<br/>(elementwise_affine=False)"]
            TxtQKV["txt_qkv: Q/K/V投影"]
            TxtQKNorm["q_norm/k_norm: QK-Norm"]
        end
        
        ConcatQKV["拼接[Q_t;Q_i], [K_t;K_i], [V_t;V_i]<br/>应用多模态RoPE<br/>(文本1D + 图像2D)"]
        JointAttn["联合自注意力计算<br/>(文本图像在同一注意力矩阵中平等交互)"]
        SplitAttn["拆分输出回图像/文本分支"]
        ImgProj["img_attn_proj + 残差"]
        TxtProj["txt_attn_proj + 残差"]
        
        subgraph ImageMLP["图像分支MLP"]
            ImgNorm2["img_norm2: RMSNorm"]
            ImgSwiGLU["img_mlp: SwiGLU MLP<br/>(w1,w2,w3三矩阵+Swish门控)"]
        end
        
        subgraph TextMLP["文本分支MLP"]
            TxtNorm2["txt_norm2: RMSNorm"]
            TxtSwiGLU["txt_mlp: SwiGLU MLP"]
        end
        
        AddImg["+ 残差连接"]
        AddTxt["+ 残差连接"]
        BlockOut["Block输出(x, txt)"]
        
        BlockIn --> ImgNorm1 --> ImgQKV --> ImgQKNorm
        BlockIn --> TxtNorm1 --> TxtQKV --> TxtQKNorm
        ImgQKNorm --> ConcatQKV
        TxtQKNorm --> ConcatQKV
        ConcatQKV --> JointAttn --> SplitAttn
        SplitAttn --> ImgProj --> ImgNorm2 --> ImgSwiGLU --> AddImg
        SplitAttn --> TxtProj --> TxtNorm2 --> TxtSwiGLU --> AddTxt
        ImgProj -->|残差| AddImg
        TxtProj -->|残差| AddTxt
        AddImg --> BlockOut
        AddTxt --> BlockOut
    end
    
    Preamble2 --> DoubleStream
    AddPos --> DoubleStream
    DoubleStream -->|17层重复后，拼接[txt;x]| FinalLayer

    subgraph Output["输出"]
        FinalNorm["FinalLayer: RMSNorm(无affine)"]
        ZeroProj["零初始化线性投影<br/>(weight/bias初始化为0)"]
        Unpatchify["Unpatchify: 像素空间重建"]
        Pred["预测速度 v / 干净图像 x₀<br/>RGB像素空间直接输出"]
        FinalLayer --> FinalNorm --> ZeroProj --> Unpatchify --> Pred
    end

    Note["关键代码实现特点：<br/>❌ 无AdaLN调制分支<br/>❌ 无显式时间步注入（MMJiTBlock.forward仅接收x,txt）<br/>❌ 无全局文本池化注入<br/>✅ 2个TextPreambleBlock纯文本预处理<br/>✅ 双流独立QKV/MLP/Norm，拼接后联合注意力再拆分<br/>✅ RMSNorm(无affine) + QK-Norm<br/>✅ SwiGLU MLP (mlp_ratio=8/3)<br/>✅ RoPE位置编码(1D文本+2D图像)+固定sincos<br/>✅ BottleneckPatchEmbed瓶颈结构<br/>✅ CFG通过attention mask置零实现<br/>✅ FinalLayer零初始化"]

    style TextPreprocess fill:#cce5ff
    style DoubleStream fill:#ccffcc
    style Note fill:#fff4cc

    linkStyle default stroke-width:2px
```

> **架构代码解读**：MM-JiT的设计可以概括为"冻结FLAN-T5-Large编码 → 线性投影到768维 → 2个TextPreambleBlock纯文本Transformer预处理 → 图像经过BottleneckPatchEmbed+固定sincos位置嵌入 → 17层双流MMJiTBlock（各自独立QKV/MLP/Norm，拼接后联合自注意力再拆分，各自残差）→ FinalLayer零初始化输出"。没有AdaLN、没有特殊的条件注入路径、没有复杂的门控机制——所有交互都通过Transformer最本质的自注意力机制完成，归一化使用RMSNorm+QK-Norm，MLP使用SwiGLU，位置编码使用RoPE。

---

## 7. 代码级实现细节

基于官方JAX/Flax代码仓库的精确实现分析（`models/mmjit.py`、`models/dit_blocks.py`、`diffusion.py`）：

### 7.1 精确模型配置参数

| 模型 | Patch | hidden_size | txt_hidden | depth_double | num_heads | head_dim | mlp_ratio | txt_preamble_depth | 去噪器参数量 |
|------|-------|-------------|------------|--------------|-----------|----------|-----------|-------------------|-------------|
| **MiniT2I-B/32** | 32 | 768 | 768 | 17 | 12 | 64 | 8/3≈2.6667 | 2 | ~260M |
| **MiniT2I-B/16** | 16 | 768 | 768 | 17 | 12 | 64 | 8/3≈2.6667 | 2 | **258M** |
| **MiniT2I-M/16** | 16 | 1024 | 1024 | 22 | 16 | 64 | 8/3≈2.6667 | 2 | ~591M |
| **MiniT2I-L/16** | 16 | 1248 | 1248 | 23 | 24 | 52 | 2.7 | 2 | **914M** |
| **MiniT2I-XL/16** | 16 | 1536 | 1536 | 33 | 24 | 64 | 8/3≈2.6667 | 2 | ~1.99B |

> 文本编码器固定使用 **google/flan-t5-large**（341M参数，完全冻结），输出维度为1024，通过txt_embedder线性投影到txt_hidden_size。B/16总参数约600M（258M去噪器+341M文本编码器），L/16总参数约1.25B。

### 7.2 双流自注意力机制详解

MMJiTBlock的双流结构是真正的"双流联合自注意力"而非交叉注意力：

```python
# 代码核心逻辑（简化自mmjit.py:60-100）
def __call__(self, x, txt):  # 注意：没有t参数！
    # 1. 图像和文本各自独立归一化+QKV投影
    qkv_i = self.img_qkv(self.img_norm1(x))    # 图像分支
    qkv_t = self.txt_qkv(self.txt_norm1(txt))  # 文本分支
    
    # 2. Q/K分别做RMSNorm（QK-Norm技术）
    q_i, k_i, v_i = split_qkv(qkv_i); q_t, k_t, v_t = split_qkv(qkv_t)
    q_i, k_i = self.q_norm(q_i), self.k_norm(k_i)
    q_t, k_t = self.q_norm(q_t), self.k_norm(k_t)
    
    # 3. 拼接后做联合自注意力（关键！）
    q = concat([q_t, q_i], axis=1)  # 文本在前，图像在后
    k = concat([k_t, k_i], axis=1)
    v = concat([v_t, v_i], axis=1)
    q, k = self.rope(q, k, txt_len=L_txt)  # 多模态RoPE
    attn_out = softmax(q @ k.T / sqrt(d)) @ v
    
    # 4. 拆分回各自分支 + 独立输出投影 + 残差
    out_t = self.txt_attn_proj(attn_out[:, :L_txt])
    out_i = self.img_attn_proj(attn_out[:, L_txt:])
    x = x + out_i; txt = txt + out_t  # 各自残差
    
    # 5. 各自独立SwiGLU MLP + 残差
    x = x + self.img_mlp(self.img_norm2(x))
    txt = txt + self.txt_mlp(self.txt_norm2(txt))
    return x, txt
```

**关键理解**：
- 图像和文本有**完全独立**的归一化层、QKV投影、注意力输出投影、MLP层——参数不共享
- 但在注意力计算的核心步骤，Q/K/V被拼接在一起，在同一个注意力矩阵中做**联合自注意力**（文本token可以关注图像patch，图像patch也可以关注文本token，文本token之间也互相关注，图像patch之间也互相关注——所有token完全平等交互）
- 注意力输出后再拆分回两个分支，各自通过独立的投影层和残差连接
- 这不是交叉注意力（Cross-Attention，一个模态做Q，另一个做K/V），而是真正的**联合自注意力**（Joint Self-Attention）

### 7.3 RMSNorm与QK-Norm

代码使用`TorchRMSNorm`且`elementwise_affine=False`：
- **RMSNorm**（Root Mean Square Layer Normalization）：仅用均方根做归一化，不减去均值，计算更简单
- `elementwise_affine=False`：**没有可学习的scale(γ)和shift(β)参数**，纯粹做归一化变换
- **QK-Norm**：在计算注意力分数之前，对Q和K分别额外做一次RMSNorm，这是近年来被证明可以稳定训练、改善注意力的技术

### 7.4 SwiGLU MLP

不使用标准Transformer的MLP（线性→GELU→线性），而是使用SwiGLU：
```python
# 代码来自dit_blocks.py:241-253
class SwiGLUMlp(nn.Module):
    def setup(self):
        self.w1 = Linear(in_features, hidden_dim, bias=False)  # 门控分支
        self.w3 = Linear(in_features, hidden_dim, bias=False)  # 输入分支
        self.w2 = Linear(hidden_dim, in_features, bias=False)  # 输出投影
    
    def __call__(self, x):
        return self.w2(silu(self.w1(x)) * self.w3(x))  # Swish激活 + 门控
```
- 使用三个权重矩阵而非两个
- 激活函数为SiLU/Swish（`x * sigmoid(x)`）
- 通过门控机制（`silu(w1(x)) * w3(x)`）控制信息流
- mlp_ratio默认是8/3≈2.6667，而非标准Transformer的4，因为SwiGLU更参数高效
- hidden_dim会向上取整到8的倍数以支持模型分片

### 7.5 RoPE旋转位置编码

- **文本**：使用1D RoPE（TextRotaryEmbedding1D），这是LLaMA等大语言模型采用的标准位置编码
- **图像**：使用2D RoPE（VisionRotaryEmbeddingFast），分别对高度和宽度方向应用旋转位置编码
- **多模态RoPE**（MultiModalRotaryEmbeddingFast）：自动对前缀文本token应用1D RoPE，对后缀图像patch应用2D RoPE
- **图像额外位置嵌入**：图像patch在进入Transformer前，还会加上**固定的2D sincos位置嵌入**（不可学习，来自MAE），加到patch嵌入后；文本没有这个额外位置嵌入，仅靠RoPE

### 7.6 BottleneckPatchEmbed瓶颈结构

不是简单的线性投影，而是两层卷积的瓶颈结构：
```python
# 代码来自dit_blocks.py:39-71
class BottleneckPatchEmbed(nn.Module):
    def setup(self):
        self.proj1 = Conv(pca_channels=128, kernel_size=patch_size, strides=patch_size, use_bias=False)
        self.proj2 = Conv(hidden_size, kernel_size=(1,1), strides=(1,1), use_bias=bias)
    
    def __call__(self, x):
        return self.proj2(self.proj1(x))  # 先投影到128维，再到768维
```
- 第一层：stride=patch_size（如16）的卷积，同时完成patch切分和第一次投影，输出128维（pca_channels）
- 第二层：1x1卷积，投影到最终的hidden_size（如768）
- 这种瓶颈结构可能比单层线性投影有更好的特征提取能力

### 7.7 零初始化输出层（FinalLayer）

```python
# 代码来自dit_blocks.py:16-36
class FinalLayer(nn.Module):
    def setup(self):
        self.norm_final = norm_layer(hidden_size, elementwise_affine=False)
        self.linear = Linear(hidden_size, patch_size*patch_size*out_channels, 
                           weight_init=ZEROS, bias_init=ZEROS)  # 零初始化！
```
- 最后一层RMSNorm同样无affine参数
- 输出线性层的weight和bias都**初始化为0**
- 训练初期模型输出为0，相当于从"恒等映射"（输出就是输入的噪声x_t）开始训练，这是一种稳定训练的技巧

### 7.8 CFG实现方式：Attention Mask置零

Classifier-Free Guidance不是通过传入空文本实现，而是通过将文本注意力mask置零：
```python
# 代码来自diffusion.py:121-147
def cfg_wrapped_net(self, cfg_scale):
    def net_cfg(x, t, y, m):
        combined = concat([x, x], axis=0)  # 复制batch
        y = concat([y, y], axis=0)
        m_null = zeros_like(m)              # 关键：mask置零！
        m = concat([m, m_null], axis=0)     # 一份有文本，一份mask=0
        out = self(combined, t, y, m)
        cond, uncond = split(out, 2, axis=0)
        return uncond + (cond - uncond) * cfg_scale  # CFG外推
```
- `m_null = zeros_like(m)`：无条件分支的注意力mask全为0
- 在MMJiT中，被mask为0的token会被替换为mask_token（初始化为很小的值），相当于"关闭"了文本条件
- label_drop_rate=0.1：训练时10%概率随机将文本mask置零，训练无条件生成能力用于CFG

### 7.9 训练目标与采样（来自diffusion.py）

- **v-prediction流匹配**：预测速度v = x - noise，而非噪声ε或x0
- **前向过程（代码形式）**：`x_t = t * x + (1 - t) * noise`，注意这里t=0是纯噪声，t=1是干净数据，与常见扩散定义相反
- **noise_scale=2.0**：噪声是标准差为2的高斯分布（`noise ~ N(0, 2²)`），不是标准正态
- **LogNormal时间步采样**：t~LogNormal(mu=-0.8, sigma=0.8)，经sigmoid映射到[0,1]，不是均匀采样
- **损失函数**：简单MSE L2 loss
- **采样器**：默认100步Euler ODE求解器，支持Heun（二阶）和SDE采样；支持Mean Flow蒸馏到4步（在mean_flow_distill分支）
- **训练分辨率**：512×512（image_size=512），图像归一化到[-1, 1]

---

← [上一章](02-three-subtractions.md) | [下一章：实验结果与性能](04-experiments-performance.md) →

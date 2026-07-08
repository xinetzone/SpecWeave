---
id: "myst-example-paper-template"
title: "模板：学术论文模板"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/paper-template.toml"
---
# 基于注意力机制的图像分类方法研究

> 使用说明：复制本模板到你的项目，替换所有占位符，删除注释即可。配套 `references.bib` 见文末。

---

## 摘要

近年来，深度学习在计算机视觉领域取得了显著进展，但卷积神经网络在建模长距离依赖关系方面仍存在局限。本文提出一种新型注意力增强网络（Attention-Augmented Network, AANet），通过引入自注意力机制捕获图像全局上下文信息。在 CIFAR-10 和 ImageNet 数据集上的实验结果表明，所提方法相比基线模型准确率分别提升 2.3% 和 3.1%，同时保持了推理效率。本研究为视觉任务中的长距离依赖建模提供了新的思路。

**关键词**：深度学习；注意力机制；图像分类；卷积神经网络

---

## 1 引言

图像分类是计算机视觉的基础任务，在自动驾驶、医学影像分析等领域有广泛应用。卷积神经网络（CNN）通过局部感受野和权值共享取得了巨大成功 {cite:p}`he2016deep`，但其固有局部性限制了对全局信息的建模能力。

受 Transformer 在 NLP 领域成功的启发 {cite:t}`vaswani2017attention`，本文探索将自注意力机制引入视觉任务。主要贡献如下：

1. 提出轻量级注意力模块，可嵌入现有 CNN 架构
2. 设计多尺度注意力融合策略，兼顾局部与全局信息
3. 在多个基准数据集上验证了方法的有效性

## 2 相关工作

### 2.1 卷积神经网络

从 AlexNet 到 ResNet，CNN 通过加深网络和残差连接不断提升性能 {cite}`he2016deep`。但卷积操作的感受野有限，需通过堆叠多层扩大感受野。

### 2.2 注意力机制

注意力机制允许模型动态关注重要区域。SENet 提出通道注意力，CBAM 结合空间与通道注意力，但这些方法仍未充分建模长距离像素依赖。

### 2.3 Vision Transformer

ViT 将图像拆分为 patch 序列输入 Transformer，但需大规模预训练才能取得好效果。本文方法结合 CNN 的局部特征提取能力与 Transformer 的全局建模能力。

## 3 方法

### 3.1 整体架构

如 {numref}`fig-architecture` 所示，AANet 由骨干网络、注意力模块和分类头三部分组成。

% 实际使用时替换为你的图片路径
% ```{figure} figs/architecture.png
% :label: fig-architecture
% :alt: AANet 架构图
% :width: 90%
% :align: center
%
% 图：AANet 整体架构，包含 CNN 骨干、注意力模块和分类头。
% ```

（此处插入架构图）

### 3.2 自注意力模块

给定输入特征图 {math}`X \in \mathbb{R}^{H \times W \times C}`，我们计算查询、键、值矩阵：

````markdown
```{math}
:label: eq-attention

\begin{align}
Q &= XW_Q, \quad K = XW_K, \quad V = XW_V \\
\text{Attention}(Q,K,V) &= \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\end{align}
```
````

其中 {math}`W_Q, W_K, W_V \in \mathbb{R}^{C \times d_k}` 为可学习投影矩阵，{math}`d_k` 为键维度。

### 3.3 多尺度融合

为处理不同尺度目标，我们在多个层级插入注意力模块，特征融合方式为：

````markdown
```{math}
:label: eq-fusion

F_{out} = \alpha F_{local} + (1 - \alpha) F_{global}
```
````

其中 {math}`\alpha` 为可学习平衡参数，初始化为 0.5。

````markdown
```{admonition} 命题 1
:class: theorem
:label: prop-convergence

当 {math}`\alpha \in [0,1]` 时，融合特征 {math}`F_{out}` 的表达能力不弱于单一分支。
```
````

````markdown
```{admonition} 证明
:class: proof

当 {math}`\alpha=1` 时退化为局部分支，{math}`\alpha=0` 时退化为全局分支，因此命题成立。∎
```
````

## 4 实验

### 4.1 实验设置

- **数据集**：CIFAR-10（5万训练/1万测试）、ImageNet-1K（128万训练/5万测试）
- **优化器**：AdamW，学习率 3e-4，权重衰减 1e-4
- **训练轮次**：CIFAR-10 训练 200 epochs，ImageNet 训练 100 epochs
- **基线模型**：ResNet-50、SENet、CBAM

### 4.2 主要结果

实验结果如 {numref}`tab-main-results` 所示，所提方法在两个数据集上均取得最优性能。

````markdown
```{table} 各模型在 CIFAR-10 和 ImageNet 上的分类准确率（%）
:label: tab-main-results
:align: center

| 模型 | CIFAR-10 | ImageNet Top-1 | 参数量(M) |
|------|:--------:|:--------------:|:---------:|
| ResNet-50 | 93.6 | 76.1 | 25.6 |
| SENet | 94.1 | 77.4 | 28.1 |
| CBAM | 94.3 | 77.8 | 28.1 |
| **AANet (Ours)** | **95.9** | **80.5** | **26.3** |
```
````

### 4.3 消融实验

为验证各模块有效性，我们进行消融实验：

% ```{figure} figs/ablation.png
% :label: fig-ablation
% :width: 85%
% :align: center
%
% 图：消融实验结果。
% ```

（此处插入消融实验图）

## 5 结果与讨论

从 {numref}`tab-main-results` 可以观察到：

1. 引入注意力机制后模型性能普遍提升，验证了全局信息的重要性
2. AANet 在参数量仅增加 0.7M 的情况下取得显著提升，说明方法高效
3. 训练过程中 {math}`\alpha` 最终收敛到约 0.6，表明局部特征略重要但全局信息不可或缺

## 6 结论

本文提出了 AANet，通过自注意力机制增强 CNN 的全局建模能力。实验证明该方法在多个基准上取得优异结果，且参数量开销小。未来工作将探索把该方法扩展到目标检测和语义分割任务。

---

## 参考文献

% 需要在 myst.yml 中配置 bibliography: references.bib

````markdown
```{bibliography}
:style: unsrt
```
````

---

## 配套 references.bib 示例

将以下内容保存为 `references.bib`，与论文源文件放在同一目录：

```bibtex
@inproceedings{he2016deep,
  author    = {He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing and Sun, Jian},
  title     = {Deep Residual Learning for Image Recognition},
  booktitle = {Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2016},
  pages     = {770--778},
  doi       = {10.1109/CVPR.2016.90}
}

@article{vaswani2017attention,
  author  = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Lukasz and Polosukhin, Illia},
  title   = {Attention Is All You Need},
  journal = {Advances in Neural Information Processing Systems (NeurIPS)},
  year    = {2017},
  volume  = {30},
  doi     = {10.48550/arXiv.1706.03762}
}

@inproceedings{hu2018squeeze,
  author    = {Hu, Jie and Shen, Li and Sun, Gang},
  title     = {Squeeze-and-Excitation Networks},
  booktitle = {CVPR},
  year      = {2018},
  doi       = {10.1109/CVPR.2018.00745}
}
```

---

## myst.yml 配置示例

```yaml
project:
  title: 基于注意力机制的图像分类方法研究
  bibliography: references.bib
  exports:
    - format: pdf
      template: lapreprint
      output: paper.pdf
      pdf:
        engine: xelatex
        fonts:
          main: "Times New Roman"
          cjk: "SimSun"
```

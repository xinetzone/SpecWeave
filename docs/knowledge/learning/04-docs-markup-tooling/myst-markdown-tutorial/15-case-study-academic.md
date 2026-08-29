---
id: "myst-tutorial-case-academic"
title: "第15章：实战案例 - 学术论文与书籍"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/15-case-study-academic.toml"
---
# 第15章：实战案例 - 学术论文与书籍

本章通过学术论文写作案例，展示 MyST 在科研写作中的完整能力：数学公式、参考文献、交叉引用、多格式导出。配套模板见 [examples/paper-template.md](examples/paper-template.md)。

:::{tip}
**学习目标**：完成本章后能够使用 MyST 撰写符合出版规范的学术论文，支持 PDF/LaTeX/Word 多格式导出。
:::

## 15.1 案例背景

学术写作对排版精度要求极高：数学公式编号对齐、BibTeX 参考文献、图表公式自动编号引用、多格式导出。MyST 原生支持上述所有需求，无需在 Word/LaTeX/Markdown 之间反复切换。

## 15.2 学术写作结构

### 15.2.1 标准论文结构

```yaml
---
title: 论文标题
authors:
  - name: 作者1
    affiliations: [aff1]
    corresponding: true
    email: author1@xxx.edu
affiliations:
  - id: aff1
    institution: XX大学
    department: 计算机科学系
keywords: [关键词1, 关键词2]
abstract: |
  摘要内容...
---

# 1 引言
# 2 相关工作
# 3 方法
# 4 实验
# 5 结果与讨论
# 6 结论
# 参考文献
# 附录（可选）
```

### 15.2.2 技术书籍结构

- 章节（Part/Chapter/Section）层级清晰
- 附录：补充证明、数据集、代码
- 术语表：使用 `{glossary}` 指令
- 索引：术语索引（mystmd 自动生成）

## 15.3 数学公式实战

### 15.3.1 行内与块级公式规范

行内公式用于简单表达式：损失函数为 {math}`\mathcal{L}(\theta) = \frac{1}{N}\sum_{i=1}^N \ell(f(x_i;\theta), y_i)`。

块级公式用于重要结论，**必须加标签**：

````markdown
```{math}
:label: eq-bayes

P(A|B) = \frac{P(B|A) P(A)}{P(B)}
```
````

引用：贝叶斯定理见 {eq}`eq-bayes`。

### 15.3.2 多公式对齐（align 环境）

使用 LaTeX `align` 环境，`&` 标记对齐位置：

````markdown
```{math}
:label: eq-softmax

\begin{align}
\sigma(z)_i &= \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}} \\
\frac{\partial \sigma(z)_i}{\partial z_k} &= \sigma(z)_i (\delta_{ik} - \sigma(z)_k)
\end{align}
```
````

其中 {math}`\delta_{ik}` 是克罗内克函数。某行不编号在行末加 `\nonumber`。

### 15.3.3 定理/证明环境

使用 `{admonition}` 模拟：

````markdown
```{admonition} 定理 1（收敛性）
:class: theorem
:label: thm-convergence

若目标函数 {math}`f` 满足 L-平滑条件，则梯度下降以 {math}`O(1/\sqrt{T})` 速率收敛。
```
````

引用：如 {numref}`定理 %s <thm-convergence>` 所示。证明环境用 `:class: proof`，结尾加 ∎。

:::{note}
Sphinx 用户可用 `sphinx-proof` 扩展提供的 `{prf:theorem}` 等专业指令。
:::

## 15.4 参考文献管理

### 15.4.1 BibTeX 文件组织

创建 `references.bib`：

```bibtex
@article{vaswani2017attention,
  author  = {Vaswani, Ashish and others},
  title   = {Attention Is All You Need},
  journal = {NeurIPS},
  year    = {2017},
  doi     = {10.48550/arXiv.1706.03762}
}
```

引用键推荐「作者年份关键词」风格，如 `vaswani2017attention`。

### 15.4.2 cite 变体使用场景

| Role | 示例效果 | 使用场景 |
|------|---------|---------|
| `{cite:p}` | (Vaswani et al., 2017) | 引用作为括号补充 |
| `{cite:t}` | Vaswani et al. (2017) | 作者作为句子成分 |
| `{cite}` | [1] | 数字编号（IEEE/GB/T 7714） |

```markdown
Transformer 由 {cite:t}`vaswani2017attention` 提出 {cite:p}`vaswani2017attention`。
多文献引用：{cite:p}`vaswani2017attention,he2016deep`
```

### 15.4.3 bibliography 配置

````markdown
## 参考文献

```{bibliography}
:style: unsrt
```
````

常用样式：`unsrt`（按引用顺序，自然科学常用）、`plain`（字母序）。自定义 CSL（如 GB/T 7714）：

```yaml
project:
  bibliography: references.bib
  csl: https://www.zotero.org/styles/gb-t-7714-2015-numeric
```

BibTeX 中含 `doi` 字段时自动生成可点击链接。

## 15.5 图表编号与引用

### 15.5.1 图（Figure）自动编号

````markdown
```{figure} figs/model-architecture.pdf
:label: fig-architecture
:alt: 模型架构图
:width: 90%
:align: center

图：本研究提出的模型架构。
```
````

引用：`如 {numref}`fig-architecture` 所示` → "如 图 3 所示"；自定义格式：`{numref}`图 %s <fig-architecture>``。

### 15.5.2 表格编号

````markdown
```{table} 各模型准确率对比（%）
:label: tab-results
:align: center

| 模型 | 数据集A | 数据集B |
|------|:-------:|:-------:|
| Baseline | 82.1 | 76.3 |
| Ours | **89.4** | **85.7** |
```
````

引用：`结果见 {numref}`tab-results``。

## 15.6 多格式导出

### 15.6.1 myst.yml 导出配置

```yaml
project:
  title: 我的学术论文
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
    - format: docx
      output: paper.docx
    - format: tex
      output: paper.tex
      template: arxiv
```

### 15.6.2 PDF 导出

```bash
myst build --pdf
```

中文字体要点：使用 XeLaTeX/LuaLaTeX 引擎，CJK 字体设 `SimSun`（宋体）、`SimHei`（黑体）。

### 15.6.3 Word/LaTeX 导出

```bash
myst build --docx   # Word格式投稿/审阅
myst build --tex    # LaTeX格式提交arXiv
```

arXiv 提交要点：使用 `arxiv` 模板，上传时将 `.tex`、`.bib`、图片一起打包。

## 15.7 学术写作最佳实践

### 15.7.1 标签命名规范

统一前缀便于搜索：`fig:`（图）、`tab:`（表格）、`eq:`（公式）、`sec:`（章节）、`thm:`（定理）。

### 15.7.2 交叉引用规范

**正确**：`如 {numref}`fig-arch` 所示`（具体明确）  
**错误**：`如下图所示`（排版后位置变化导致歧义）

### 15.7.3 术语一致性：Substitution

```yaml
myst:
  substitutions:
    CNN: 卷积神经网络
    SOTA: 当前最优（State-of-the-Art）
```

使用：`本文使用 {{CNN}} 提取特征，达到 {{SOTA}} 性能。`

### 15.7.4 协作与版本控制

- Git 管理 `.md` 源文件、`.bib`、图片
- `_build/`、`paper.pdf` 等产物加入 `.gitignore`
- Zotero 导出时保持引用键一致

## 15.8 投稿注意事项

### 15.8.1 双盲匿名化

分离作者信息，创建 `myst-anon.yml` 清空作者字段：

```bash
myst build --pdf --config myst-anon.yml
```

正文中避免自指："我们之前的工作" → "先前工作"。

### 15.8.2 提交前 Checklist

- [ ] 作者信息、单位、邮箱、ORCID 完整
- [ ] 摘要、关键词符合字数要求
- [ ] 所有图表/公式在正文中被引用
- [ ] 参考文献格式符合期刊要求
- [ ] DOI 链接可点击，无拼写错误
- [ ] PDF 字体已嵌入，匿名版无作者信息

:::{important}
**黄金法则**：投稿前从审稿人视角通读——所有引用是否可追溯？图表是否自解释？
:::

## 15.9 小结

- **结构**：论文用摘要/引言/方法/实验/结论/参考文献
- **数学**：`{math}` + `:label:` + `{eq}`，`align` 对齐，admonition 模拟定理环境
- **参考文献**：`.bib` 管理，`{cite:t}`/`{cite:p}` 引用，`bibliography` 生成列表
- **图表**：`{figure}`/`{table}` + `{numref}` 自动编号
- **多格式**：`--pdf`（XeLaTeX+中文字体）、`--docx`、`--tex`（arXiv）
- **投稿**：双盲匿名化，提交前 Checklist

配套模板：[examples/paper-template.md](examples/paper-template.md)

## 导航
[« 上一章：技术文档写作](14-case-study-tech-docs.md) | [返回目录](README.md) | [下一章：常见问题解答 »](16-faq.md)

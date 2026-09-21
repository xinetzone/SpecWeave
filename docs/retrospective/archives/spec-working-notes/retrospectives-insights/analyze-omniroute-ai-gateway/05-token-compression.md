---
id: "analyze-omniroute-ai-gateway-05"
title: "RTK + Caveman token压缩"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 5
created: "2026-07-09"
---

# RTK + Caveman token压缩

## 双重压缩机制

OmniRoute采用双重压缩策略：RTK过滤重复内容 + Caveman规则压缩，两层配合实现高效的token节省。

## 压缩效果

压缩效果显著，可实现15%-95%的token节省。

## 官方示例

官方给出的示例：69 token的React解释可以压缩到19 token，意思保持不变。

## 安全边界

压缩机制有明确的安全边界：代码块、URL、JSON结构保持不动，只压缩冗余的自然语言内容，不会破坏代码和结构化数据的完整性。

## 适用场景

特别适用于经常跑git diff、grep、日志等包含大量重复自然语言内容的场景。

## 作者评价

作者幽默评价："这个没啥用，我都混免费额度了"。

## 质量保证

需要注意的是，压缩只作用于输入内容，模型输出保持不变，因此输出质量不会下降。

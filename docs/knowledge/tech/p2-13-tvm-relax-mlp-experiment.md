---
id: p2-13-tvm-relax-mlp-experiment
title: TVM Relax 前端 MLP 实验记录
source: d:\spaces\chaos\IO\test.ipynb
source_type: file
category: tech
tags:
  - tvm
  - relax
  - mlp
  - nn-module
  - experiment
archive_status: archived
archive_priority: P2
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T12:00:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 IO/test.ipynb、正文为成熟专题提炼、元数据与 tech 分类映射核对通过
summary: TVM Relax 前端 nn.Module API 的最小 MLP 实验，展示从模型定义到 export 导出链路的验证样例，可作为 Relax 前端学习与回归参考。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p2-13-tvm-relax-mlp-experiment.md
archived_at: 2026-08-02T03:27:35Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:27:35Z archived from d:\spaces\chaos\.agents\knowledge\temp\tech\p2-13-tvm-relax-mlp-experiment.md to D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p2-13-tvm-relax-mlp-experiment.md
---

# TVM Relax 前端 MLP 实验记录

## 来源

- 源文件：[IO/test.ipynb](file:///d:/spaces/chaos/IO/test.ipynb)
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`tech`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\tech\`

## 正文摘要

`IO/test.ipynb` 是一个 TVM Relax 前端的最小验证实验，验证 `tvm.relax.frontend.nn` 的模块化建模与导出链路。

### 模型定义

以 `nn.Module` 定义三层 MLP（MNIST 风格 784 → 256 → 10）：

```python
import tvm
from tvm import relax
from tvm.relax.frontend import nn

class MLPModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        return x
```

### 验证要点

- `nn.Module` 子类通过属性赋值嵌套组成模块树
- 实例化后可直接访问 `model.export` 导出能力（Relax 前端将模块导出为可编译 IR）
- 该实验确认了「定义 → 实例化 → export」的最小可用链路，为后续 Relax 前端建模提供回归基准

## 动作边界

本轮为 P2 专题抽样条目。正式归档时以模型定义片段与验证结论为核心正文，不搬运 notebook 的完整输出流与交互会话。

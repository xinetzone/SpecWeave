# samples-retrospective

> apps/samples 目录里程碑复盘产出物（基于七概念方法论编排 R→I→E→A→C 链路）

## 文件清单

| 文件 | 说明 |
|------|------|
| [retrospective-report.md](retrospective-report.md) | 里程碑复盘报告：38条事实 + 3条洞察 + 1个可复用模式 + 6项原子行动项 |
| [tutorial.md](tutorial.md) | 指导教程：示例驱动模式传播 — 6步构建高质量技术示例项目 |

## 复盘范围

| 项目 | 技术栈 | 传播模式 |
|------|--------|----------|
| [cow-demo](../cow-demo/) | C++17 / CMake | 零拷贝COW读写分离 |
| [serial-camera-controller](../serial-camera-controller/) | Python / OpenCV | 三线程分离+自动降级 |
| [short-video-site](../short-video-site/) | HTML/CSS/JS | AI全栈快速原型流程 |
| [zleap-workspace-first-prototype](../zleap-workspace-first-prototype/) | Python | Workspace-first上下文治理 |

## 方法论链路

```
R（复盘：38条事实）→ G1通过
I（洞察：3条四元组）→ G2通过
E（萃取：1个L2模式）→ G3通过
A（原子化：报告+教程）→ 产出物
C（提交：原子交付）→ G4
```

## 关键发现

1. 文档声明与文件实际状态存在脱节（serial-camera 的 docs/ 目录缺失）
2. 测试覆盖率两极分化（2/4项目有系统化测试，2/4项目完全无测试）
3. 示例项目天然具有"模式载体"属性，模式密度比功能完整度更重要

## 核心萃取模式

**示例驱动模式传播**：通过最小可运行实现+多场景演示+双向链接+测试即文档+复盘沉淀的6步法，将抽象架构模式转化为可学习、可复制的代码示例。

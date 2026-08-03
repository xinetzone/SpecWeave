---
id: "animejs-threejs-adapter-wiki-resources"
title: "资源与术语表"
category: "learning"
tags:
  - animejs
  - threejs
  - resources
  - glossary
  - references
date: "2026-08-03"
status: "active"
author: "SpecWeave"
source: "spec:animejs-threejs-adapter-wiki"
---

# 资源与术语表

## 官方资源

以下为 Anime.js 与 Three.js 官方资源链接，建议收藏作为日常开发查阅参考：

- [Anime.js GitHub Release v4.5.0](https://github.com/juliangarnier/anime/releases/tag/v4.5.0) — v4.5 版本发布说明，包含 Three.js 适配器的首次正式发布信息
- [Anime.js 官网](https://animejs.com/) — Anime.js 官方首页，包含示例展示与最新动态
- [Three.js 官网](https://threejs.org/) — Three.js 官方首页，包含示例、文档入口
- [@animejs/three 适配器文档](https://animejs.com/documentation/three) — 适配器官方 API 文档，最权威的使用参考
- [Three.js 官方文档](https://threejs.org/docs/) — Three.js 完整 API 参考手册

## 学习资源推荐

- **原文文章（微信公众号）** — 本教程的原始参考文章，提供了适配器的设计背景与核心思路解读
- [**Anime.js v4 官方文档**](https://animejs.com/documentation/) — Anime.js v4 完整 API 文档，包含核心动画能力的详细说明
- [**Three.js 动画指南**](https://threejs.org/manual/#en/animation) — Three.js 官方手册中的动画章节，讲解原生 Three.js 动画的实现方式
- **Three.js Journey** — 业界推荐的 Three.js 系统教程，由 Bruno Simon 主讲，涵盖从基础到高级的完整 Three.js 知识体系

## 术语表

| 术语（英文） | 中文翻译 | 简明解释 |
|---|---|---|
| Adapter Pattern | 适配器模式 | 一种软件设计模式，将一个类的接口转换成客户端期望的另一个接口，使原本不兼容的类可以协同工作。`@animejs/three` 即通过此模式将 Three.js 对象 API 适配为 Anime.js 可识别的动画目标。 |
| InstancedMesh | 实例化网格 | Three.js 中用于批量渲染大量相同几何体的技术，通过单次绘制调用渲染成千上万个实例，显著提升性能。适配器支持直接对其矩阵属性进行动画。 |
| Stagger | 交错动画 | 让多个元素的动画按顺序依次触发而非同时开始的技术，可产生错落有致的视觉节奏感。适配器扩展了 3D 空间交错能力。 |
| Uniform / Uniform 变量 | Uniform 变量 | WebGL/Shader 中在一次绘制调用中保持不变的全局变量，用于从 JavaScript 向着色器传递颜色、位置、时间等参数。适配器支持直接对其进行动画驱动。 |
| Transform | 变换 | 在 3D 空间中对物体进行位置（position）、旋转（rotation）、缩放（scale）的操作统称，是 3D 动画最基础也最常用的属性类型。 |
| Easing | 缓动 | 控制动画进度随时间变化的曲线函数，决定动画是匀速、加速、减速还是弹性运动，直接影响动画的自然感和质感。 |
| Timeline | 时间线 | Anime.js 中用于编排多个动画顺序、重叠、嵌套关系的核心容器，支持精确控制动画的时间偏移和播放流程。 |
| Interpolation | 插值 | 在两个关键帧值之间计算中间过渡值的过程，动画引擎通过插值算法在每一帧计算出当前应显示的属性值。 |
| requestAnimationFrame | 请求动画帧 | 浏览器提供的专为动画设计的 API，会在下次重绘前调用回调函数，通常与屏幕刷新率同步（约 60fps），是 Web 动画的底层驱动机制。适配器自动管理此循环。 |
| SSOT (Single Source of Truth) | 唯一事实源 | 架构设计原则，确保数据只有一个权威来源，其他模块通过同步获取该来源数据。适配器让 Anime.js 成为动画状态的唯一事实源，Three.js 仅负责渲染。 |
| Property Flattening / 属性扁平化 | 属性扁平化 | 适配器的核心设计之一，将 Three.js 中深度嵌套的属性路径（如 `mesh.position.x`）映射为扁平的键值（如 `x`），简化动画代码编写。 |
| Extended Transforms | 扩展变换 | 适配器在标准 Three.js transform 基础上扩展的 CSS transform 风格属性（如 `translateX`、`rotateY`、`scale`），让前端开发者可以用熟悉的 CSS 思维编写 3D 变换动画。 |
| Shader | 着色器 | WebGL 中运行在 GPU 上的小程序，分为顶点着色器（处理顶点位置）和片元着色器（处理像素颜色），用于实现自定义渲染效果。 |
| Matrix | 矩阵 | 3D 图形学中用于表示物体变换（位置、旋转、缩放）的数学结构，4x4 矩阵可以一次性编码完整的空间变换信息。InstancedMesh 使用矩阵数组存储所有实例状态。 |
| Quaternion | 四元数 | 一种用四元组表示 3D 旋转的数学方式，相比欧拉角（Euler angles）可以避免万向节锁（Gimbal Lock）问题，是 Three.js 内部表示旋转的底层机制。 |

## 项目内相关 Wiki 交叉引用

- [**返回上级目录**](README.md) — 本教程 Wiki 首页
- [**返回教程总览**](00-overview.md) — 第 00 章，教程全貌与章节导航
- [**原始学习分析文档**](../animejs-threejs-adapter-analysis.md) — 本教程的前置学习分析，包含六大痛点、五大核心功能、代码对比与价值分析
- **其他前端相关教程** — 请关注 [05-ai-multimodal-content](../) 目录下其他内容，该目录收录了 AI 多模态与前端创意开发相关的各类 Wiki 教程

## 本教程文件清单

以下是本 Wiki 教程的完整章节文件列表，方便快速导航：

| 章节编号 | 标题 | 文件链接 |
|---|---|---|
| 00 | 教程总览 | [00-overview.md](00-overview.md) |
| 01 | 快速开始 | [01-quickstart.md](01-quickstart.md) |
| 02 | 核心概念 | [02-core-concepts.md](02-core-concepts.md) |
| 03 | 五大核心特性详解 | [03-five-features.md](03-five-features.md) |
| 04 | 实战案例 | [04-practical-examples.md](04-practical-examples.md) |
| 05 | 最佳实践与常见陷阱 | [05-best-practices.md](05-best-practices.md) |
| 06 | 常见问题解答 | [06-faq.md](06-faq.md) |
| 07 | 资源与术语表 | [07-resources.md](07-resources.md) |
| — | 教程首页 | [README.md](README.md) |

---

> 本 Wiki 教程为 Anime.js v4.5 Three.js 适配器的系统性学习资料，建议结合官方文档与实际编码练习同步学习。遇到问题时可先查阅 [第 06 章 常见问题解答](06-faq.md)。

---

> **上一章**：[第 06 章 — 常见问题解答 ←](06-faq.md)  
> **返回**：[教程首页 README](README.md)

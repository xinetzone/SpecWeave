# OKF 知识包集合

本目录是 SpecWeave 项目的 OKF（Open Knowledge Format）知识包集合，采用自包含、自洽的结构化知识格式，每个知识包（bundle）可独立使用、移植和阅读。

## 知识包分类

- [**chaos/** — 跨领域知识包集合](./chaos/index.md)
  - 收录 AI Agent 框架、编译器与深度学习、IoT 与智能家居、人文学术、工具生态等 10 个多样化知识包

## 使用说明

每个知识包的标准结构：
- `concepts/` — 核心概念文档（按学习路径组织，00-overview 为总览）
- `examples/` — 实践示例与快速上手
- `references/` — 事实清单、信源登记、架构洞察等参考资料
- `index.md` — 知识包入口与导航
- `log.md` — 构建变更日志
- `verification-report.md` — 验证报告（经对抗审查通过的知识包）

所有内部链接使用 bundle-relative 路径（以 `/` 开头），可在本地 Markdown 预览器和静态网站中正常工作。

```{toctree}
:maxdepth: 2

chaos/index
```
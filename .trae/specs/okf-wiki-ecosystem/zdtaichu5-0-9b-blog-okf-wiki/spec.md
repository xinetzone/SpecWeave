---
status: "draft"
version: "1.0"
source: "https://mp.weixin.qq.com/s/YOW4mB8Dg6loiKDfzF_NHQ?from=industrynews&color_scheme=light#rd"
---

# ZDTaichu5.0-9B 博文 → OKF Wiki 教程 Spec

## 内容敏感度预检

源文是无访问控制的微信公众号公开文章，按公开内容处理。规划位于 `.trae/specs/`，知识包落入 `projects/awesome-okf-xs/doc/bundles/`。

## 方法论编排

- 场景：知识沉淀
- 链路：`R → I → E → V`
- G1：事实与作者判断分层
- G2：洞察包含证据、边界与影响
- G3：模式可迁移到其他具身模型评估
- V：对官方报告值、独立复现性和部署边界进行对抗审查

## 骨架与归属

文章是技术综述/资讯盘点，不含版本化安装、配置、输入输出和实测步骤，因此不设 `examples/`。主线实体是 ZDTaichu5.0-9B，落入现有 `sheke/industry/` 行业与技术分析分组；不新建分组。

## 事实登记摘要

- F-001～F-018：文章元信息、模型定位、能力、训练管线、场景和作者判断。
- F-019～F-024：官方 Blog/GitHub/Hugging Face 核验补充。
- 基准分数和“超过闭源模型”属于官方发布值，尚未找到独立复现实验，正文降级为“官方报告”。

## 产出

- `zdtaichu5-0-9b/index.md`
- `concepts/00-model-and-release.md`
- `concepts/01-spatial-reasoning-and-training.md`
- `concepts/02-embodied-deployment-boundaries.md`
- `references/article-source.md`
- `references/verification.md`
- `log.md`
- 更新行业分组索引与 bundles 总索引

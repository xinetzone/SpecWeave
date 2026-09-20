---
type: spec
title: OpenMontage Agent 视频制作系统 OKF Wiki
source: https://mp.weixin.qq.com/s/Icq2rjqPi7gfVb-x7cCz8Q
status: complete
---

# OpenMontage Agent 视频制作系统 OKF Wiki

## 内容敏感度

微信公众号页面为公开文章，无 `code`、`token` 或登录访问控制参数，采用公开内容工作流。产出进入 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

- 场景：知识沉淀
- 链路：R（事实采集）→ I（知识拆分与洞察）→ E（信源先行生成）→ V（对抗审查与门禁）
- G1：事实与作者判断分离。
- G2：每条核心洞察包含现象、证据、反常识和工程建议。
- G3：模式可迁移到其他 Agent 生产系统。
- G4：安装示例、流水线示例和审核清单均可独立验证。

## 归属位置

| 候选位置 | 判定 | 理由 |
| --- | --- | --- |
| `jishu/ai/agent-platform-notes/` | 选定 | 文章主线是 Agent 编排平台，现有分组已收录多个独立平台散篇 |
| 新建 `openmontage/` 分组 | 排除 | 单篇文章不新建顶级分组 |
| `jishu/viz/` | 排除 | 重点不是渲染引擎源码，而是 Agent 驱动的视频生产系统 |

## 骨架判定

文章包含 `git clone`、`make setup`、环境依赖、示例提示词、流水线阶段和输出审查，因此两个可复现性问题均为“是”，建立 `examples/`。

## 交付物

- `references/article-source.md`：文章事实登记，F-001 起编号。
- `references/verification.md`：GitHub 官方源核验、口径差异与证据边界。
- `concepts/`：系统定位、流水线架构、工程治理三层知识。
- `examples/`：最小安装路径与创作请求设计。
- `index.md`、`log.md`：导航与维护记录。

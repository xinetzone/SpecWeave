# Oracle 博文 → OKF Wiki 知识包转化规格

## 任务来源

- 用户指令：使用 seven-concepts-cmd 方法论编排，学习微信公众号文章并生成 OKF wiki 教程
- 场景：知识沉淀（R→I→E→V→C），执行 blog-article-to-okf-wiki 七阶段工作流
- 信源：《太炸裂了！这是哪个大佬发现的 CodeX这个神仙用法，居然能将gpt-plus发挥到极致！》
  - 公众号「Leon学AI」，原创，2026-08-30 21:45 发布于广东
  - URL: https://mp.weixin.qq.com/s/_J1BzyqyoNWuj_998DLo1g
  - 正文 1684 字，无图片信息含量、无超链接（URL 为纯文本），话题标签 #codex教程

## 敏感度预检

公开内容（无 code/token/邀请码参数）→ 标准工作流：spec 落本目录，bundle 落 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-agent/oracle/`。

## 归属决策

| 候选位置 | 判定 | 理由 |
|---|---|---|
| jishu/ai/ai-agent（✅ 采纳） | 主线实体 | Oracle 是被 Coding Agent 调用的 CLI+MCP 工具；该组「📰 产品资讯/工具教程」板块有 wigolo/openviking/zhihu-cli/claude-vision-skill 等同形态博文转化先例 |
| jishu/ai/anthropic | ❌ | 非 Anthropic 实体 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（过度工程） |

## 骨架判定（操作可复现性两问）

1. 有读者可照做的安装/配置/调用流程？✅ 安装（brew/npm）、Browser Mode 首次登录、Codex skill 复制、AGENTS.md 接线
2. 经实测且可复现？⚠️ 博文作者为转述推荐（"有人开源做好了"），未声明一手实测；但全部命令经官方仓库 docs（install.md/browser-mode.md/agents.md）与 npm 官方包页逐行核验一致

→ 设 examples/（2 篇），显著标注"命令经官方文档核验，博文作者未声明一手实测；CLI 快速迭代，以 `oracle --help` 为准"。

## 知识拆分（三层）

- concepts/00：发布事实层——项目档案、定位、三引擎、会话模型、版本快照
- concepts/01：模式层——"第二模型/第二大脑"工作流、推理与执行分流、额度经济学（观点分层）、适用边界
- concepts/02：机制层——Browser Mode（CDP/manual-login profile/附件打包/fail-closed/平台矩阵/并发）
- examples/00：安装与 Browser Mode 首次登录（含 Node 24+、Windows 边界）
- examples/01：Codex skill 接入与团队工作流（含 MCP 备选、安全卫生）

## 核验结论摘要

- 博文 10 项操作型声明与官方源逐项一致，0 ❌ 硬错误、0 项需勘误的错误数字
- "额度更耐用"为作者定性观点（无数据），博文自行澄清"不是额度互换"
- 5 项博文缺失/时效信息由官方源补充：Node 24+、brew 仅 macOS/Linux、API 六家 Provider、MCP server、版本快速演进
- status: verified；stale_after: 2026-12-31（CLI 月度级迭代，正文标注版本快照）

## 产出物

bundle：`jishu/ai/ai-agent/oracle/`（index + log + 3 concepts + 2 examples + 2 references + 3 子目录 index，共 10 文件）；组索引与总索引计数 V 阶段以 gates 脚本三角校验后同步。

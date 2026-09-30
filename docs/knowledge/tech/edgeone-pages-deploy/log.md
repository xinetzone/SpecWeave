# EdgeOne Pages 前端部署教程 - 变更日志

## 2026-09-29：初始版本（v1.0）

基于 2026-09-29 一次真实部署实战建束，采用七概念方法论（R→I→E→V→C，depth=standard）。

### R 阶段（事实采集）

- 从 `designer-portfolio` 部署全过程采集 21 条客观事实（F1–F21）
- 事实来源：CLI 实测输出、文件系统检查、npm 安装日志
- 关键事实：安装故障的 esbuild postinstall 根因（F2–F4）、项目结构（F10–F11）、部署耗时与产物（F14–F20）

### I 阶段（洞察）

- 提炼 3 条核心洞察（四元组完整：现象/根因/影响/建议）
  1. 安装失败的表层报错与真实根因不在同一层，需下钻一层
  2. 单体仓库中「这个前端项目」是指代歧义源，部署前必须显式消歧
  3. 登录站点与项目落区、预览链接时效三者不一致，需以控制台为准

### E 阶段（文档生成）

- `references/00-sources.md`：信源登记（S-001～S-005），信源先行
- `concepts/00-overview.md`：平台概览与适用场景
- `concepts/01-cli-install.md`：CLI 安装与 Windows 排错
- `concepts/02-login-auth.md`：登录与鉴权
- `concepts/03-deploy-static.md`：部署静态站点
- `concepts/04-deploy-framework.md`：部署需构建的前端项目
- `concepts/05-deploy-output.md`：解析部署产物
- `concepts/06-troubleshooting.md`：故障排查速查表
- `examples/00-static-portfolio-full-flow.md`：designer-portfolio 全流程实战
- 各级 `index.md`（根 + concepts + examples + references）与 `log.md`，均含 `{toctree}` 块

### V 阶段（验证）

- 结构检查：束目录完整（concepts 7 / examples 1 / references 1 / index / log）
- Frontmatter 检查：内容文档 9 篇字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）
- 交叉链接检查：全部使用 `/` 开头 bundle-relative 路径
- 计数断言：11 个 package.json、11 个前端配置、4 个作品页、6 个顶层条目，均经 `wc -l` 独立计数
- 事实一致性：命令、耗时、ID 与复盘报告 F1–F21 对齐

### C 阶段（模式沉淀）

- 沉淀「EdgeOne Pages 静态站点部署模式」（含 6 条反模式）至复盘报告第 5 节
- 排错结论固化入 `~/.workbuddy/skills/edgeone-pages-deploy/SKILL.md`（`--ignore-scripts` 绕过、`edgeone pages` 弃用说明）

---

**状态**：draft
**规范**：OKF v0.2
**下次检查**：2027-09-29（stale_after）

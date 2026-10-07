---
id: "agent-workspace-starter-skill"
name: "agent-workspace-starter"
title: "装载智能体工作区起步套件（Agent Workspace Starter）"
description: "把「智能体工作区起步套件」装载进用户自有项目并引导 60 分钟上手。当用户说'装载起步套件'、'装一下智能体工作区'、'starter 上手'、'把这套规范装进我的项目'、'用这个工作区起步'或要求把 starter 的 AGENTS.md/.agents 拷进某个项目时调用。装载后运行自检脚本验证完整性，并带用户走 60 分钟教程与规格驱动演练。"
version: "1.0.0"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
content-sensitivity: "public"
---

# 装载智能体工作区起步套件（Skill 门面）

## Skill ID

- **ID**：`agent-workspace-starter`
- **版本**：1.0.0
- **定位**：本套件自带的产品交付物（买家可装入自己的 Trae 环境使用），非 SpecWeave 仓库的主权区技能注册。

## 功能描述

帮助用户把「Agent Workspace Starter（智能体工作区起步套件）」装载进自有项目：把 `starter/` 的根契约 `AGENTS.md`、规范容器 `.agents/` 与 `LICENSE-NOTICE.md` 拷入目标项目，运行零依赖自检脚本确认装载完整，再按 60 分钟时间盒教程带用户跑通第一个「规格驱动小任务」。

## 何时使用（触发场景）

- 用户说「装载起步套件 / 智能体工作区 / starter 上手 / 把这套规范装进我的项目」。
- 用户手握本套件（含 `starter/`、`guide/`、`walkthrough/`、`scripts/`），希望把它落到某个自有项目。
- 用户想让一个现有项目具备「根 `AGENTS.md` + `.agents/` 导览」的最小智能体工作区。
- 用户装载后希望继续走教程或演练。

## 核心步骤

1. **确认目标**：向用户确认目标项目路径，以及 `AGENTS.md` 是「新建」还是「合并进已有文件」；不替用户默认决定。
2. **拷贝 starter**：按 [../bootstrap-prompt.md](../bootstrap-prompt.md) 的 S1-S8 安全规则，把 `starter/AGENTS.md`、`starter/.agents/`、`starter/LICENSE-NOTICE.md` 装入目标项目（详见 [../starter/AGENTS.md](../starter/AGENTS.md) 的「启动协议」）。
3. **运行自检**：执行 `python ../scripts/verify_starter.py --target <目标项目>`（脚本见 [../scripts/verify_starter.py](../scripts/verify_starter.py)）；退出码 0 视为装载完整，非 0 则按报告补缺。
4. **按启动协议读取**：读取目标根 `AGENTS.md` 全文，核验「启动协议」关键词，再据 `.agents/context-routing.md` 路由本次任务所需规范。
5. **带用户走教程**：引导用户打开 [../guide/README.md](../guide/README.md)，按 00 概览 / 01 装载 / 02 首个任务 / 03 进阶四段推进；首个任务照 [../walkthrough/README.md](../walkthrough/README.md) 的规格驱动剧本执行。
6. **就绪报告**：报告目标路径、根契约关键词命中、已装载类目、自检结果与下一步。

## 安全检查清单

- [ ] 写入前已向用户确认目标路径与「新建 / 合并」策略（S2）。
- [ ] 未在用户主目录、系统目录、磁盘根目录、隐藏目录自动创建文件（S3）。
- [ ] 装载过程只读取与拷贝文件，未执行 hooks / 脚本 / 依赖安装 / 系统配置修改（S4）。
- [ ] 目标根 `AGENTS.md` 已验证存在且含「启动协议」关键词（S5）。
- [ ] 遇错已说明类型、原因与解决方案，未静默失败（S6）。
- [ ] 只读取装载相关文件，未扫描整个文件系统、未上传数据（S7）。
- [ ] 若目标已是有效工作区，已跳过拷贝直接报告就绪（S8，幂等）。
- [ ] 已运行 `verify_starter.py` 并转述退出码与报告摘要。

## 关联引用

- [装载提示词（一句话装载）](../bootstrap-prompt.md)
- [教程总览（60 分钟路径）](../guide/README.md)
- [装载段教程（01-bootstrap）](../guide/01-bootstrap.md)
- [演练剧本（规格驱动小任务）](../walkthrough/README.md)
- [starter 根契约（AGENTS.md）](../starter/AGENTS.md)
- [零依赖自检脚本（verify_starter.py）](../scripts/verify_starter.py)
---
id: "agent-workspace-starter-guide-01-bootstrap"
title: "01 装载（15 分钟）——把工作区拷进你的项目"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 01 装载（15 分钟）

**本段目标**：把 `starter/` 拷进你的自有项目，让智能体按「启动协议」读取它，并用自检脚本程序化确认装载完整。

**前置**：00 概览已读完，你能指出 [../starter/AGENTS.md](../starter/AGENTS.md) 里的「启动协议」标题块。

## 步骤 1（5 分钟）：把 starter 拷进你的项目

starter 是「可直接搬进你项目」的目录，包含一份根契约 `AGENTS.md`、一个 `.agents/` 规范容器与一份许可说明。

**照抄（PowerShell，把尖括号处换成实际路径）：**

```powershell
# 把 starter 内容并入你的项目根目录
Copy-Item -Path "<套件路径>\starter\AGENTS.md"          -Destination "<你的项目>\AGENTS.md" -Force
Copy-Item -Path "<套件路径>\starter\.agents"            -Destination "<你的项目>\.agents" -Recurse -Force
Copy-Item -Path "<套件路径>\starter\LICENSE-NOTICE.md"  -Destination "<你的项目>\LICENSE-NOTICE.md" -Force
```

> 若你的项目根已有 `AGENTS.md`，先用编辑器把 starter 版的「启动协议」段落**合并**进去，避免覆盖你原有内容。

拷完后的目标结构：

```
你的项目/
├── AGENTS.md            ← starter 根契约
├── LICENSE-NOTICE.md    ← 许可说明
└── .agents/             ← 规范容器（全貌导览）
```

## 步骤 2（5 分钟）：让智能体按启动协议读取

把下面这段**简版装载提示词**发给你的智能体（完整版见 [../bootstrap-prompt.md](../bootstrap-prompt.md)）：

```text
请装载这个项目里的智能体工作区：
1. 先读根目录 AGENTS.md 全文，确认其中存在「启动协议」标题块，并按它执行。
2. 再按上下文路由，读取 .agents/ 下与当前任务直接相关的规范入口。
3. 读完后向我报告：装载到的规范类目清单、可用角色、可用技能。
4. 装载过程只读规范文件，不执行任何 hooks 脚本，不安装任何依赖。
5. 若 AGENTS.md 缺失或读不到「启动协议」，直接告诉我失败原因，不要假装成功。
```

**验收点**：智能体的报告里出现「启动协议」字样，并列出 `.agents/` 下的类目清单。

> 这一步体现了工作区的核心价值：你不再需要每次重复交代规则——项目里的 `AGENTS.md` 已经写清了开工流程。

## 步骤 3（5 分钟）：运行自检

自检脚本会核对 starter 文件齐备性、「启动协议」关键词锚点与相对链接可达性。

**照抄（在套件根目录运行，即 `agent-workspace-starter\` 下；脚本不在你的项目里，无需拷入）：**

```powershell
python scripts\verify_starter.py
```

**或对已并入 starter 的项目目录做定向核验（同样在套件根目录运行，把尖括号处换成你的项目路径）：**

```powershell
python scripts\verify_starter.py --target "<你的项目>"
```

**验收点**：脚本输出通过报告且退出码为 0（PowerShell 中用 `$LASTEXITCODE` 查看）。若脚本列出缺失项，按报告补齐对应文件后重跑。

> 自检脚本位于套件根的 [../scripts/verify_starter.py](../scripts/verify_starter.py)（由并行任务产出，路径固定）。

## 完成检查点

- [ ] starter 的 `AGENTS.md`、`.agents/`、`LICENSE-NOTICE.md` 已并入你的项目。
- [ ] 智能体报告中出现「启动协议」字样，并列出 `.agents/` 类目清单。
- [ ] `python scripts\verify_starter.py`（在套件根目录运行）输出通过报告且退出码为 0。
- [ ] 能说出「装载」与「通读全部规范」的区别：你只装了入口层与导览。

---

下一段 → [02-first-task.md](02-first-task.md)（首个任务，25 分钟）
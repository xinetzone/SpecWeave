---
title: "来源会话证据：external/playground 三件套落盘"
source: "Qoder 会话 3e23608a-835b-4346-adf5-2ec846d41320（标题：添加README与代理）"
date: "2026-10-24"
type: "evidence"
---

# 来源会话证据

## 1. 会话范围

- 会话 ID：`3e23608a-835b-4346-adf5-2ec846d41320`
- 标题：添加README与代理
- 用户请求：`七概念 同时为 D:\spaces\SpecWeave\external 和 D:\spaces\SpecWeave\playground 添加 README.md + AGENTS.md + .agents/`
- 会话只有一轮，**没有用户纠正**；以下结论全部来自该轮工具输出。

## 2. 实际执行链

1. 读取磁盘根 `AGENTS.md`，执行启动协议。
2. 加载 `seven-concepts-cmd`，识别为「重构优化」场景，链路 `I→F→A→C`。
3. 盘点两个目录：`ls`、`find AGENTS.md`、`find .agents/`。
4. 核对版本控制：`.gitignore` 第 12 行 `external/`、第 13 行 `playground/`；`git ls-files` 两目录计数均为 0；`git check-ignore -v` 命中。
5. 读取范本：`apps/.agents/README.md`、`projects/.agents/README.md`、`playground/huncheng-lab`、`.agents/protocols/workspace-discovery.md` §5、`.agents/rules/content-sensitivity-precheck.md`。
6. 写入 5 个新文件，修改 1 个既有 README。
7. 校验关键词、相对链接与 gitignore 状态。

`seven-concepts-cmd` 只提供方法论编排，没有覆盖「目录治理三件套落盘」这一具体工序；该工序是在执行中临时展开的，因此需要独立 Skill 固化。

## 3. 可复核的观测值

| 观测 | 值 |
|---|---|
| `external/` 嵌套 AGENTS | 5 个（`chaos/ai`、`chaos/xmtools`、`dao/rea`、`dao/Strata`、`shengjidaguai-china/Financial_Modeling`） |
| `playground/` 嵌套 AGENTS | 18 个（根 AGENTS 登记 5 个，其余声明嵌套优先） |
| `external` 失效引用 | `external/chaos/npuusertools` 不存在；实际已归档为 `chaos/npuusertools-archive-20260921`；`compose-overlay-ops/SKILL.md` 仍指向旧路径 |
| 产物 | 新增 `external/{README.md,AGENTS.md,.agents/README.md}`、`playground/{AGENTS.md,.agents/README.md}`；修改 `playground/README.md` |
| 独立复核（本 Skill 创建时） | 6 个文件仍在；相对链接 19/13/11/45/22/12 条，0 断链 |

## 4. 未验证项

- 会话没有用户纠正，不能把「无纠正」写成「用户确认」。
- 校验后对 `external/README.md` 与 `playground/README.md` 的两次 Edit，工具输出只记录「1 replacement」，未捕获精确 diff；最终报告称「仅增补 AI 入口引用并追加 changelog」。
- 未运行触发词 eval；description 为人工审查。
- 校验脚本不检查 HTML 链接、代码块内链接与文档语义质量。

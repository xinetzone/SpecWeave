---
id: "doocs-md-py-agents-changelog"
title: "doocs-md-py AI 资产变更日志"
source: "../AGENTS.md#变更日志"
---
# doocs-md-py - AI 资产变更日志

本文件汇总 `apps/doocs-md-py` 的 AI 资产（`AGENTS.md` 与 `.agents/`）变更，按原子提交粒度记录。
条目格式：`日期 | 类型 | 说明`（类型沿用 Conventional Commits 的 `type`）。

## 2026-10-16

- 2026-10-16 | chore | **AI 资产容器初始化**：新增应用级 [AGENTS.md](../AGENTS.md) 与 [.agents/](README.md)，应用由「遵循根规范」升级为**应用自治**
  - [AGENTS.md](../AGENTS.md)：启动协议（含内容敏感度预检与 5 项自检）+ 项目概述（上游基线 v2.1.0 @ `1bdad48d` / 三条入口 / 渲染核心 27 模块）+ 嵌套路由关系（含 `src/` 全分层映射）+ 上下文路由表（19 行，覆盖渲染/服务端/上传/CLI/MCP/构建/证据复现）+ P0 约束速览（12 项）
  - [.agents/rules/upstream-reconstruction.md](rules/upstream-reconstruction.md)：上游基线唯一化与磁盘为准、锚点注释强制、复刻口径三分类、`D-`/`CD-` 差异台账登记与裁决流程、AC-U2/AC-U3 验收口径、NG1–NG6 非目标冻结
  - [.agents/rules/engineering-redlines.md](rules/engineering-redlines.md)：Python ≥3.14 与 `__future__` annotations 禁令（AST 守护）、依赖白名单与克制、scikit-build-core 三段声明、命名与 frontmatter 溯源、覆盖率双门禁（总 ≥80% + 关键模块 ≥90%）、ruff / PATH 裁剪 / 跨平台路径 / `/mnt/ai` 大体积落点
  - [.agents/rules/render-and-theme-contract.md](rules/render-and-theme-contract.md)：渲染核心无副作用与三入口共享、管线顺序、12 扩展注册纪律、11 项特色行为不可回退清单、主题 CSS `var()`/`calc()` 解析与代码块主题 CDN 白名单、归一化 DOM 等价验收与黄金样例、NFR-6 性能基线
  - [.agents/rules/server-api-and-security.md](rules/server-api-and-security.md)：契约 1:1 与装配顺序、SQLite 替代 D1（8 迁移幂等 / epoch ms / LWW / 游标 / 配额 / 限流）、JWT 与 Origin 白名单、分享 PBKDF2 与固定 CSP 净化、密钥不入库不入日志与配置体检、上传后端门控、爱发电「只信订单号并服务端回查」幂等纪律
  - [.agents/rules/uploaders-dual-path.md](rules/uploaders-dual-path.md)：`server/upload_*.py` 与 `uploaders/*.py` 两套上传路径辨识、`providers.ts` 协议与注册表真源、手写签名与已知答案测试向量、凭证零内置、图床数量口径差异登记、`formCustom` 不执行用户 JS 边界
  - [.agents/rules/cli-and-mcp-contract.md](rules/cli-and-mcp-contract.md)：`mdpy` 五子命令与退出码契约、MCP 13 工具 1:1、`render_markdown` 入参显式 camelCase → snake_case 映射与双向锁定测试、选项字面值一致性、数量口径更正纪律（19→20 更正先例）
  - [.agents/README.md](README.md)：资产索引 + 22 项核心资产真源 + 人类文档 ↔ AI 规则对应关系 + 三级父级回退链
  - 同步 [apps/AGENTS.md](../../AGENTS.md)：应用路由表行（`—（遵循根规范）`/`❌ 无` → AGENTS.md 链接 / `✅ 有`）、「可用资产索引」新增 doocs-md-py 应用小节、「边界声明」新增 AGENTS.md 与 `.agents/` 两行、嵌套优先级图新增根级应用分支、路由流程图「有自身 AGENTS.md」名单补入
- 2026-10-16 | docs | 记录本次事实采集的两项基线结论以备后续复用：①本应用为 apps/ 下**首个根级自治应用**（此前根级应用均「遵循根规范」）；②`docs/` 现为 5 篇工程文档且**暂无索引页**，若后续补 `docs/README.md` 需同步 [../AGENTS.md](../AGENTS.md)「人类文档」行与 [.agents/README.md](README.md) 的人类文档映射表

- 2026-10-16 | fix | **规则事实性错误更正（数量口径）**：`engineering-redlines.md` §2 与 [../AGENTS.md](../AGENTS.md)「P0 约束速览」#6 的「运行期依赖白名单」由「9 项（含 `mcp`）」更正为「**8 项（不含 `mcp`）**」。依据：`pyproject.toml` `[project].dependencies` 实为 8 项，且 `src/` 全量检索无任何 `import mcp`；`mcp` 已按 [../docs/contract-differences.md](../docs/contract-differences.md) 的 `CD-21` 删除（`mcp` 2.3.0 对 Python 3.14 不兼容，stdio JSON-RPC 2.0 传输层与工具注册表改本仓手写）。同步更正 [apps/AGENTS.md](../../AGENTS.md) 可用资产索引中的「9 项依赖白名单」表述
  - **预防措施**：依赖口径的陈述一律以 `pyproject.toml` 为唯一事实源并显式标注；凡涉及「依赖数量 / 清单」的规则表述，须与手写实现边界（如 MCP 传输层）区分开，避免将「本仓手写能力」误计入第三方白名单

- 2026-10-16 | fix | **依赖白名单口径更正（9 → 8 项，移除 `mcp`）**：`mcp` 已于 T18 决策移出运行期依赖（证据见 [Task 18「移除 `mcp>=1.2` 运行时依赖声明」](../../../.trae/specs/doocs-md-py/tasks.md)），stdio 传输层改为仓内手写零依赖实现；但 [../AGENTS.md](../AGENTS.md) P0 约束速览第 6 项、[rules/engineering-redlines.md](rules/engineering-redlines.md) §2 与 [../../src/doocs_md_py/mcp_server/stdio.py](../../src/doocs_md_py/mcp_server/stdio.py) 模块 docstring 仍按「9 项含 `mcp`」表述，本次一并更正
  - [../AGENTS.md](../AGENTS.md) P0 约束速览第 6 项：白名单改为 8 项，并显式标注「不含 `mcp`（MCP 传输层为仓内手写实现）」
  - [rules/engineering-redlines.md](rules/engineering-redlines.md) §2：白名单改为 8 项；新增「`mcp` 不在白名单」说明条（含排除理由与对上游 `packages/mcp-server` 的 1:1 契约关系），防止后续被误加回
  - [../../src/doocs_md_py/mcp_server/stdio.py](../../src/doocs_md_py/mcp_server/stdio.py)：模块 docstring 将旧述「pyproject 的 `mcp>=1.2`」更正为历史时态，并新增「依赖状态」段
  - 已对齐、本次无需改动：[../../pyproject.toml](../../pyproject.toml) 与 [../../README.md](../../README.md) 的白名单本即为 8 项（README 快速开始处同步补注「MCP 零外部依赖」）
  - 未处理的同类残留（待裁决）：`spec.md` NFR-2 仍列「9 项含 `mcp`」，属需求层表述，就地更正需用户批准

## 约定（后续条目遵循）

- 任何 `AGENTS.md` / `.agents/` 变更**必须**同步：①本文件新增条目；②受影响规则文件的 `§` 与 [../AGENTS.md](../AGENTS.md) 的「上下文路由表」「P0 约束速览」；③若涉及应用自治状态变化，同步 [apps/AGENTS.md](../../AGENTS.md) 路由表与边界声明
- 变更类型沿用 Conventional Commits：`chore`（资产初始化/结构调整）、`docs`（文档与规则内容修订）、`fix`（规则事实性错误更正，如数量口径、路径失效）

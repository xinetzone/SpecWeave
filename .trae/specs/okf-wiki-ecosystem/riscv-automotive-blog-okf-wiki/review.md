---
id: review
title: 《ARM败在哪？RISC-V上车》博文转化 V 阶段对抗审查记录
created: 2026-11-04
---

# V 阶段对抗审查记录（review）

> 对象：`projects/awesome-okf-xs/doc/bundles/jishu/iot/riscv-automotive/`（9 文件）+ spec 事实集。
> 方法：四视角 + 老板视角内容审查，机械门禁脚本实跑。

## 1. 四视角审查结论

### 1.1 事实溯源（魔鬼代言人）

- 全部产业主张均挂 F 编号（F-001~F-041）；正文无 facts.md 之外的编造。
- **作者主张与核验方补充事实清晰分离**：DF30/M100/CCR4001 等产业案例（F-030~F-034）在正文明确标注为"核验方引入的佐证，非作者主张"（见 [concepts/00 §1](../../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/riscv-automotive/concepts/00-supply-chain-autonomy.md) 与根 index 已知边界 5）。
- 3 项 ⚠️ 全部保留口径限定、不升格为事实：① "2026 量产元年"标注为媒体框架（M100 实为 2025-12-18 上车）；② "换供应商不重写软件"标注为理想上限（F-018 作者自陈）；③ "短期 ARM 仍主流/双轨并行"标注为作者定性能见。
- 本文**无量化数字与具体产品名**，故无逐字勘误项；核验转为"产业事实框架是否成立"，已在 verification.md 如实说明。

### 1.2 结构规范

- 骨架与两问判定一致：产业评论类，**无 examples/**（与 embedded-weekly-03 正例同型）。
- 3 个 index.md（根 / concepts / references）均含 `{toctree}` 块；根 toctree 收 concepts/index、references/index、log。
- 文件名 kebab-case；frontmatter 9 文件齐备必需字段（okf_version/type/title/description/tags/generated/status/stale_after），根 index 与 references 含 sources。
- 单个 Mermaid 代码块（concepts/01 §2 生态链）以 ```text 表达，无渲染风险。

### 1.3 读者可用性（新人视角）

- bundle 内 30 条相对链接经正则 + 存在性校验 **0 断链**。
- 三条概念路径按"现象事实 → 机制路径 → 工程边界"排列，阅读顺序 00→02 明确；每篇底部有"延伸"互链。
- 首页性质声明 + "三点口径提示"置顶，读者在进入正文前即知本文为产业评论、含定性判断与媒体框架。

### 1.4 时效边界（未来视角）

- `stale_after: 2027-05-31`；3 条提前复核触发条件：① 权威出货份额数据出现；② RISC-V 车规安全认证标准化实质进展；③ 高安全核心域（动力/底盘/域控）RISC-V 方案批量量产。
- 已记录"量产元年"两口径（2025-12 精确起点 vs 2026 行业框架），避免时效性误读。

### 1.5 老板视角（采用决策）

- 给车企/供应链读者的可行动结论：RISC-V 的价值是**打开第二供应链**（双轨并行），而非立即替代 ARM；采用前需评估 **AUTOSAR 层抽象适配成本**（F-021）与**工具链 ISO 26262 全链路认证成本**（F-022/F-023，ASIL-D 约 2 年、编译器属 TCL1）。
- 提示"开源 ≠ 无风险"：商用车规 IP 多为私有实现，开源代码不附安全资质（F-026/F-027）。

## 2. 机械门禁结果（脚本真实输出）

| 检查项 | 工具 | 结果 |
|--------|------|------|
| 总索引五面对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / **705 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| 双份 F 编号 | 正则 `^\|\s*F-(\d{3})\s*\|` 集合比对（spec facts.md ↔ article-source.md） | ✅ 各 41、集合相等、F-001~F-041 连续 |
| 相对链接 | 正则提取 + 路径存在性（bundle 9 文件 / 30 链接） | ✅ 0 断链 |
| UTF-8 strict | `python scripts/check-utf8.py` | ✅ 12769 文件通过 |
| 敏感信息 | grep 检索 `file:///`、`C:\Users`、家目录前缀 | ✅ 0 命中 |
| frontmatter | 必需字段 + sources 三信源（博文 + riscv.org + 官方规范库） | ✅ |
| toctree 可达 | `python scripts/check-toctrees.py` | ⚠️ 见下节（4 处缺口**均在他人 WIP 目录，与本包无关**） |

> **gates 环境说明**：`invoke gates.all` 依赖 invocations 环境，本次以**手动等效核验**直接运行底层 `scripts/*.py`，未谎报"invoke gates 通过"。

## 3. 过程异常与处置

1. **并发会话改动总索引**：本轮开始读到的 `bundles/index.md` 为 703 束/513 束，门禁首跑即报"frontmatter=704 而目录树=705"——查明为**其他会话并发新增 1 束**并已将计数改为 704/514。按项目记忆的**并发隔离纪律**，重新读盘后仅补本次 +1（→705/515），**未回滚他人变更**。
2. **toctree 门禁 4 处缺口均为他人在途 WIP**：`jishu/ai/products/pagekin/`（缺 index.md、references 文件不可达）、`jishu/ai/ecosystems/deepseek/super-agent-architecture/`（缺 index.md）属并行会话未完成产物；本包 3 级 toctree **全部可达**、无告警。按纪律**只报告不擅改**。
3. **微信反爬例外如实记录**：Skill 文档载明 `mp.weixin.qq.com` 常被 WebFetch 反爬（13/13 拦截），本次首次即成功返回全文，已记为**例外**，非普遍可行。

## 4. 终判

- bundle `status: draft`：核心框架经产业事实佐证、**0 勘误**；但内容以定性与趋势判断为主、可核性有限，按保守档处理，**不置 flagged**。
- 可进入 C 阶段；提交待用户明确指令（子模块 → 主仓库 spec → gitlink，不 push）。

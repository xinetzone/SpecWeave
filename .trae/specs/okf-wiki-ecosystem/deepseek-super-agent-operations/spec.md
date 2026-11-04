---
title: DeepSeek Super-agent 安装与权限管理 OKF 教程
status: draft
version: "1.0"
methodology: seven-concepts-cmd R→I→E→V
content-sensitivity: public
source: https://mp.weixin.qq.com/s/53k2H8ma2ZnjZzCncB0FuA
---

# DeepSeek Super-agent 安装与权限管理 OKF 教程

## 概述

将 AI信息Gap 于 2026-11-02 06:59 发布、署名木易的AI频道的《DeepSeek「超级智能体」，我真养上了！没人 @ 自动干活，附保姆级教程》转为原创、可溯源的中文 OKF Wiki。浏览器已读取页面元信息及完整文本正文，未保存全文镜像。配图内容尚未单独核读。

目标读者为理解 GitHub Issue、PR 和基本终端操作，准备评估研究原型的开发者。

## 目标与非目标

目标目录：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/deepseek/super-agent-operations/`。

用户已选择独立教程包，不并入在途 `super-agent-architecture/`。正文侧重安装、身份隔离、观察模式、自动接单、自定义静默规则、停止与恢复，以及费用和支持范围。

不安装软件、不登录机器账号、不创建 Issue/PR、不启动服务、不配置定时任务、不提交或推送 Git。不给出“生产就绪”“保证静默”“固定耗时费用”的承诺。不覆盖在途架构包，不替其他会话修整全局存量缺陷。

## 背景与约束

文章公开可读，无登录或验证码。子项目 AGENTS.md 明确允许公开知识写入 `doc/bundles/`，其嵌套规则适用于本次产出。

原文同时有安装命令、操作顺序、输入与作者观察到的输出，满足设立 `examples/` 的两问条件；所有操作示例必须注明“依据作者实测整理，本次未运行复现”。

当前 `gh api repos/deepseek-ai/dsh-superagent-prototype/contents/README.md` 返回退出码 4，要求 GH_TOKEN。仓库 URL 由原文提供，但 README、SETUP.md、LICENSE 和固定提交未核读，不能冒称官方验证。

官方价格页 WebFetch 读到 `deepseek-v4-flash`、输出 2 元/百万 tokens；搜索结果指向更新后的 `deepseek-flash` 和闲时分档。需继续核对实时页面，不能把不同模型/时段的值直接作为对方错误的证据。

共享总索引及多个包存在他方未提交或已暂存变更。写共享索引前回读现盘、只增本包条目和相应计数；若发生直接冲突则暂停该面，不覆盖。

## 功能需求

- FR-1：登记账号、作者、日期、访问通道、来源距离及失败清单；连续 F 编号分离页面事实、作者声明与执行者推论。
- FR-2：核对日期版本、成效数字、范围口径、引文与官方政策；不可得证据标单源或 flagged。
- FR-3：用概念页解释身份、接收开关、接单模式、接单规则与执行授权的不同职责，覆盖文章六部分以及文末限制。
- FR-4：提供安装前审阅、首个工单、观察到自动接单、静默规则与停止恢复的学习示例；命令仅按已读来源记录。
- FR-5：形成至少三条四元组洞察和一个单案例待验证的迁移模式，不把推导当官方机制。
- FR-6：每篇非保留 Markdown 有可解析 OKF frontmatter；各级 toctree 完整并接入父索引，相关主题链接只指向实际存在的入口。

## 非功能需求

- NFR-1：中文原创改写，英文 kebab-case 文件名，不复制长提示词或全文。
- NFR-2：所有具体能力、数值、命令均引用 F 编号；来源使用 `sources[].resource`。
- NFR-3：核心官方实现无法核验时使用 `status: flagged`，设复核期限，不伪造 verified 事件。
- NFR-4：实施者自验后由新上下文只读审查；编译、链接与内容证据分别报告。

## 验收标准

### AC-1 信源可审计
- **Type**: `rule`
- **Pass Condition**: source-manifest 记录公开性、身份和失败；facts 与 article-source 两份连续 F 集合相同，verification 覆盖全部编号；实测、官方和推论不混用。
- **Evidence**: 信源台账、编号机械比对、核验表。

### AC-2 教程覆盖与可读性
- **Type**: `rubric`
- **Dimension**: 六部分操作与文末边界的覆盖、前置条件、预期结果、失败处置及原创表达。
- **Scale**: 1-5
- **Anchors**: 1 = 摘要拼接且缺安全边界；3 = 基本覆盖但前置条件或证据级别不清；5 = 全覆盖、分层准确、可独立学习且不冒称实测。
- **Pass Threshold**: >= 4
- **Evidence**: 章节映射与独立内容审查。

### AC-3 方法论分层
- **Type**: `rule`
- **Pass Condition**: 至少三条洞察均有现象、工作假说、影响、建议与 F 证据；一个模式有适用/不适用、步骤、反模式、检验与概念迁移，明确单案例未验证。
- **Evidence**: knowledge-map 与模式页、G1-G3 记录。

### AC-4 导航与格式
- **Type**: `rule`
- **Pass Condition**: 新增文件 UTF-8 无 BOM，非保留文件 frontmatter 完整，相对链接无断链，toctree 覆盖全部正文；索引计数依据当前目录与权威脚本验证。
- **Evidence**: 子项目门禁、范围链接检查与构建结果；存量或并发缺陷单独归因。

### AC-5 权限与交付边界
- **Type**: `rule`
- **Pass Condition**: 未改在途架构文件、未安装或启动原型、未执行 Git 写操作；价格冲突和源码未读限制在入口及相关正文同步；最终独立审查无本任务可行动发现。
- **Evidence**: 作用域 diff/status、log、独立 review。

## 待决事项

完整规格与任务批准前不写正式教程。GH_TOKEN 缺失不要求用户提供明文秘密；保持官方实现待核验，可交付 flagged 学习包。后续实际部署需要另行授权。

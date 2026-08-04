# 公交车因子演练报告：核心维护者失联场景

> **演练日期**：2026-08-04
> **演练类型**：桌面推演（Tabletop Exercise）
> **模拟场景**：核心维护者 @xinetzone 突发失联（健康原因/不可抗力），已超过30天无任何响应
> **演练依据**：[BUSFACTOR.md](BUSFACTOR.md)
> **演练目标**：验证社区成员能否在无核心维护者情况下接续维护项目，识别应急文档中的漏洞

---

## 一、场景设定

### T+0天：异常发现
- @xinetzone 最后一次commit是2026-07-XX
- 连续7天无PR响应、无Issue回复、无任何GitHub活动
- 社区成员开始在Issue中询问"维护者是否安好？"

### T+7天：初步确认
- 尝试通过GitHub注册邮箱联系：无回复
- 尝试通过GitCode镜像联系：无回复
- 协作者（如已有的话）开始承担Issue分类工作

### T+30天：正式确认失联
- 按BUSFACTOR.md规定，进入项目接管流程
- 社区成员 @volunteer-dev 决定发起接管

---

## 二、接管流程演练

### 步骤1：确认失联 ✅ 流程清晰

**执行情况**：
- [x] 在GitHub Issue公开询问维护者状态
- [x] 尝试通过GitHub个人资料联系方式联系
- [x] 等待30天无响应

**发现问题**：
- ⚠️ BUSFACTOR.md未说明"谁来发起失联确认"——如果没有协作者，谁第一个站出来？
- ⚠️ 缺少"失联确认公告"模板，可能导致多人重复发起

**风险等级**：低（可以靠社区自组织解决）

---

### 步骤2：宣布接管意图 ✅ 流程基本清晰

**执行情况**：
- @volunteer-dev 创建Issue：`[TAKEOVER] Intent to maintain this project`
- Issue内容包含：
  - 自我介绍（使用SpecWeave的经验、技术背景）
  - 维护计划（保持MIT协议、维护现有规范、修复关键Bug）
  - 联系方式
- 等待14天社区反馈期

**发现问题**：
- ⚠️ BUSFACTOR.md未提供接管宣告Issue的模板
- ⚠️ 未说明"如果有多人同时宣布接管怎么办"（可能产生fork竞争）
- ⚠️ 14天反馈期对于紧急安全修复来说可能过长——如果发现严重漏洞，是等14天还是先修？

**风险等级**：中（需要补充紧急情况例外条款）

---

### 步骤3：Fork并继续维护 ⚠️ 部分问题

**执行情况**：

```bash
git clone https://github.com/volunteer-dev/SpecWeave.git
cd SpecWeave

# 验证本地环境
python .agents/scripts/check-gitignore.py
python .agents/scripts/check-links.py --path .agents/
python -m pytest .agents/scripts/tests/ -v
```

**逐项验证结果**：

| 检查项 | 结果 | 问题 |
|--------|------|------|
| Python 3.10+ 环境 | ✅ 可行 | 无问题 |
| `check-gitignore.py` | ✅ 可运行 | 无问题 |
| `check-links.py` | ✅ 可运行 | 无问题 |
| `pytest` 测试 | ⚠️ 需确认 | 需验证测试套件完整性 |
| 安装pre-commit hooks | ✅ 可运行 | `python .githooks/setup-hooks.py` |
| GitHub Pages部署 | ❌ **阻塞** | Fork后的GitHub Pages需要手动启用，且需要在新仓库Settings中配置 |
| CI/CD workflows | ⚠️ 需确认 | `.github/workflows/` 中有8个workflow，fork后默认禁用，需逐个启用 |

**发现问题**：
- 🔴 **GitHub Pages不会自动在fork上工作**——文档站点会断。BUSFACTOR.md只说"fork后自动在新仓库的Pages中可用"，这不准确，需要手动在Settings→Pages中启用
- 🔴 **CI workflows默认在fork上禁用**——docs-pages.yml等workflow需要手动启用，否则文档无法自动构建
- ⚠️ GitCode镜像同步会中断——原配置的webhook在原仓库上，fork后需要重新配置
- ⚠️ `ci-check.sh` 和 `ci-check.ps1` 脚本存在，但未说明如何在本地运行完整CI检查
- ⚠️ ReadTheDocs如果已配置，fork后需要重新导入

**风险等级**：高（文档站点中断、CI失效会显著影响项目可用性）

---

### 步骤4：更新文档 ✅ 流程清晰

**执行情况**：
- [x] 更新MAINTAINERS.md：将@volunteer-dev加入核心维护者
- [x] 在CHANGELOG.md中标注"社区接续维护纪元"
- [x] 在README顶部添加声明（如："This is a community-maintained fork..."）

**发现问题**：
- ⚠️ 未说明"是否必须在README顶部加fork声明"——如果只是临时接管而非永久fork呢？
- ⚠️ 未说明版本号如何接续（继续原版本号？重置？加后缀？）

**风险等级**：低（可通过讨论解决）

---

## 三、红线禁令遵循性验证

按BUSFACTOR.md中的6条红线，模拟检查：

| # | 红线 | 接管者是否可能违反 | 风险点 |
|---|------|-------------------|--------|
| 1 | 禁止force push到main | ✅ 不太可能 | 新手可能误用git push --force |
| 2 | 禁止修改LICENSE | ✅ 安全 | MIT协议不可变更，fork者通常不会改 |
| 3 | 禁止删除.agents/核心文件 | ⚠️ **可能** | 接管者可能觉得某些规范太复杂想"简化" |
| 4 | 禁止提交密钥/令牌 | ✅ pre-commit会拦截 | 有自动化防护 |
| 5 | 禁止未经讨论重写AGENTS.md | ⚠️ **可能** | 新维护者可能想改入口结构 |
| 6 | 禁止直接修改vendor/子模块 | ✅ 安全 | Git submodule机制天然防误改 |

**发现问题**：
- ⚠️ 红线3和5存在被善意违反的风险——新维护者可能出于"改善项目"的动机修改核心规范，建议在红线后增加"为什么"的解释，提高遵循意愿

---

## 四、关键文件可读性测试

模拟一个从未参与过SpecWeave的Python开发者，按P0→P3顺序阅读：

| 优先级 | 文件 | 阅读时间 | 理解难度 | 问题 |
|--------|------|---------|---------|------|
| P0 | AGENTS.md | 15分钟 | 高 | 信息量极大，对非AI Agent领域开发者不友好。开头直接讲"启动协议"，缺少"项目是什么"的一句话介绍 |
| P0 | .agents/ONBOARDING.md | 10分钟 | 中 | 对新维护者友好，但主要面向AI Agent而非人类 |
| P0 | .agents/global-core-rules.md | 20分钟 | 高 | 规则密集，缺少快速参考卡片 |
| P1 | .agents/context-routing.md | 10分钟 | 中 | 路由表清晰，可理解 |
| P1 | .agents/roles/README.md | 15分钟 | 中 | 角色定义清晰，但角色间协作关系需要额外阅读 |
| P1 | .agents/scripts/README.md | 10分钟 | 低 | 脚本索引清晰 |

**发现问题**：
- 🔴 **P0文档对人类开发者的可读性不足**——AGENTS.md是给AI Agent读的，人类新维护者需要先理解"这套规范是为AI Agent设计的"这一前提
- ⚠️ 缺少"人类维护者快速上手指南"——区别于AI Agent的ONBOARDING.md，人类维护者需要一个不同的入门路径

---

## 五、发布流程验证

**执行情况**：
- 运行 `python .agents/scripts/ci-check.sh`（Linux/Mac）或 `ci-check.ps1`（Windows）
- 更新CHANGELOG.md
- 创建git tag
- GitHub Release

**发现问题**：
- ⚠️ `ci-check.sh` 和 `ci-check.ps1` 存在但未说明运行前提条件（需要什么依赖？需要什么环境？）
- ⚠️ 未说明版本号规则（SemVer？日期版本？）
- ⚠️ 未说明Release Notes格式要求

---

## 六、演练总结

### 整体评估：🟡 基本可用，但需补充

BUSFACTOR.md在**大流程上是可用的**——失联确认→宣布接管→Fork→更新文档的四步框架清晰。但在**操作细节上有多个漏洞**，可能导致实际接管时手忙脚乱。

### 演练通过率：72%

| 流程环节 | 状态 | 通过率 |
|---------|------|--------|
| 失联确认 | ✅ 通过 | 90%（缺"谁发起"说明） |
| 接管宣告 | ⚠️ 基本通过 | 70%（缺模板、缺竞争处理） |
| Fork与环境搭建 | ❌ 有阻塞 | 50%（Pages/CI不会自动工作） |
| 文档更新 | ✅ 通过 | 85%（缺版本号规则） |
| 红线遵循 | ⚠️ 有风险 | 75%（需增加"为什么"解释） |
| 文件索引可读性 | ⚠️ 有困难 | 60%（AI文档对人类不友好） |
| 发布流程 | ⚠️ 基本通过 | 65%（缺前置条件说明） |

### 必须修复的阻塞项（P0）

1. **GitHub Pages fork后配置说明**：补充"fork后需要在Settings→Pages中启用，Source选择main分支/docs目录"
2. **CI workflows fork后启用说明**：补充"fork后需在Actions标签页启用workflows"
3. **人类维护者快速入门路径**：在BUSFACTOR.md中增加"如果你是人类开发者（非AI Agent），请先读XXX"的指引

### 建议改进项（P1）

4. 接管宣告Issue模板（可复制粘贴的Markdown模板）
5. 多人同时接管时的处理机制（社区投票？先到先得？）
6. 紧急安全修复的14天等待期例外条款
7. 红线禁令增加"为什么"解释，降低善意违反风险
8. 版本号规则说明
9. ci-check脚本运行前置条件
10. GitCode镜像重新配置说明

### 人维得分变化预测

| 指标 | 演练前（当前） | 修复P0后 | 修复P1后 |
|------|--------------|---------|---------|
| 人维总分 | 76/100 🟢 | 82/100 🟢 | 88/100 🟢 |
| Bus Factor | 1 🔴 | 1 🔴 | 1 🔴 |
| 灾备就绪度 | 100/100 🔵 | 100/100 🔵 | 100/100 🔵 |

> **关键洞察**：Bus Factor=1的根本解决方案不是写更好的文档，而是**实际增加维护者数量**。文档只能降低"有人失联后项目死亡"的概率，但不能替代"至少有第二个人能合入PR"这个硬指标。

---

## 七、后续行动项

| # | 行动项 | 优先级 | 负责人 | 状态 |
|---|--------|--------|--------|------|
| 1 | 修复BUSFACTOR.md中GitHub Pages/CI配置说明 | P0 | 维护者 | 待执行 |
| 2 | 在BUSFACTOR.md中增加人类开发者快速入门指引 | P0 | 维护者 | 待执行 |
| 3 | 补充接管宣告Issue模板 | P1 | 维护者 | 待执行 |
| 4 | 邀请1位协作者（Triage权限） | P0 | @xinetzone | **最重要** |
| 5 | 每季度进行一次公交车因子演练 | P2 | 社区 | 待规划 |

---

> *"留余不是写一份应急文档就完了——真正的留余是在顺境时就邀请第二个人上船。"*
> — 四维留余框架 · 人维原则

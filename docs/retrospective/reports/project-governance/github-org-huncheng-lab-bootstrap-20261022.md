---
id: "github-org-huncheng-lab-bootstrap-20261022"
title: "huncheng-lab GitHub 组织创建复盘"
created: 2026-10-22
source: 七概念方法论编排（F→V→I→C → R→I→E→C 闭环）
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/project-governance/github-org-huncheng-lab-bootstrap-20261022.toml"
tags: [github, organization, naming, bootstrap, methodology]
---

# huncheng-lab GitHub 组织创建复盘

> 从"想建个组织管 demo"到组织上线，完整走了七概念 F→V→I→C 闭环。本报告沉淀命名决策过程与可复用模式。

## R · 事实清单（客观事实，无因果词）

| # | 事实 |
|---|---|
| R1 | 用户初始需求：创建 GitHub 组织管理个人项目，主要针对 demo |
| R2 | 用户触发 /七概念，场景识别为创新突破（F→V→I→C） |
| R3 | 首推组织名 `xinetzone-lab`（基于个人品牌连续性） |
| R4 | 用户提议改为 `daoyi-lab`（取"道生一"之意） |
| R5 | V 审查发现：道一云（广州，腾讯投资，OA/SaaS，70万+客户）存在商业商标冲突 |
| R6 | V 审查发现：GitHub 上 `Dao-AILab`（FlashAttention 作者实验室）为近似名 |
| R7 | 用户要求基于帛书老子推荐更多名字 |
| R8 | 从帛书老子提取 8 个候选：boshu-lab、haomo-lab、pu-lab、chong-lab、weiming-lab、xuan-lab、xisheng-lab、xuantong-lab |
| R9 | 首推 `boshu-lab`（直接锚定马王堆帛书文本） |
| R10 | 用户提议 `baopu-lab`（见素抱朴） |
| R11 | V 审查发现：`baopu-lab.github.io` 已被 Dr. Bo Gao 的 AI 研究实验室占用（已发表 arXiv:2501.13428） |
| R12 | V 审查发现：天眼查 121 家"抱朴"相关企业（含上海抱朴信息、深圳抱朴科技等） |
| R13 | 用户反馈："boshu 太局限"（被锚定在具体文物上） |
| R14 | 重新框定：从"文本载体级"升级到"宇宙论级"开放概念 |
| R15 | 推荐 `huncheng-lab`（"有物混成，先天地生"） |
| R16 | 用户拍板 `huncheng-lab` |
| R17 | gh CLI v2.92.0 已登录（账号 xinetzone，token scopes: repo/read:org/workflow） |
| R18 | `gh api POST /orgs` 返回 404（普通用户无创建组织 API 端点） |
| R19 | 打开浏览器引导用户在网页完成组织创建 |
| R20 | 组织创建成功（id: 346140767，Free plan，created_at: 2026-10-22T02:50:04Z） |
| R21 | `gh repo create huncheng-lab/.github --public` 成功 |
| R22 | `git clone` 失败（github.com:443 连接超时） |
| R23 | 改用 `gh api PUT /repos/.../contents/profile/README.md` 直接创建文件 |
| R24 | 第一次用 `--input` 文件方式失败（PowerShell 写 JSON 带 BOM） |
| R25 | 改用 `-f` 命令行参数传递 base64，成功创建 profile/README.md（1698 bytes） |

## I · 核心洞察（四元组）

### 洞察 1：命名是"逐层去锚定"的收敛过程

| 维度 | 内容 |
|---|---|
| **陈述** | 从 xinetzone-lab → daoyi-lab → baopu-lab → boshu-lab → huncheng-lab，每一步都在解除上一个方案的锚定 |
| **证据** | R3（个人品牌锚定）→ R4-R6（商业商标锚定）→ R10-R12（GitHub已占用锚定）→ R13（文本载体锚定）→ R15（无锚定的宇宙论概念） |
| **反常识** | 用户最初以为要找"一个好名字"，实际需要的是"一个不被任何东西绑死的容器"——越抽象、越无具体指向的名字，越适合作为 demo/实验组织。有文化出处的名字反而最危险，因为有出处意味着已被使用 |
| **下次行动** | 未来做组织/品牌命名时，直接从"容器论/宇宙论"概念出发，不从个人品牌或具体典故出发。命名收敛路径：个人品牌 → 查冲突 → 换典故 → 查占用 → 去典故化 → 抽象概念 |

### 洞察 2：V 对抗审查在命名决策中的否决率是 75%

| 维度 | 内容 |
|---|---|
| **陈述** | 4 个候选名中 3 个被 V 阶段否决，只有最终方案通过 |
| **证据** | daoyi-lab（道一云商标冲突，R5）、baopu-lab（GitHub已占用+121家企业，R11-R12）、boshu-lab（用户判定格局局限，R13）全部否决；huncheng-lab 通过 |
| **反常识** | 直觉上"有文化出处、好记"的名字恰恰是被否决最多的——因为有文化出处意味着该词已被广泛使用，商标/GitHub/近似名撞车概率极高。最安全的名字反而是最抽象、最少人用的概念 |
| **下次行动** | 命名时先做可用性检查（GitHub 占用 + 商标搜索），再讨论文化含义。文化含义是最后一步的加分项，不是第一步的起点 |

### 洞察 3：GitHub 组织创建的自动化边界

| 维度 | 内容 |
|---|---|
| **陈述**： | gh CLI 能自动化 90% 的组织配置，但"创建组织"这 10% 必须人工网页操作 |
| **证据** | R18（POST /orgs 404）证明普通用户无创建组织 API；R20-R25 证明创建后所有配置（.github 仓库、profile README）都可以 API 化 |
| **反常识** | git clone 因 443 超时失败，但 gh api 成功——说明 gh CLI 走的网络栈（可能是 API 代理或不同的连接方式）和 git HTTPS 不同。网络受限时，Contents API 是最可靠的文件写入通道 |
| **下次行动** | 未来用 gh 操作 GitHub 时优先用 `gh api` 而非 `git clone/push`；网络受限时用 `gh api PUT /repos/.../contents/...` 直接写文件，base64 编码后用 `-f` 参数传递，避免文件 BOM 问题 |

## E · 可复用模式：GitHub 组织命名与 bootstrap 流程

详见萃取的 Skill：[`.agents/skills/github-org-bootstrap-cmd/SKILL.md`](../../../../.agents/skills/github-org-bootstrap-cmd/SKILL.md)

### 模式核心步骤

```
1. 场景识别：用户要创建组织管理某类项目
2. F·公理识别：组织 = 命名空间 + 权限容器，不是品牌本身
3. V·三维度审查：GitHub占用 / 商标冲突 / 格局开放度
4. I·命名收敛：个人品牌 → 商业冲突检查 → 文化典故 → 宇宙论抽象概念
5. C·创建落地：
   - 网页创建组织（API 不支持普通用户）
   - gh api 创建 .github 仓库
   - gh api PUT contents/profile/README.md 写组织主页
6. 治理规范：命名规范 + 状态徽章 + 归档规则 + 质量底线
```

### 反模式

- ❌ 从个人品牌直接派生组织名（会割裂未来品牌扩展）
- ❌ 选有文化出处的词不查商标（道一云/抱朴教训）
- ❌ 选两字母或常见词做组织名（GitHub 必被占）
- ❌ 试图用 git clone 写文件（网络受限时用 Contents API）
- ❌ 用 --input 传 JSON 文件（PowerShell BOM 问题，用 -f 参数）

## C · 原子行动项

| # | 行动项 | 状态 |
|---|---|---|
| C1 | 组织 huncheng-lab 已创建并上线 | ✅ 完成 |
| C2 | profile/README.md 已推送 | ✅ 完成 |
| C3 | 设置组织头像（混沌/漩涡风格） | ⏳ 待用户操作 |
| C4 | 迁移第一个现有 demo 到组织 | ⏳ 待用户操作 |
| C5 | 本报告落盘 + skill 入库 | ✅ 本次完成 |

## 关键链接

- 组织主页：https://github.com/huncheng-lab
- Profile README：https://github.com/huncheng-lab/.github/blob/main/profile/README.md
- 萃取的 Skill：`.agents/skills/github-org-bootstrap-cmd/SKILL.md`

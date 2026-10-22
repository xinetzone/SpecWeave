---
name: github-org-bootstrap-cmd
version: 1.0.0
description: "当用户要创建 GitHub 组织（Organization）管理个人项目/demo/实验，或提到'创建GitHub组织'、'建个org'、'组织名怎么起'、'demo组织'时，必须使用此技能。覆盖命名收敛（个人品牌→冲突检查→文化典故→抽象概念）、V 对抗审查（GitHub 占用/商标冲突/格局开放度）、gh CLI 自动配置（.github 仓库/profile README）、治理规范模板（命名规范+状态徽章+归档规则）与幂等重入保护。"
argument-hint: "<组织用途描述> [期望风格：个人品牌/文化典故/抽象概念]"
user-invocable: true
paths:
  - "playground/"
  - "AGENTS.md"
  - "docs/retrospective/reports/project-governance/"
title: "GitHub Organization Bootstrap 命令"
x-toml-ref: "../../../.meta/toml/.agents/skills/github-org-bootstrap-cmd/SKILL.toml"
---

# GitHub Organization Bootstrap 命令

> 从"想建个组织"到组织上线的完整流程：命名收敛 → 冲突审查 → 创建落地 → 治理配置。

## 1. 何时触发

- 用户说"创建 GitHub 组织 / Organization / 建个 org"
- 用户要管理多个 demo/实验/原型项目，需要独立命名空间
- 用户在纠结组织名/项目名/仓库名
- 用户已有 GitHub 组织但要配置 profile README 和治理规范

## 2. 命名收敛流程（F→V→I）

### Step 1：F·公理识别

先确认两个基本事实：

1. **组织 = 命名空间 + 权限容器**，不是品牌本身。它应该能装下各种类型的项目，不被名字绑死
2. **Demo/实验组织的本质是"未分化的容器"**——成熟项目会从这里分化出去成为正式仓库

> **为什么**先立公理再起名：绝大多数"名字不好听"的返工来自跳过公理直接造词，最后选出的名字只对当前一个项目成立，装不下第二个项目。公理把组织名从"品牌"重新定义为"容器"，评价标准随之从"够不够好听"变为"装不装得下"。

### Step 2：V·三维度审查

每个候选名必须过三关：

| 维度 | 检查方法 | 失败信号 |
|---|---|---|
| **GitHub 占用** | 搜索 `github.com/<name>` 和 `<name>-lab` | 已有组织/用户/仓库同名 |
| **商标/商业冲突** | 搜索"<中文名> 公司 科技 创业" | 已有科技公司使用该名（尤其腾讯/大厂投资的） |
| **格局开放度** | 问：这个名字能不能装下和当前方向完全不同的项目？ | 名字绑定了具体技术栈/文本/行业 |

> **为什么**要有文化典故这一路候选：因为"有出处"本身是好名字的来源，也是冲突的来源。命名收敛因此必须把"有出处"当成双刃信号而非直接加分项——被广泛引用的概念，GitHub 与商标系统里往往也已占位。

**否决率预期**：直觉上"有文化出处、好记"的名字 70% 会在这三关中被否决——因为有出处意味着已被广泛使用。

### Step 3：I·命名收敛路径

按以下顺序收敛，每步被否决就升级到下一步：

```
个人品牌派生（xinetzone-lab）
  ↓ 被 V 否决（品牌割裂/未来扩展受限）
文化典故（daoyi-lab / baopu-lab）
  ↓ 被 V 否决（商标冲突/GitHub占用）
文本载体锚定（boshu-lab）
  ↓ 被 V 否决（格局局限）
宇宙论抽象概念（huncheng-lab）← 最终推荐
```

> **为什么**最终收敛到宇宙论级抽象概念：它同时满足"不绑定技术栈/行业/文本"与"两到三个音节好拼好记"，且拼音组合非常见、GitHub 大概率可用。这是把格局开放度这一维度做到位后的自然解，而不是单纯取巧。

**最安全的名字特征**：

- 哲学/宇宙论概念（混成、观妙、若海、虚、渊）
- 不绑定具体技术栈、行业、文本
- 拼音非常见组合（GitHub 大概率可用）
- 两到三个音节，好拼好记

## 3. 创建落地流程（C）

### 关键限制：GitHub API 不支持普通用户创建组织

`gh api POST /orgs` 返回 404（仅 Enterprise 管理员可用）。**创建组织必须走网页**：

1. `Start-Process "https://github.com/organizations/new"` 打开浏览器
2. 引导用户填写：Organization name / Email / My personal account / Free plan
3. 等用户确认创建完成

> **为什么**不放行"脚本代建组织"的幻觉路径：`POST /orgs` 在普通账号下恒返回 404，这个错误码看起来像路径写错，容易被误判成接口变更而反复重试。明确锁死"网页创建 + CLI 配置"两段式，避免把 404 当信号错误去 debug。

### 创建后全自动配置

组织创建成功后，以下全部用 `gh api` 完成，**不要用 git clone**（网络受限时 443 会超时）：

```powershell
# 1. 创建 .github 仓库（组织 profile README 的特殊仓库）
gh repo create <org>/.github --public --description "Organization profile"

# 2. 准备 README 内容（UTF-8 无 BOM）
$readme = @'
# <Org Name>（中文名）
> 引用出处一句话

这里是 @<username> 的实验场...
'@
$bytes = [System.Text.Encoding]::UTF8.GetBytes($readme)
$b64 = [Convert]::ToBase64String($bytes)

# 3. 用 Contents API 直接写文件（不要用 --input，会 BOM）
gh api --method PUT /repos/<org>/.github/contents/profile/README.md `
  -f message="docs: add organization profile README" `
  -f content=$b64 `
  -f branch="main"
```

> **为什么**用 Contents API + base64 而不是 `gh api --input file.json`：PowerShell 的 `Out-File` 默认写 UTF-8 BOM，GitHub Contents API 对带 BOM 的 JSON 直接返回 400 JSON parse error，而错误信息里不会提 BOM，排查成本极高。base64 通道同时天然规避了命令行转义与 BOM 两个变量。

### 幂等重入保护

本 Skill 可被重复触发（用户改主意再跑一次），所有写操作前先探测现状，已达成则跳过而非重复创建：

| 操作 | 探测命令 | 已存在时的行为 |
|---|---|---|
| 创建组织 | `gh api /orgs/<name>` | 返回 404 才走网页创建；200 表示组织已在，直接进入配置阶段 |
| 创建 .github 仓库 | `gh api /repos/<org>/.github` | 200 则跳过 `gh repo create`，直接写 profile |
| 写 profile README | `gh api /repos/<org>/.github/contents/profile/README.md` | 已有则先比对内容哈希，一致则跳过写入，不一致才 PUT |

### 写操作预览门（dry-run 等价）

任何写操作前先输出"将要发生什么"的清单交用户确认，确认后才执行：

```
[预览] 组织名：<org>（V 审查结论：已通过 / 未通过）
[预览] 待创建仓库：<org>/.github（公开）
[预览] 待写入文件：<org>/.github/contents/profile/README.md
[预览] 已存在将跳过的对象：<列表>
```

> **为什么**建组织这类操作必须有预览门：组织创建是**不可回滚**的公开操作——名字一旦占位，商标与 GitHub 名义的冲突只能靠删除重建绕开，而删除后原名立即被他人抢占。把最终生效名单提前摊开给用户确认，是唯一能在不可逆动作前拦下错误名字的时机。

## 4. 治理规范模板

每个组织都应在 profile README 中定义以下四条规则：

### 4.1 边界铁律

明确"这是什么"和"这不是什么"——组织只放某一类项目，正式项目去另一个地方。

### 4.2 仓库命名规范

```
<type>-<主题>-<技术栈>
```

demo 组织统一 `demo-` 前缀，全小写连字符。

### 4.3 状态徽章约定

每个仓库 README 顶部标注：

- 🚧 WIP / ✅ Done / 📦 Archived / 🌟 Graduated

### 4.4 归档规则

- N 个月无提交自动归档
- 毕业项目在原仓库注明新地址

## 5. 安全检查清单（写操作质量门）

写操作执行前后逐项确认（每项须实际验证，不得凭印象打勾）：

- [ ] 已确认组织名通过三维度 V 审查（GitHub 占用/商标冲突/格局开放度）
- [ ] 已确认目标组织尚不存在（`gh api /orgs/<name>` 返回 404），避免误改同名既有组织
- [ ] 已验证 profile README 的 `content` 为 UTF-8 无 BOM 的 base64
- [ ] 已确认 `.github` 仓库的 `main` 分支存在且写入路径为 `profile/README.md`
- [ ] 已检查文档与仓库中的组织名、仓库名与实际创建结果一致，无残留占位符
- [ ] 已确认未向仓库写入任何 Token/私钥（gh CLI 凭据仅留在本地配置）
- [ ] 已确认未创建超出组织边界的仓库（demo 命名规范与归档规则已写入 profile）

## 6. 关联资源

- 实战复盘：[github-org-huncheng-lab-bootstrap-20261022.md](../../../docs/retrospective/reports/project-governance/github-org-huncheng-lab-bootstrap-20261022.md)
- gh CLI 官方文档：https://cli.github.com/manual/
- GitHub Contents API：https://docs.github.com/rest/repos/contents

## 7. Gotchas

以下是无错误码的隐性陷阱，与 §3 的"常见坑"不同——它们不报错，只是让结果悄悄偏离预期：

| # | 陷阱 | 反直觉行为 | 规避方式 |
|---|---|---|---|
| G1 | 组织名"存在"但不可见 | `gh api /orgs/<name>` 对未登录/无权限的私有组织返回 404，与"不存在"同码 | 创建前用浏览器登录态二次确认，而非只看 API 404 |
| G2 | `gh api --input` 的 BOM | PowerShell `Out-File` 写 JSON 带 BOM，服务端报 400 JSON parse error（与内容无关） | 改用 `-f` 逐字段传参，或 base64 通道 |
| G3 | git clone 443 超时但 gh api 通 | 两者走不同网络栈，clone 超时不代表 GitHub 不可达 | 全程用 `gh api`，不做 clone 试探 |
| G4 | `.github` 仓库默认分支不是 main | 建仓后默认分支可能是 `master`，PUT 指定 `branch=main` 会 404 | 建仓后先读默认分支名再传 `branch` |
| G5 | profile README 路径不是仓库根 | profile README 必须放 `profile/README.md`，放根目录不会显示在组织主页 | 固定写 `contents/profile/README.md` |
| G6 | 名字"有出处"反而更容易撞车 | 文化典故类候选名的 GitHub/商标占位率显著偏高，否决率约 70% | 把"有出处"当双刃信号，抽象概念作为兜底路径 |
| G7 | 重复触发导致重复建仓 | 用户改主意重跑时，若无探测直接 `gh repo create` 会撞名失败 | 按 §3 幂等表先探测后写 |

## 8. 常见错误处理

| 错误 | 解决方案 |
|---|---|
| `gh api --input file.json` 报 400 JSON parse error | PowerShell `Out-File` 写 JSON 带 BOM，改用 `-f` 参数直接传字段 |
| `git clone` 443 超时但 `gh api` 能通 | gh CLI 走不同网络栈，优先用 `gh api` 不用 git |
| `--jq ".field + 'string'"` PowerShell 报错 | 引号嵌套问题，直接看原始 JSON 输出 |
| `POST /orgs` 返回 404 | 普通账号无建组织权限（仅 Enterprise 管理员可用），改走网页创建 |

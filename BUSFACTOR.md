# 公交车因子应急手册（Bus Factor）

> **⚠️ 紧急文档**：如果核心维护者突然无法继续维护本项目（失联超过30天、健康原因、其他不可抗力），本文档提供接续维护所需的全部关键信息。
>
> **留余原则**：项目不应因任何单一个人的缺席而死亡。MIT协议赋予任何人fork的权利，本文档确保fork者或接续维护者能快速上手。

## 项目基本信息

| 项目 | 信息 |
|------|------|
| 名称 | SpecWeave |
| 定位 | AI智能体工作区规范体系（Agent Workspace Hub） |
| 开源协议 | MIT（见 [LICENSE](LICENSE)） |
| 主仓库 | https://github.com/xinetzone/SpecWeave |
| 国内镜像 | https://gitcode.com（镜像同步） |
| 文档站 | GitHub Pages（通过 `.github/workflows/docs-pages.yml` 自动部署） |
| 核心入口 | [AGENTS.md](AGENTS.md) |
| 编程语言 | Python 3.10+（脚本/工具）+ Markdown（规范文档） |

## 关键账号与权限

> **注意**：以下账号的凭据不在本仓库中存储。如果核心维护者失联，接续维护者应通过以下方式恢复访问：

| 平台/服务 | 用途 | 恢复方式 |
|-----------|------|---------|
| GitHub (`xinetzone/SpecWeave`) | 主仓库、Issues、PRs、CI/CD | 联系GitHub支持申请仓库所有权转移；或直接fork |
| GitCode 镜像 | 国内访问镜像 | 主仓库恢复后重新配置webhook同步；或手动fork |
| GitHub Pages | 文档站点 | fork后自动在新仓库的Pages中可用 |
| ReadTheDocs | 备用文档托管 | fork后在ReadTheDocs导入新仓库即可 |

## 紧急接续步骤

### 如果核心维护者失联 < 30天
1. 继续通过Issue/PR正常贡献，等待维护者回归
2. 协作者（Collaborators）可继续进行Issue分类和PR初步审查

### 如果核心维护者失联 ≥ 30天（项目接管流程）

**步骤1：确认失联**
- 在GitHub Issue中公开询问维护者状态
- 尝试通过GitHub个人资料中的联系方式（邮箱/社交）联系
- 等待30天无响应后进入步骤2

**步骤2：宣布接管意图**
- 在项目Issue中发一条标题为 `[TAKEOVER] Intent to maintain this project` 的Issue
- 说明自己的资质和维护计划
- 等待14天供社区反馈

**步骤3：Fork并继续维护**
```bash
# 1. Fork仓库到自己的GitHub账号
# 2. Clone fork
git clone https://github.com/<your-username>/SpecWeave.git
cd SpecWeave

# 3. 验证本地环境可用
python .agents/scripts/check-gitignore.py
python .agents/scripts/check-links.py --path .agents/

# 4. 运行现有测试（如有）
python -m pytest .agents/scripts/tests/ -v
```

**步骤4：更新文档**
- 更新 `MAINTAINERS.md` 中的维护者列表
- 在 `CHANGELOG.md` 中标注新维护纪元
- 在README顶部声明这是接续维护的fork（如适用）

## 发布流程（版本发布）

> 仅核心维护者或经授权的接续维护者执行。

```bash
# 1. 确保main分支所有检查通过
python .agents/scripts/ci-check.sh  # Linux/Mac
# 或
python .agents/scripts/ci-check.ps1 # Windows

# 2. 更新CHANGELOG.md，记录版本号和日期
# 3. 创建git tag
git tag -a v<version> -m "release: v<version>"
git push origin v<version>

# 4. GitHub Release
# 在GitHub Releases页面基于tag创建Release，附上CHANGELOG内容
```

## 🔴 绝对禁止事项（红线）

以下操作可能导致项目不可恢复的损坏，任何时候都不应执行：

1. **禁止force push到main分支** — 会丢失提交历史
2. **禁止修改LICENSE** — MIT协议不可变更，这是项目开源的基础
3. **禁止删除 `.agents/` 目录下的核心规范文件** — 这是项目的核心资产
4. **禁止向仓库提交密钥/令牌/密码** — pre-commit hook会检测，但也要人工确认
5. **禁止在未经讨论的情况下重写AGENTS.md路由结构** — 这是所有智能体的入口契约
6. **禁止直接修改 `vendor/` 子模块** — 这些是第三方依赖，应向上游贡献

## 关键文件索引（接续维护必读）

按优先级阅读，理解项目架构：

| 优先级 | 文件 | 说明 |
|--------|------|------|
| P0 | [AGENTS.md](AGENTS.md) | 项目最高优先级入口和路由表 |
| P0 | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | AI智能体快速装载指南 |
| P0 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 全局核心规则 |
| P1 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→规范映射表 |
| P1 | [.agents/roles/README.md](.agents/roles/README.md) | AI角色定义索引 |
| P1 | [.agents/scripts/README.md](.agents/scripts/README.md) | 自动化脚本索引 |
| P2 | [.agents/capability-registry.md](.agents/capability-registry.md) | 全量能力索引 |
| P2 | [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| P2 | [MAINTAINERS.md](MAINTAINERS.md) | 维护者清单 |
| P3 | [CHANGELOG.md](CHANGELOG.md) | 历史变更记录 |

## 本地开发环境

```bash
# 必需环境
# - Python 3.10+
# - Git
# - 无需数据库、无需后端服务

# 首次设置
git clone <repo-url>
cd SpecWeave

# 安装pre-commit hooks（推荐）
python .githooks/setup-hooks.py

# 验证环境
python .agents/scripts/check-gitignore.py
python .agents/scripts/check-links.py --path .agents/README.md
```

## CI/CD 流水线说明

| 工作流 | 触发条件 | 功能 |
|--------|---------|------|
| [docs-pages.yml](.github/workflows/docs-pages.yml) | push到main且docs/变更 | 构建Sphinx文档并部署到GitHub Pages |

> 目前CI较为精简。本地验证脚本（`check-links.py`、`check-margin.py`、`check-mermaid.py`等）构成了主要的质量门禁，见 [.agents/scripts/](.agents/scripts/)。

## 子模块说明

```bash
# 更新vendor子模块（如需更新第三方依赖）
git submodule update --remote vendor/
git add vendor/
git commit -m "chore(vendor): update submodules"
```

- `vendor/flexloop/` — FlexLoop第三方子模块
- `vendor/ark-cli/` — Ark-CLI第三方子模块
- `projects/xuanspace/` — 第一方子项目

> **注意**：不要直接修改子模块内容。如需修改，应在子模块的上游仓库提交PR，再更新submodule引用。

## 安全漏洞处理

1. 接收漏洞报告（私信/Issue marked as security）
2. **不要**在公开Issue中讨论漏洞细节
3. 私下（或通过GitHub Security Advisory）修复
4. 修复后发布版本，在CHANGELOG中标注安全修复（不泄露利用方式）
5. 给报告者致谢

## 项目健康度快速检查

接续维护后，运行以下命令确认项目状态：

```bash
# 1. 链接完整性
python .agents/scripts/check-links.py --path .

# 2. 敏感信息检测
python .agents/scripts/check-hardcode.py

# 3. Mermaid图语法
python .agents/scripts/check-mermaid.py

# 4. 四维留余评估（项目治理健康度）
python .agents/scripts/check-margin.py --non-interactive --scores "?,?,?,?"

# 5. 运行测试
python -m pytest .agents/scripts/tests/ -v
```

## 写在最后

本项目以MIT协议开源，这意味着它永远属于社区。如果原维护者无法继续，任何人都有权也有责任接续维护。

> *"留余的终极价值不是让你赢最多，而是让你活得最久。在无限游戏中，不下牌桌比赢下某一手牌重要一万倍。"*
> — 四维留余框架

---

> **关联文档**：
> - [MAINTAINERS.md](MAINTAINERS.md) — 维护者清单与职责
> - [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南
> - [AGENTS.md](AGENTS.md) — 项目入口与路由

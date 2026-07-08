---
source: "d:\\AI\\.chaos\\libs\\minitap-ai\\agent-skills"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task4-output.toml"
analysis_date: "2026-07-07"
task: "task4 - Agent Skill定义深度分析"
---
# Minitest AI Agent Skill 深度分析报告

## 1. 完整目录结构

`file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/` 目录结构如下：

```
agent-skills/
├── .git/                           # Git版本控制目录
├── .gitignore                      # Git忽略配置
├── README.md                       # 仓库级说明文档
└── skills/
    └── minitest-cli/
        ├── SKILL.md                # 核心Skill定义文件（YAML frontmatter + Markdown指令）
        ├── metadata.json           # Skill元数据（name/version/description/triggers）
        └── README.md               # Skill说明文档
```

**关键发现**：
- 无 `AGENTS.md` 文件存在
- 无 `references/` 目录（可选的支持文档目录）
- 单一Skill：`minitest-cli`，遵循 [Agent Skills](https://agentskills.io/) 标准格式
- 通过 `npx skills add minitap-ai/agent-skills` 安装

---

## 2. SKILL.md Frontmatter 格式与触发词设计

### 2.1 Frontmatter 结构

核心定义位于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:1-10`：

```yaml
---
name: minitest-cli
description: &gt;
  Use the minitest CLI to manage user stories, upload builds, execute test runs
  on virtual devices (simulators/emulators), and analyse results. Use when the user asks to test
  their mobile app, create test scenarios, run tests, check test results, or
  manage builds via the command line. Also use after any code change that
  affects UI, navigation, or user journeys to check if existing tests need
  to be updated.
---
```

### 2.2 触发词设计（metadata.json）

元数据位于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/metadata.json:15-25`：

```json
"triggers": [
  "minitest cli",
  "minitest command",
  "run mobile tests",
  "upload build",
  "test my app with cli",
  "minitest flow",
  "minitest run",
  "minitest apps create",
  "create minitest app"
]
```

**触发词分层设计**：
- **工具名触发**：`minitest cli`、`minitest command`、`minitest flow`、`minitest run`
- **动作触发**：`run mobile tests`、`upload build`、`test my app with cli`
- **API触发**：`minitest apps create`、`create minitest app`（具体子命令精确匹配）

**description 触发场景覆盖**：
1. 显式请求：测试移动应用、创建测试场景、运行测试、检查结果、管理构建
2. 隐式触发：代码变更影响UI/导航/用户旅程后，检查现有测试是否需要更新

---

## 3. Onboarding Playbook 设计（minitest init引导全流程）

### 3.1 入口命令

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:26-53`：

```bash
minitest init            # 打印端到端onboarding playbook（管道/非交互时输出原始markdown）
minitest init --agent    # 强制原始markdown输出，无论上下文
```

### 3.2 Playbook 执行阶段

Playbook 按顺序引导完成以下步骤：
1. **认证**：`minitest auth login`（浏览器OAuth）
2. **查找/创建应用**：`minitest apps list` / `minitest apps create`
3. **定义Personas（测试Profile）**：为每个角色/订阅层级创建测试配置文件
4. **映射用户旅程**：枚举所有关键用户路径（happy path + 失败路径）
5. **创建带依赖关系的场景**：使用 `--depends-on` 声明DAG依赖
6. **上传虚拟设备构建**：上传模拟器/兼容的 `.apk`/`.ipa`
7. **运行测试套件**：执行全量测试

### 3.3 Playbook 依赖的关键约定

| 约定项 | 规则 | 来源 |
|---|---|---|
| 路径覆盖 | 枚举所有真实需要的关键用户旅程，不仅是示例；覆盖happy path和失败状态（验证错误、权限拒绝、空状态、边缘情况） | SKILL.md:42-47 |
| 离线场景 | 使用 "Offline (wifi off)" 表述，**禁止**写 "airplane mode"（云测试设备无飞行模式） | SKILL.md:48-49 |
| 文件预置 | 需要设备文件时，先 `minitest test-file upload`，再用 `minitest user-story-binding set-files` 绑定 | SKILL.md:50-51 |
| 验收标准 | 面向目标（job to be done），不是微步骤 | SKILL.md:46-47 |

---

## 4. 测试 Profile 与 Persona 设计

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:195-222`，共四种模式：

### 4.1 模式一：@qa.minitap.ai 共享收件箱OTP自动读取（默认推荐）

```bash
minitest --app $APP test-profile create \
  --name "Pro User" --username "pro@qa.minitap.ai" \
  --about "Pro subscription active, has saved items, payment method on file"
```

**设计要点**：
- 用户名格式：`<prefix>@qa.minitap.ai`，**不设置密码**
- 所有 `@qa.minitap.ai` 地址邮件投递到共享收件箱
- 测试Agent运行时自动读取登录/验证码，无需管理真实凭证
- 留空username则自动生成
- 非 `@qa.minitap.ai` 且无密码会被拒绝

### 4.2 模式二：BYO账户（Bring Your Own）

当用户提供真实账户且应用需要密码时使用：

```bash
printf "%s" "$PASSWORD" | minitest --app $APP test-profile create \
  --name "Pro User" --username "real-user@example.com" --password-stdin --about "..."
```

**设计要点**：
- 通过stdin传递密码，避免shell历史记录泄露
- `--password` 内联值会被shell日志记录，不推荐
- 两个密码标志互斥

### 4.3 模式三：特定状态账户预配置（如Premium）

```bash
# 创建带密码的 @qa.minitap.ai persona
# 然后请用户将该 email+password 在后端关联到pro/特定状态账户
```

**设计要点**：
- 使用 `<something>@qa.minitap.ai` + 显式密码
- `@qa.minitap.ai` 保持收件箱可读（用于OTP）
- 密码让用户可以预配置账户状态
- 用户需在后端完成账户状态关联

### 4.4 模式四：无Persona绑定（匿名模式）

**设计要点**：
- Story无profile时，Agent默认为匿名（跳过登录）
- 如果流程强制认证，运行时自生成 `<random>@qa.minitap.ai` + 临时密码
- 自动注册并读取收件箱获取确认/OTP码
- 无需预先配置即可运行未绑定场景

### 4.5 补充机制

- **默认Profile**：`test-profile set-default <profile_id>`，省略 `--profile` 时自动绑定
- **第三方OAuth**：使用Minitap共享账户池绑定到对应Story（也是 `@qa.minitap.ai` 域）
- **about字段**：注入测试Agent运行时prompt，描述profile的差异化特征
- **绑定时机**：创建时用 `--profile`，创建后用 `user-story-binding set-profile`

---

## 5. 用户故事验收标准四条规则

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:229-234`：

| 规则编号 | 规则 | 详细说明 |
|---|---|---|
| 1 | **视觉可验证** | 必须是Agent在屏幕上能看到的内容（Agent仅能看到屏幕） |
| 2 | **具体明确** | 必须specific且unambiguous，无歧义 |
| 3 | **单断言** | 每个criterion只包含一个断言（One assertion per criterion） |
| 4 | **时间顺序** | 按照旅程中出现的先后顺序排列 |

**版本化机制**（SKILL.md:248-251）：
- `--criteria` 是完整替换：未变内容保持身份（稳定 `criterionId`），修改内容创建新版本，删除项软删除
- `--add-criteria` 仅追加

---

## 6. Story Types 枚举

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:183-188`：

```
login, registration, onboarding, search,
settings, navigation, form, profile, other, custom
```

**受限类型（禁止创建）**：
- `checkout`、billing、payment - 涉及真实交易，尚不支持
- 代码分析阶段跳过这些类型并告知用户

**验证机制**（SKILL.md:276-292）：
```bash
minitest flow-types list          # 列出有效值，每行一个
minitest --json flow-types list   # JSON数组，便于管道到jq
```
- 编程式生成user story时，先调用此接口验证 `--type` 值
- 无效值非零退出
- 后端无公开写端点，新增类型需要后端变更

---

## 7. --depends-on DAG 依赖

### 7.1 创建时声明依赖

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:172-181`：

```bash
minitest --app &lt;app_id&gt; user-story create \
  --name "View Order History" \
  --type navigation \
  --depends-on &lt;login_story_id&gt; \
  --criteria "The order history screen is displayed"
```

`--depends-on` 可重复使用声明多个父依赖。

### 7.2 更新时管理依赖

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:253-274`：

| 操作 | 命令 | 说明 |
|---|---|---|
| 完整替换依赖集 | `--depends-on &lt;id1&gt; --depends-on &lt;id2&gt;` | 全量替换，省略的父项会被移除 |
| 移除单个依赖 | `--remove-dependency &lt;parent&gt;` | 外科手术式delta，仅移除指定项 |
| 清除所有依赖 | `--depends-on ""` | 传空列表 |

**互斥规则**：同一调用中 `--depends-on` 和 `--remove-dependency` 互斥，同时提供时 `--remove-dependency` 被忽略。

### 7.3 依赖图可视化

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:112-129`：

```bash
minitest apps dependencies &lt;app_id&gt;                    # Mermaid flowchart TD输出（LLM友好）
minitest --json apps dependencies &lt;app_id&gt;             # 原始图JSON（nodes + edges）
minitest --app &lt;app_id&gt; apps dependencies              # 使用全局--app标志
```

- 输出 `flowchart TD` 格式
- 每个节点标签为 `"Story Name\n(type)"`
- 有向边表示依赖关系（parent → child）

---

## 8. CI/自动化使用模式

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:409-435`，核心机制：

### 8.1 JSON 管道模式

| 特性 | 说明 |
|---|---|
| 全局标志 | `--json`：camelCase JSON到stdout，诊断信息到stderr |
| 安全管道 | 可安全pipe到jq等工具 |
| 示例 | `minitest --json user-story list \| jq '.items[].name'` |

### 8.2 环境变量配置

```bash
export MINITEST_APP_ID="&lt;app_id&gt;"
export MINITEST_API_KEY="${{ secrets.MINITEST_API_KEY }}"  # CI中推荐
```

**认证优先级**（SKILL.md:57-63）：
1. `MINITEST_TOKEN` - 原始bearer覆盖（遗留，通常不设置）
2. `MINITEST_API_KEY` - 租户范围 `mtk_…` key，CI/脚本推荐
3. `minitest auth login` - 交互式OAuth

### 8.3 Env Set 安全模式

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:507-540`：

| 机制 | 说明 |
|---|---|
| 显式确认 | 所有变更命令（`set`/`unset`/`clear`）需要 `--yes`/`-y`，否则拒绝 |
| Dry Run | `--dry-run` 打印diff（`+`/`~`/`-`）但不修改后端 |
| 读-合并-写 | set/unset获取当前集合，应用变更，发回全量map，不覆盖其他key |
| 掩码默认 | `env list` 默认掩码为 `********`，`--show` 显示全部 |
| 单值暴露 | `env get &lt;KEY&gt;` 逐字打印单个值到stdout（可安全脚本赋值） |

```bash
minitest --app $APP env set API_TOKEN abc123 --yes
minitest --app $APP env set API_TOKEN abc123 --dry-run   # 仅显示diff
```

### 8.4 --yes 非交互模式

所有可能产生副作用的写操作都需要 `--yes` 标志：
- env set/unset/clear
- 其他破坏性操作（如delete需要 `--force`）

防止Agent或CI作业意外修改secrets。

### 8.5 --no-watch Fire-and-Forget模式

```bash
minitest --app &lt;app_id&gt; --json run start "User Login" \
  --ios-build &lt;id&gt; --android-build &lt;id&gt; \
  --no-watch    # 立即返回runId，CI中有用
```

### 8.6 Test File 绑定机制

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:490-505`：

```bash
# 上传测试文件（最大25MB，支持image/video/audio/document/other）
minitest --app ID test-file upload ./local/file.pdf --note "..."

# 原子替换绑定到story（全量替换，省略的id被解绑）
minitest --app ID user-story-binding set-files &lt;story_id&gt; --file &lt;id&gt; --file &lt;id&gt;

# 清除所有绑定
minitest --app ID user-story-binding set-files &lt;story_id&gt; --clear
```

用例：头像照片、示例PDF、录音等Story依赖的文件在Agent运行前推送到设备。

### 8.7 CI 完整示例

```bash
export MINITEST_APP_ID="&lt;app_id&gt;"

minitest --json build upload ./app.apk
minitest --json build upload ./MyApp.ipa

IOS_BUILD=$(minitest --json build list --platform ios --page-size 1 | jq -r '.[0].id')
ANDROID_BUILD=$(minitest --json build list --platform android --page-size 1 | jq -r '.[0].id')

minitest --json run all \
  --ios-build "$IOS_BUILD" \
  --android-build "$ANDROID_BUILD"
```

---

## 9. CLI-Skill 配对 PR 同步机制

从文档结构分析，CLI与Skill的协同设计如下：

### 9.1 单一来源原则

- SKILL.md 作为AI Agent使用CLI的权威指令源
- `minitest init --agent` 输出与SKILL.md一致的原始markdown
- CLI子命令与Skill文档一一对应：每个CLI命令在Quick Reference表中有条目

### 9.2 版本同步隐含机制

- Skill `version: "1.0.0"`（metadata.json:3）
- CLI通过 `minitest flow-types list` 动态获取有效类型，避免硬编码枚举过时
- CLI退出码标准化（0/1/2/3/4），便于Skill/脚本可靠处理

### 9.3 双入口设计

- **MCP入口**（minitest skill，README.md:7提及）：直接管理flow templates
- **CLI入口**（本skill）：通过命令行驱动相同工作流，MCP不可用或CI/自动化场景使用

---

## 10. Quick Reference 表维护要求

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md:437-488`，包含29项命令：

### 10.1 表结构规范

| 列 | 说明 |
|---|---|
| Task | 任务描述，简洁动词短语 |
| Command | 完整命令模板，包含必要参数和可选标志 |

### 10.2 条目覆盖范围分类

| 分类 | 条目数 | 包含项 |
|---|---|---|
| 应用管理 | 3 | Onboard、List apps、Create app、Dependency graph |
| 用户故事 | 7 | Create (with/without profile)、List、Update、Set dependencies、Remove dependency |
| 配置/知识 | 3 | Flow types、App knowledge get/update |
| 环境变量 | 4 | List、Reveal、Set、Remove、Clear |
| 构建管理 | 2 | Upload、List |
| 测试运行 | 6 | Run one、Run all、Cancel、Check status、List runs |
| 批次管理 | 3 | List、Get with runs、Cancel |
| 认证 | 4 | Login、Mint/List/Revoke API key |
| 测试Profile | 6 | List、List shared、Create、Set default、Clear default、Update、Delete |
| 测试文件 | 5 | List (by kind)、Upload、Get (download URL)、Update、Delete |
| Story绑定 | 3 | Bind profile、Clear profile、Bind files、List files |

### 10.3 维护要求（隐含约定）

1. **新增CLI子命令必须同步添加Quick Reference条目**
2. **命令标志变更必须同步更新模板**
3. **参数顺序保持一致**：`--app ID` 位置固定
4. **可选参数用方括号 `[...]` 标注**
5. **互斥标志需在描述中说明**

---

## 11. Conventions 关键约定汇总

### 11.1 构建约定（SKILL.md:320-332）

| 平台 | 要求 |
|---|---|
| iOS | **Simulator build**（`.ipa`，为iOS Simulator目标构建，非物理设备） |
| Android | **x86_64兼容 `.apk`**，Gradle构建需包含x86_64 ABI |

- 仅支持 `.apk` 和 `.ipa`，从扩展名自动检测平台
- 上传仅设备构建（如arm64 iOS归档或arm-only Android APK）会导致测试运行失败

### 11.2 密码安全约定（SKILL.md:542-553）

- 优先 `--password-stdin` 通过管道传入，禁止在命令行直接传密码（避免shell历史）
- `--password` 和 `--password-stdin` 互斥
- 清除已有密码用 `update --clear-password`

### 11.3 退出码约定（SKILL.md:93-101）

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General error |
| 2 | Authentication required |
| 3 | Network / API error |
| 4 | Resource not found |

### 11.4 全局标志约定（SKILL.md:86-92）

| Flag | Effect |
|---|---|
| `--json` | camelCase JSON到stdout，诊断到stderr - 适合管道 |
| `--app &lt;id&gt;` | 目标应用（覆盖 `MINITEST_APP_ID`），必须出现在子命令**之前** |

### 11.5 多租户约定（SKILL.md:131-151）

- 认证用户属于单租户时CLI自动解析
- 多租户非交互上下文（CI、管道调用）必须显式传 `--tenant &lt;id&gt;`，否则退出1
- `apps list` 在JSON模式暴露现有租户ID

### 11.6 API Key生命周期约定（SKILL.md:65-84）

- `mtk_` key可创建和撤销，但不会过期
- 轮换流程：mint新key → 更新CI/orchestrator中的secret → revoke旧key
- 与 `MINITEST_TOKEN` 同时设置时，`MINITEST_TOKEN` 优先，每进程一次stderr警告
- 视为凭证，禁止commit，怀疑泄露时轮换

### 11.7 输出约定

- JSON模式：stdout输出camelCase（匹配后端API），stderr输出诊断
- 非JSON模式：人类可读输出
- `init --agent` 强制原始markdown输出，便于Agent机器处理

---

## 12. 文件引用索引

| 文件 | 用途 |
|---|---|
| `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/README.md` | 仓库根说明，安装方法 |
| `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/.gitignore` | Git忽略配置 |
| `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/SKILL.md` | 核心Skill定义（553行完整指令） |
| `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/metadata.json` | Skill元数据与触发词 |
| `file:///d:/AI/.chaos/libs/minitap-ai/agent-skills/skills/minitest-cli/README.md` | Skill级说明文档 |

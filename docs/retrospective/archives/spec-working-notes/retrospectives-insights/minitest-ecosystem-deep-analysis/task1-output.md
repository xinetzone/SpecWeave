---
id: "minitest-ecosystem-deep-analysis-task1"
title: "Minitest生态系统深度分析 - 官方文档系统梳理"
source: "https://www.minitap.ai/docs/minitest"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task1-output.toml"
generated_at: "2026-07-07"
analysis_scope:
  - 产品首页
  - Meet Mini
  - Quickstart
  - Anatomy of your suite
  - Run report
  - Builds
  - Triggering a run
  - Mini maintains your suite
  - Suggestions
---
# Minitest官方文档深度分析报告

## 一、产品定位

### 1.1 核心价值主张

**Minitest是面向移动应用（iOS/Android）的AI驱动自动化QA测试平台，为没有专门QA团队的开发团队提供无需雇佣QA人员即可获得的移动端测试覆盖率。**

- **目标用户**：正在发布iOS或Android应用但没有自有QA团队的开发团队
- **核心角色**：Mini - 一个AI QA工程师智能体
- **产品本质**：AI Agent驱动的端到端自动化测试平台

### 1.2 产品愿景

让每个移动应用团队都能拥有专业QA工程师的测试能力，无需组建专门的QA团队。通过AI智能体自主运行用户故事测试，在虚拟设备上执行测试用例，并给出明确的测试结论。

---

## 二、Mini AI Agent能力详解

Mini是驱动整个测试流程的核心AI智能体，具备以下全方位能力：

### 2.1 测试套件自主维护能力

Mini能够持续维护测试套件与代码库的同步，解决"测试套件易编写但难维护"的痛点：

| 维护层级 | 能力描述 | 具体表现 |
|---------|---------|---------|
| **微观漂移修复** | 小范围UI变更适配 | 按钮重命名、标签调整、表单顺序变化时自动重写验收标准以匹配当前界面 |
| **宏观漂移处理** | 功能级变更适配 | 功能被移除时自动下线相关故事；新功能发布时自动起草新的测试故事 |
| **连接组织** | 测试依赖自动管理 | 自动建立故事间的依赖关系；自动将已有配置文件关联到需要的测试旅程 |

**工作机制**：
- 持续监控默认分支（通常是main）的代码变更
- 检测到有意义的diff时在后台自动更新测试套件
- 无需人工触发，无需逐次审查变更，团队只需持续交付代码

**需要人工介入的场景**：
1. **新增配置文件（Profiles）**：当新旅程需要新身份（如Pro用户测试付费墙、Admin用户测试设置页面），需要人工提供凭证
2. **设备文件**：照片、PDF、音频等仓库外的文件需要手动附加

### 2.2 虚拟设备执行能力

- **运行环境**：每次测试运行都在虚拟iOS或Android设备上执行
- **构建来源**：直接从GitHub构建应用，无需人工管理构建产物
- **登录能力**：使用附加到每个故事的配置文件自动登录
- **Google登录**：使用Minitap维护的共享Google账户，无需自行准备测试账号

### 2.3 问题发现与报告能力

当发现问题时，Mini提供可直接行动的完整信息：

1. **失败场景的设备操作视频录像**
2. **精确失败的验收标准**
3. **可直接粘贴到Cursor或Claude的修复提示词（Fix Prompt）**
4. **相关设备日志**（当日志有助于解释失败原因时自动提取）

### 2.4 主动发现能力（Suggestions）

Mini在执行预定测试之外，还会主动发现测试范围外的问题：
- UX细节问题
- 损坏的边缘情况
- UI不一致性
- 文案表达问题
- 产品层面的功能行为观察

这些作为**建议（Suggestions）**呈现，独立于正式问题，不阻塞发布，供团队选择性处理。

### 2.5 多界面触达能力

Mini在多个工作场景中与团队交互：

| 触达渠道 | 功能范围 |
|---------|---------|
| **Dashboard（仪表板）** | 编写故事、监控运行、分类问题的主界面 |
| **Slack** | 每次运行实时心跳通知，直接在线程中进行问题分类 |
| **Pull Request** | 每个PR上的miniTest检查，绿色表示套件在该构建上通过 |
| **IDE（Cursor/Claude）** | 通过MCP服务器在IDE中编写和编辑用户故事 |

---

## 三、User Story与Acceptance Criteria模型

### 3.1 User Story（用户故事）结构

一个用户故事代表应用中的一段完整用户旅程，是Mini执行测试的脚本和断言列表。

**核心字段**：

| 字段 | 说明 | 示例 |
|-----|-----|-----|
| **Name（名称）** | 简短的动作导向标题 | `Sign in with email`、`Add item to cart` |
| **Type（类型）** | 旅程分类，用于图标、颜色和分组 | 内置类型 + 自定义类型 |
| **Description（描述）** | 一句话描述用户目标 | "A returning user signs in and reaches the home screen." |
| **Acceptance Criteria（验收标准）** | Mini在运行时评分的可观察条件列表 | 见下文详细说明 |

**内置故事类型**：
- Login（登录）
- Registration（注册）
- Checkout（结账）
- Onboarding（引导）
- Search（搜索）
- Settings（设置）
- Navigation（导航）
- Form（表单）
- Profile（个人资料）
- Other（其他）

**自定义类型**：
- 可创建自定义类型，包含名称、图标、颜色
- 可选的使用提示词，在该类型故事运行时注入Mini上下文
- 典型自定义类型：Payment、Reservation、Loyalty等
- 类型仅用于分类，不自动选择配置文件，也不改变评分严格度

### 3.2 Acceptance Criteria（验收标准）规则

每个验收标准是一条可观察条件，用平实的英文短句书写。Mini端到端执行旅程后，根据观察到的情况对每条标准判定PASS或FAIL。

**三条黄金规则**：

1. **一行一条件**：如果一个步骤做两件事，拆分它
2. **像用户一样说话**：用用户看到的方式引用UI元素，而非无障碍ID
3. **跳过输入步骤**：附加配置文件时，写登录后的状态标准（如"显示已登录用户的主屏幕"），Mini已有凭证完成登录

**示例**：
```
1. The home screen is displayed.
2. The "Cart" button shows a badge with "1".
3. Tapping "Checkout" opens the address form.
```

**版本管理**：
- 编辑标准会创建新版本
- 已有问题绑定到其评分时的版本，修改措辞不会破坏分类历史
- 删除标准会自动解决其关联的未结问题

### 3.3 可附加配置项

除四个基础字段外，三个可选配置项塑造Mini运行故事的方式：

#### 3.3.1 Profiles（配置文件/测试身份）

当故事需要登录时使用的命名身份。附加到故事后，Mini每次运行都使用该身份。

**典型配置**：大多数应用需要少量配置文件——免费用户、专业用户、管理员（如果旅程不同）。

**创建配置文件**：
路径：App settings → Test Data → Profiles → New profile

字段：
- **Name**：引用名称（如`Free user`、`Pro user`、`Admin`）
- **Username**：邮箱、电话或登录界面接受的任何凭证
- **Password**：静态加密存储，不再显示，不会出现在运行报告或Slack中
- **About this user**：Mini作为上下文读取的自由格式备注（账户状态、权益、特殊事项）

也可通过MCP服务器在IDE中创建。

**Google登录**：
- 应用使用Google登录时无需自行准备测试账户
- Minitap管理一组共享Google账户，在配置文件选择器的"Shared by Minitap"下显示

**最佳实践**：
- 按角色而非按人配置：使用专用测试用户，不要使用个人账户
- 失败运行可能使账户处于异常状态（未完成结账、放弃购物车），避免污染真实用户账户

#### 3.3.2 Files（文件）

当旅程需要上传、附加或引用用户提供内容时使用（头像、PDF收据、短音频片段等）。

- Mini在运行开始前将文件预加载到测试设备
- 智能体从设备相册、文件应用或文档选择器中取用，与真实用户操作方式一致
- 支持类型：图片、文档、视频、音频
- 可从仪表板的故事详情附加，或在IDE中通过MCP服务器附加

#### 3.3.3 Dependencies（依赖关系）

故事可以依赖其他故事。当父故事失败时，其依赖项在该次运行中被跳过，而不是重跑已知损坏的旅程（例如：登录失败时没必要检查结账）。

- 在故事详情中设置依赖
- 完整依赖图显示在依赖视图中

### 3.4 编写渠道

可在三个界面编写用户故事：
1. Cursor或Claude（通过MCP服务器/CLI）
2. Slack（通过@mini交互）
3. Dashboard仪表板

---

## 四、测试执行流程

### 4.1 构建（Builds）环节

每次运行使用应用的真实构建，在虚拟设备上运行。有两种构建提供方式，可按应用混合使用：

#### 方式一：Mini自动构建（推荐）

连接仓库后Mini代为构建。当运行需要新产物时，拉取正确commit，为iOS和Android编译，将二进制文件交给测试设备。

**前置条件**：
- 组织上安装MiniTest GitHub App
- 配置应用编译所需的构建环境变量

**Monorepo支持**：在App Settings → Builds中指向包含移动应用的子文件夹。

**PR检查支撑**：此路径支撑PR检查功能——PR打开时Mini构建head commit，运行套件，将结论回贴到PR。

**Expo应用优化**：支持repack builds——仅JS bundle变化时增量重建复用原生shell。当日首次构建是完整构建，后续构建快速完成。

**构建环境变量**：
- 大多数移动构建需要至少一个环境变量才能干净编译：API base URL、Sentry DSN、功能开关覆盖等
- Mini按应用存储，构建时注入
- 配置路径：App Settings → Builds → Environment Variables
- 静态加密存储，仅在构建环境内解密
- 不出现在仪表板日志、运行报告或修复提示词副本中

#### 方式二：自行上传构建

在笔记本、Bitrise、Codemagic或任何地方自行构建，通过CLI推送产物：

```shell
minitest build upload ./path/to/build.ipa
minitest build upload ./path/to/app-debug.apk
```

- CLI打印可在运行中定位的构建ID
- 适用于一次性检查和构建流水线在GitHub外的应用
- 此方式不应用构建环境变量——产物中已包含

#### 构建选择

- 仪表板触发运行时：使用配置分支的**最新**构建（默认）；或选择**特定commit**或构建ID
- CI触发的运行：始终使用触发commit产生的构建，PR门禁时无手动选择

#### Web预览URL

运行Web构建时，Mini部署到生成的预览主机，可打开和分享：
- 格式：`<preview_key>--<tenant_slug>.preview.minitap.ai`
- 自动注入环境变量：`MINITAP_PREVIEW_URL`
- OAuth配置：需添加通配符域名 `*--<tenant_slug>.preview.minitap.ai` 到提供商

### 4.2 运行触发方式

共有四种触发运行的方式，适配不同工作场景：

#### 方式一：Dashboard手动触发

在任意应用页面点击**Run tests**，侧边面板引导两步：
1. **选择构建**：使用配置分支最新构建、选择特定commit/构建ID、上传新.apk/.ipa、粘贴PWA URL
2. **选择故事**：运行**全部**（默认）或从可搜索列表缩小到子集

点击Start run后Mini在下一个可用设备上排队，Runs标签实时更新。

**适用场景**：演示前一次性检查、验证刚推送的修复、对来自第三方CI的构建进行健全性检查。

#### 方式二：Slack触发

通过`@mini`触发，无斜杠命令。

**内联输入运行**：提及Mini并指定应用和构建标签：
```
@mini run acme-checkout v1.4.2
```
Mini发布临时确认消息（10秒取消窗口）后启动。心跳发送到该应用配置的频道。

**打开选择器引导流程**：
```
@mini run all tests
```
Mini发布交互式消息，引导完成应用→构建→故事→确认流程。

**前置条件**：Slack用户需链接到Minitap账户。

#### 方式三：GitHub Actions CI触发（PR检查）

支撑PR检查的路径，一次配置后Mini在每个PR上运行套件：构建head commit、运行故事、将结论回贴到PR。

**配置方法**：在仓库中添加工作流文件，调用`minitap-ai/minitest-trigger` GitHub Action：

```yaml
name: miniTest

on:
  pull_request:
    branches: [main]

jobs:
  run-suite:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # OIDC认证必需
      contents: read
    steps:
      - uses: minitap-ai/minitest-trigger@v1
        with:
          app-slug: my-app
```

将文件放入`.github/workflows/`，推送到默认分支即完成配置。

**默认行为**：构建head commit、运行所有故事、在PR上发布检查和粘性评论。

**可选配置参数**：`run-ios`、`run-android`、`ios-build-path`、`android-build-path`、`user-story-types`、`tenant-id`、`cancel-previous-runs`等。

**PR门禁配置**：
- 默认PR检查是**信息性**的
- 要求Mini通过才能合并：在工作区设置启用`block_on_test_failures`，并将检查添加到GitHub分支保护规则的必需状态检查中

**重跑方式**：
- 切换粘性PR评论中的**Run tests**复选框
- 在PR评论中发布`/test`
- 在仪表板运行报告上点击**Re-run**

#### 方式四：CLI触发

两个命令，按作用域区分：

**单个故事**：
```shell
minitest run start <user-story-id> \
  --ios-build <build-id> \
  --android-build <build-id>
```

**整个套件**：
```shell
minitest run all \
  --ios-build <build-id> \
  --android-build <build-id>
```

两个命令都接受`--watch`参数，将状态流式传输到终端，而非打印运行ID后退出。

**前置操作**：执行一次`minitest auth login`登录。

### 4.3 测试执行完整流程

```
代码变更/手动触发
    ↓
构建获取（Mini自动构建/自行上传/CI构建）
    ↓
虚拟设备准备（iOS/Android）
    ↓
文件预加载（如果配置）
    ↓
按依赖顺序执行用户故事
    ├─ 使用配置文件自动登录
    ├─ Mini自主操作UI完成旅程
    ├─ 实时采集设备视频
    ├─ 采集设备日志
    └─ 对照验收标准逐项判定
    ↓
生成运行报告
    ├─ 每个故事的结论（Passed/Warning/Failed/Unprocessable）
    ├─ 每个验收标准的判定
    ├─ 失败时刻截图
    ├─ 完整操作视频+时间线
    ├─ 相关设备日志
    └─ 失败项生成Fix Prompt
    ↓
结果分发（Dashboard/Slack/PR检查）
    ↓
主动发现问题 → Suggestions收件箱
```

---

## 五、结果类型与交付物详解

### 5.1 Verdict结论类型

运行报告是单故事视图：一个用户故事、一个构建、一个设备。从运行视图点击任意行打开。

| 结论类型 | 含义 | 处理方式 |
|---------|-----|---------|
| **✅ Passed（通过）** | 所有关键标准都成立 | 构建可安全发布 |
| **⚠️ Warning（警告）** | 所有关键标准成立，但至少一个警告标准不成立 | 需要关注但不阻塞发布 |
| **❌ Failed（失败）** | 至少一个关键标准不成立 | 存在bug，需要修复 |
| **⚙️ Unprocessable（无法处理）** | Mini运行了故事但无法评分 | 测试前就出问题了，需要排查前置问题 |

前三种是需要分类的正常结果，Unprocessable表示测试甚至没有机会正常执行。

#### Unprocessable常见原因：
1. **构建损坏**：无法安装、启动崩溃、包格式错误 → 打开构建面板使用其fix prompt
2. **登录失败**：Mini无法通过认证，下游无法测试 → 为用户故事附加可用的配置文件
3. **标准与应用不匹配**：通常是从其他应用复制的故事，或要求应用不具备的功能 → 编辑故事
4. **故事中途硬阻塞**：流程早期问题导致所有剩余标准无法到达 → 阅读第一个失败的标准

**排查提示**：如果同一构建上多个故事反复出现Unprocessable，先怀疑构建而非测试套件。

### 5.2 验收标准状态

每个标准显示状态和智能体的证据：

| 状态 | 说明 |
|-----|-----|
| **✅ Passed** | 智能体观察到的匹配内容 |
| **❌ Failed** | 期望vs实际观察到的内容，失败时刻固定截图 |
| **⚠️ Warning** | 非关键标准不成立 |

点击任意标准可跳转到视频中对应时刻。

### 5.3 核心交付物

#### 交付物一：视频+时间线（Video + timeline）

- 智能体操作应用的连续录像
- 下方时间线标记每个标准的开始/结束
- 可直接擦洗定位到失败位置

#### 交付物二：修复提示词（Fix Prompt）

每个失败标准暴露**Copy fix prompt**按钮。提示词是Mini在运行故事时编写的可直接粘贴文本块，包含三部分：

1. **根本原因（Root cause）**：出了什么问题以及原因
2. **复现步骤（Steps to reproduce）**：智能体进入失败的路径
3. **具体修复建议（Concrete proposed fix）**：起点而非最终答案

直接粘贴到Cursor或Claude Code中。IDE已有代码库其余部分作为上下文，fix prompt加上下文通常足以让智能体开出PR。

**设计特点**：fix prompt刻意使用纯文本——无截图URL、无日志转储。视频和上方标准详情已覆盖证据；fix prompt是交给IDE的内容。

**构建修复提示词**：当构建本身编译或安装失败时（不同于健康构建上的故事失败），构建状态面板暴露自己的**Copy fix prompt**按钮，结构相同：根本原因、复现、建议修复。适用于运行因构建从未安装到设备而显示Unprocessable的场景。

#### 交付物三：设备日志（Device logs）

当设备日志有助于解释失败时，Mini自动提取并纳入报告。

#### 交付物四：复现路径（Repro steps）

fix prompt中包含精确的复现步骤，基于Mini实际执行的操作路径。

#### 交付物五：失败时刻截图（Screenshot pinned to failure）

每个失败标准都附带失败时刻的截图固定在详情中。

### 5.4 Suggestions（建议）独立收件箱

Mini在运行用户故事时，有时会注意到你没有要求它检查的事情，这些成为**建议（Suggestions）**：

**与Issues（问题）的区别**：

| 维度 | Issues（问题） | Suggestions（建议） |
|-----|---------------|-------------------|
| 来源 | 失败的验收标准或Mini自行发现的bug | Mini在验收标准外注意到的事情 |
| 绑定关系 | 绑定到用户故事，有结论 | 无结论，不阻塞 |
| 处理位置 | Issues中分类 | 独立的Suggestions标签页 |
| Fix Prompt | 有 | 无（只是观察，非带复现路径的失败） |

**Suggestions三个标签页**：
1. **Proposal（待处理）**：新建议，等待你的决定。侧边栏徽章仅计数此项
2. **Not useful（无用）**：你标记为不可行动的建议，保持可见
3. **Acknowledged（已知悉）**：已阅读并接受，但暂时不处理

**展示位置**：建议不出现在运行报告、PR评论或Slack中，Suggestions标签页是唯一位置。

**建议卡片内容**：
- 简短标题
- Mini的可选描述
- 观察到该建议的用户故事（或故事间观察到则显示"No linked story"）
- Mini注意到该问题时刻的嵌入式视频
- 平台
- 上次运行中同一观察出现的时间

**建议生命周期**：
- 当Mini在接触应用该部分的故事中不再注意到某建议时，建议自动消失，无需人工操作
- 标记为"Not useful"不抑制未来观察——如果Mini在后续运行中看到同样问题，卡片留在Not useful标签页并更新"last seen"时间，不会弹回Proposal，但在Mini停止注意到之前也不会消失

**舰队汇总**：在应用页面，每个应用显示Proposal中建议数量——快速了解整个舰队中待处理分类工作量。可按此筛选排序，聚焦未处理建议最多的应用。该计数从不阻塞任何流程。

---

## 六、Quickstart流程（约15分钟）

### 步骤1：创建工作区

1. 在 [app.minitap.ai](https://app.minitap.ai/) 注册
2. 按引导完成：
   - 选择工作区名称
   - 在拥有移动仓库的组织上安装**MiniTest GitHub App**
   - 连接一个应用（名称、图标、仓库、分支）

### 步骤2：编写第一个用户故事

1. 进入**User stories**标签页
2. 点击**New story**
3. 用平实英文描述旅程，让miniTest起草验收标准

示例输入：
```
Name: Sign in with email
Description: A returning user signs in and reaches the home screen.
```

4. 批准建议的验收标准——标准应该是人们仅通过看屏幕就能验证的内容

### 步骤3：运行测试

1. 打开应用的**Runs**标签页
2. 点击**New run**
3. 选择最新构建（或通过CLI上传）
4. 选择故事
5. 点击**Start**

几分钟后获得：
- 绿色的标准列表
- 智能体驱动应用的视频

如果有失败：
- 运行页面提供准备好的fix prompt，可直接用于Cursor或Claude

### 后续步骤推荐

1. **接入GitHub Actions**：让每个PR自动运行套件
2. **从IDE编写故事**：使用CLI或MCP服务器在Cursor/Claude中操作
3. **附加配置文件**：为需要登录用户的故事附加profile

---

## 七、关键能力矩阵总结

| 能力维度 | 具体能力 | 自动化程度 |
|---------|---------|-----------|
| **测试编写** | 用户故事起草、验收标准生成 | Mini自动完成，人工审核 |
| **测试维护** | UI变更适配、新旧功能故事增删、依赖管理 | 全自动，仅凭证/文件需人工 |
| **构建获取** | GitHub源码自动构建、增量构建 | Mini自动完成 |
| **测试执行** | 虚拟设备操作、自动登录、UI交互 | Mini全自动执行 |
| **结果判定** | PASS/FAIL/WARNING判定、证据采集 | 全自动判定 |
| **问题定位** | 视频录制、截图、日志提取、根本原因分析 | 全自动 |
| **修复辅助** | Fix Prompt生成（根因+复现+修复建议） | 全自动生成，人工应用 |
| **主动发现** | UX问题、边缘情况检测 | 全自动，建议人工决定是否处理 |
| **多端集成** | Dashboard、Slack、PR检查、IDE | 全渠道覆盖 |
| **CI/CD集成** | GitHub Actions原生支持、CLI支持 | 配置后全自动 |

---

## 八、核心设计理念

1. **AI Agent为核心**：不是传统录制回放，而是由AI智能体像真人QA一样理解和操作应用
2. **测试即代码但无需写代码**：用自然语言定义用户故事和验收标准，降低测试编写门槛
3. **自维护测试套件**：解决测试套件过时的核心痛点，测试随代码自动演进
4. **可行动结果**：失败时不仅告诉你"坏了"，还给你视频、复现步骤、日志和修复建议
5. **不阻塞流程**：Warning和Suggestions不阻塞发布，团队自主决定处理优先级
6. **IDE原生集成**：通过MCP服务器深度融入开发者工作流，修复提示词直接对接AI编码助手
7. **真实设备环境**：虚拟iOS/Android设备运行，结果贴近真实用户体验

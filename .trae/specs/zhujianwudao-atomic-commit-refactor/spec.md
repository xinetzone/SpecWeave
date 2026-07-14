# 竹简悟道原子提交策略与代码原子化重构 Spec

## Why

`d:\AI\.chaos\zhujianwudao` 当前存在两个工程化问题：

1. **提交粒度不可控**：当前工作区有 2 个未提交文件（`A2ASidebar.tsx` + `components.css`）混合了视觉调整与样式清理；历史提交虽已采用 Conventional Commits，但缺乏"三查暂存法"等可复用的原子提交操作规范，无法保证每次提交只承载一个完整功能/修复。
2. **源码原子性不足**：`src/` 下业务组件、hooks、services 全部平铺在根目录；存在 7 个超过 15KB 的超大文件（最大 `A2ASidebar.tsx` 36KB）；缺少 `src/types/`、`src/constants/` 等公共目录，跨模块复用成本高，可维护性与扩展性受限。

本次变更通过建立原子提交操作规范 + 按功能域对源码进行原子化重构，使每次提交对应一个独立可验证的工程单元，并将源码拆分为独立、可复用的最小单元。

## What Changes

### 原子提交策略
- 将当前未提交的 `A2ASidebar.tsx` + `components.css` 作为单个原子提交归档（侧边栏视觉调整）
- 在 `d:\AI\.chaos\zhujianwudao\AGENTS.md` 中补充「原子提交操作规范」章节：三查暂存法（查新增/查修改/查删除）、Conventional Commits 类型与 scope 词表、提交信息模板
- 后续每个重构步骤均对应一个独立提交，禁止跨功能域混合暂存

### 代码原子化重构
- 在 `src/components/` 下按功能域建立子目录：`meditation/`、`a2a/`、`auth/`、`community/`、`dream/`、`common/`
- 在 `src/hooks/` 下按功能域建立子目录：`meditation/`、`a2a/`、`platform/`、`common/`
- 新建 `src/types/` 收集跨模块共享类型（如 NavItem、FunctionItem、AgentCard 等）
- 新建 `src/constants/` 收集跨模块共享常量（如侧边栏宽度、快捷键映射、导航项配置等）
- 拆分 7 个超大文件（>15KB）：A2ASidebar.tsx、a2a-demo.tsx、project-status.tsx、history.tsx、DreamGenerator.tsx、DeepBreathModal.tsx、routes/index.tsx
- 更新所有受影响文件的 import 路径

### 不在本次范围
- 不引入新功能、不修改业务逻辑、不调整视觉样式
- 不重写 shadcn `ui/` 子目录（已是标准化组件，保持原状）
- 不变更构建配置（vite/tsconfig/tailwind）与依赖版本
- 不删除 `outputs/`、`migrations/`、`functions/`、`e2e/`、`skills/`、`.agents/` 等非 src 目录

## Impact

- **Affected specs**: 无（新建独立 spec）
- **Affected code**:
  - `d:\AI\.chaos\zhujianwudao\AGENTS.md` — 新增「原子提交操作规范」章节
  - `d:\AI\.chaos\zhujianwudao\src\components\**` — 按功能域重组
  - `d:\AI\.chaos\zhujianwudao\src\hooks\**` — 按功能域重组
  - `d:\AI\.chaos\zhujianwudao\src\types\**` — 新建公共类型目录
  - `d:\AI\.chaos\zhujianwudao\src\constants\**` — 新建公共常量目录
  - `d:\AI\.chaos\zhujianwudao\src\routes\**` — 大文件拆分后更新 import
  - `d:\AI\.chaos\zhujianwudao\src\components\A2ASidebar.tsx` 等 7 个超大文件 — 拆分为多个子模块
- **回归风险**:
  - import 路径变更可能引发编译错误 → 通过 `tsc --noEmit` 在每个提交前验证
  - 文件移动可能触发 project_memory 中记录的"Git 文件移动删除暂存陷阱" → 强制执行三查暂存法
  - 测试快照路径可能失效 → 同步更新测试文件 import

## ADDED Requirements

### Requirement: 原子提交操作规范

系统 SHALL 在 `d:\AI\.chaos\zhujianwudao\AGENTS.md` 中新增「原子提交操作规范」章节，明确以下内容：

1. **三查暂存法**：每次提交前必须执行 `git status` 三次确认
   - 查新增：`git status --short | findstr "^??"` 确认新增文件符合本次提交范围
   - 查修改：`git status --short | findstr "^ M\|^M "` 确认修改文件符合本次提交范围
   - 查删除：`git status --short | findstr "^ D\|^D "` 确认旧路径删除已暂存（文件移动场景必备）
2. **Conventional Commits 类型词表**：feat / fix / docs / style / refactor / test / chore
3. **scope 词表**：sidebar / meditation / a2a / auth / community / dream / routes / hooks / types / constants / commit-policy
4. **提交信息模板**：`type(scope): 简明描述变更内容与目的`，主体段落描述「为什么」而非「是什么」
5. **单一职责原则**：单次提交只承载一个功能/修复/重构单元，禁止混合功能域

#### Scenario: 现有未提交变更归档

- **WHEN** 执行首次原子提交
- **THEN** `A2ASidebar.tsx` 与 `components.css` 的视觉调整作为单个 `feat(sidebar)` 提交归档，提交信息描述侧边栏折叠态布局美化与 edge-toggle 遮挡修复

#### Scenario: 文件移动场景

- **WHEN** 将 `src/components/MeditationStats.tsx` 迁移至 `src/components/meditation/MeditationStats.tsx`
- **THEN** 必须同时暂存新路径的添加与旧路径的删除（`git add src/components/MeditationStats.tsx` + `git add src/components/meditation/MeditationStats.tsx`），否则提交后旧文件仍存在于版本控制中

### Requirement: 功能域目录结构

系统 SHALL 在 `src/components/` 与 `src/hooks/` 下按功能域建立子目录，并将业务文件迁移至对应子目录。

#### Scenario: components 功能域分组

- **WHEN** 重构完成后
- **THEN** `src/components/` 下存在以下子目录且业务组件已迁移：
  - `meditation/` — BambooSlip、BreathAnimation、DeepBreathModal、DeepBreathModalV2、MeditationContent、MeditationStats、TodaysInsight、ConceptTrap、InkDiffusion、DialogBox、Message、SpeechPlayer
  - `a2a/` — A2ASidebar
  - `auth/` — AuthProvider、ProtectedRoute、AlipayButton
  - `community/` — CommentModal、ShareMeditationModal、VirtualMessageList
  - `dream/` — DreamGenerator、SceneImage、SceneContainer、EndingScreen
  - `common/` — AudioToggle、ChoiceButton、ErrorBoundary、LaidBackToggle、LazyComponentWrapper、ModalActions、ModelSelector、PageLoader、ProgressBar、PWAInstallPrompt、PushNotificationSettings、NoirEffects、ContemplationInput
- **AND** `src/components/ui/` 保持原状（shadcn 标准组件不动）

#### Scenario: hooks 功能域分组

- **WHEN** 重构完成后
- **THEN** `src/hooks/` 下存在以下子目录：
  - `meditation/` — useContemplation、useBreathSound、useTypewriter、useTextToSpeech
  - `a2a/` — useQAHistory
  - `platform/` — usePWA、usePushNotification、useWebVitals、useMobile
  - `common/` — useAudio、useAuth、useHotkeys、useLocalStorage、useTouch、useCommunity

### Requirement: 公共类型与常量提取

系统 SHALL 新建 `src/types/` 与 `src/constants/` 目录，收集跨模块共享的类型与常量。

#### Scenario: 公共类型提取

- **WHEN** 多个模块共享同一类型定义
- **THEN** 该类型定义 SHALL 提取至 `src/types/` 下对应文件（如 `src/types/navigation.ts` 收集 NavItem、FunctionItem），并通过 `@/types/...` 路径引用

#### Scenario: 公共常量提取

- **WHEN** 多个模块共享同一常量
- **THEN** 该常量 SHALL 提取至 `src/constants/` 下对应文件（如 `src/constants/sidebar.ts` 收集 COLLAPSED_WIDTH、EXPANDED_WIDTH、a2aNavItems、functionItems）

### Requirement: 超大文件拆分

系统 SHALL 对 7 个超过 15KB 的源文件进行拆分，每个文件拆分后单文件不超过 500 行。

#### Scenario: A2ASidebar.tsx 拆分

- **WHEN** 拆分 `src/components/A2ASidebar.tsx`（36KB）
- **THEN** 拆分为以下子模块：
  - 主组件文件 `A2ASidebar.tsx`（仅保留组件主体逻辑）
  - 配置文件迁移至 `src/constants/sidebar.ts`（导航项、功能项、宽度常量）
  - 类型定义迁移至 `src/types/navigation.ts`（NavItem、FunctionItem）
  - 子组件拆分至 `src/components/a2a/sidebar/`（如 SidebarHeader、SidebarNavList、SidebarFunctionPanel、SidebarToggleButton）

#### Scenario: 路由大文件拆分

- **WHEN** 拆分 `src/routes/a2a-demo.tsx`（33KB）、`src/routes/project-status.tsx`（33KB）、`src/routes/history.tsx`（28KB）、`src/routes/index.tsx`（17KB）、`src/routes/about.tsx`（15KB）
- **THEN** 每个路由文件拆分为：
  - 主路由文件仅保留路由定义与组件组合
  - 静态配置数据迁移至 `src/constants/` 或路由同名子目录
  - 子组件提取至 `src/components/<功能域>/` 对应子目录

#### Scenario: 业务大组件拆分

- **WHEN** 拆分 `src/components/DreamGenerator.tsx`（18KB）、`src/components/DeepBreathModal.tsx`（17KB）
- **THEN** 每个大组件拆分为：
  - 主组件文件保留对外接口与组合逻辑
  - 内部子组件提取至同级子目录
  - 配置数据迁移至 `src/constants/` 对应文件

### Requirement: 重构后验证

系统 SHALL 在每个原子提交前通过以下验证：

#### Scenario: 类型检查通过

- **WHEN** 执行 `npm run typecheck`
- **THEN** TypeScript 编译无错误

#### Scenario: 单元测试通过

- **WHEN** 执行 `npm run test`
- **THEN** 所有 vitest 用例通过，无回归

#### Scenario: 构建成功

- **WHEN** 执行 `npm run build`
- **THEN** Vite 构建成功，无报错

## MODIFIED Requirements

### Requirement: AGENTS.md 文档

现有 `d:\AI\.chaos\zhujianwudao\AGENTS.md` 在「快速导航」与「目录结构」之间新增「原子提交操作规范」章节，包含三查暂存法、Conventional Commits 词表、提交信息模板、单一职责原则四个小节。其余章节保持不变。

## REMOVED Requirements

无（本次为新增规范 + 重构，不删除任何现有功能或文档）。

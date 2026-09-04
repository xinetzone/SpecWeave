# Tasks

## 阶段一：原子提交策略落地

- [x] Task 1: 归档当前未提交变更并建立原子提交操作规范
  - [x] SubTask 1.1: 将 `src/components/A2ASidebar.tsx` 与 `src/styles/components.css` 的当前修改作为单个原子提交，类型为 `feat(sidebar)`，描述侧边栏折叠态布局美化与 edge-toggle 遮挡修复
  - [x] SubTask 1.2: 在 `d:\AI\.chaos\zhujianwudao\AGENTS.md` 的「快速导航」与「目录结构」之间新增「原子提交操作规范」章节，包含三查暂存法（查新增/查修改/查删除）、Conventional Commits 类型与 scope 词表、提交信息模板、单一职责原则；以 `docs(commit-policy)` 类型单独提交
  - [x] SubTask 1.3: 验证 AGENTS.md 章节锚点链接与现有「版本信息」章节兼容，无格式冲突

## 阶段二：公共目录骨架建立

- [x] Task 2: 创建功能域目录骨架与公共类型/常量目录
  - [x] SubTask 2.1: 在 `src/components/` 下创建空目录骨架：`meditation/`、`a2a/`、`auth/`、`community/`、`dream/`、`common/`
  - [x] SubTask 2.2: 在 `src/hooks/` 下创建空目录骨架：`meditation/`、`a2a/`、`platform/`、`common/`
  - [x] SubTask 2.3: 新建 `src/types/` 与 `src/constants/` 目录，并各创建一个 `index.ts` 桶文件用于聚合导出
  - [x] SubTask 2.4: 以 `chore(structure)` 类型提交目录骨架

## 阶段三：超大文件拆分

- [x] Task 3: 拆分 `src/components/A2ASidebar.tsx`（36KB）
  - [x] SubTask 3.1: 提取 `NavItem`、`FunctionItem` 类型至 `src/types/navigation.ts`
  - [x] SubTask 3.2: 提取 `COLLAPSED_WIDTH`、`EXPANDED_WIDTH`、`a2aNavItems`、`functionItems` 至 `src/constants/sidebar.ts`
  - [x] SubTask 3.3: 拆分内部子组件至 `src/components/a2a/sidebar/`（SidebarHeader、SidebarNavList、SidebarFunctionPanel、SidebarToggleButton）
  - [x] SubTask 3.4: 主文件 `A2ASidebar.tsx` 仅保留组件主体组合逻辑
  - [x] SubTask 3.5: 运行 `npm run typecheck` 验证
  - [x] SubTask 3.6: 以 `refactor(a2a)` 类型提交

- [x] Task 4: 拆分 `src/routes/a2a-demo.tsx`（33KB）
  - [x] SubTask 4.1: 提取五子论道配置数据至 `src/constants/a2a-demo.ts`
  - [x] SubTask 4.2: 提取内部子组件至 `src/components/a2a/demo/`
  - [x] SubTask 4.3: 主路由文件仅保留路由定义与组件组合
  - [x] SubTask 4.4: 运行 `npm run typecheck` + `npm run test` 验证
  - [x] SubTask 4.5: 以 `refactor(routes)` 类型提交

- [x] Task 5: 拆分 `src/routes/project-status.tsx`（33KB）
  - [x] SubTask 5.1: 提取项目状态数据至 `src/constants/project-status.ts`
  - [x] SubTask 5.2: 提取内部子组件至 `src/components/common/project-status/`（或新建功能域目录）
  - [x] SubTask 5.3: 主路由文件仅保留路由定义与组件组合
  - [x] SubTask 5.4: 运行 `npm run typecheck` 验证
  - [x] SubTask 5.5: 以 `refactor(routes)` 类型提交

- [x] Task 6: 拆分 `src/routes/history.tsx`（28KB）
  - [x] SubTask 6.1: 无静态配置数据需要提取（所有数据来自hooks动态获取），跳过创建 `src/constants/history.ts`
  - [x] SubTask 6.2: 提取内部子组件至 `src/components/common/history/`（DateGroup.tsx + RecordItem.tsx）
  - [x] SubTask 6.3: 主路由文件仅保留路由定义与组件组合（758→464行）
  - [x] SubTask 6.4: 运行 `npm run typecheck` 验证
  - [x] SubTask 6.5: 以 `refactor(routes)` 类型提交

- [x] Task 7: 拆分 `src/components/DreamGenerator.tsx`（18KB）
  - [x] SubTask 7.1: 提取风格预设、模型选项、比例选项至 `src/constants/dream.ts`
  - [x] SubTask 7.2: 提取内部子组件至 `src/components/dream/`
  - [x] SubTask 7.3: 主组件文件仅保留对外接口与组合逻辑（454→234 行）
  - [x] SubTask 7.4: 运行 `npm run typecheck` 验证
  - [x] SubTask 7.5: 以 `refactor(dream)` 类型提交

- [x] Task 8: 拆分 `src/components/DeepBreathModal.tsx`（17KB）
  - [x] SubTask 8.1: 提取呼吸阶段配置数据至 `src/constants/meditation.ts`
  - [x] SubTask 8.2: 提取内部子组件至 `src/components/meditation/deep-breath/`
  - [x] SubTask 8.3: 主组件文件仅保留对外接口与组合逻辑（510→355 行）
  - [x] SubTask 8.4: 运行 `npm run typecheck` 验证
  - [x] SubTask 8.5: 以 `refactor(meditation)` 类型提交

- [x] Task 9: 拆分 `src/routes/index.tsx`（17KB）
  - [x] SubTask 9.1: 提取首页配置数据至 `src/constants/home.ts`（SAMPLE_PROMPTS）
  - [x] SubTask 9.2: 提取内部子组件至 `src/components/meditation/home/`（5 个子组件）
  - [x] SubTask 9.3: 主路由文件仅保留路由定义与组件组合（472→252 行）
  - [x] SubTask 9.4: 运行 `npm run typecheck` + `npm run test`（含 `-index.test.tsx`）验证
  - [x] SubTask 9.5: 以 `refactor(routes)` 类型提交

## 阶段四：业务组件按功能域迁移

> **重要**：每个功能域迁移为一个独立原子提交，提交前必须执行三查暂存法（重点查旧路径删除是否已暂存）。

- [x] Task 10: 迁移 meditation 功能域组件
  - [x] SubTask 10.1: 将 BambooSlip、BreathAnimation、DeepBreathModal、DeepBreathModalV2、MeditationContent、MeditationStats、TodaysInsight、ConceptTrap、InkDiffusion、DialogBox、Message、SpeechPlayer 迁移至 `src/components/meditation/`
  - [x] SubTask 10.2: 同步迁移对应测试文件（`*.test.tsx`）
  - [x] SubTask 10.3: 更新所有引用方的 import 路径
  - [x] SubTask 10.4: 运行 `npm run typecheck` + `npm run test` 验证
  - [x] SubTask 10.5: 以 `refactor(meditation)` 类型提交

- [x] Task 11: 迁移 a2a 功能域组件
  - [x] SubTask 11.1: 将 `src/components/A2ASidebar.tsx`（已拆分后的主文件 + sidebar/ 子目录）迁移至 `src/components/a2a/`
  - [x] SubTask 11.2: 更新所有引用方的 import 路径
  - [x] SubTask 11.3: 运行 `npm run typecheck` 验证
  - [x] SubTask 11.4: 以 `refactor(a2a)` 类型提交

- [x] Task 12: 迁移 auth 功能域组件
  - [x] SubTask 12.1: 将 AuthProvider、ProtectedRoute、AlipayButton 迁移至 `src/components/auth/`
  - [x] SubTask 12.2: 更新所有引用方的 import 路径
  - [x] SubTask 12.3: 运行 `npm run typecheck` 验证
  - [x] SubTask 12.4: 以 `refactor(auth)` 类型提交

- [x] Task 13: 迁移 community 功能域组件
  - [x] SubTask 13.1: 将 CommentModal、ShareMeditationModal、VirtualMessageList 迁移至 `src/components/community/`
  - [x] SubTask 13.2: 更新所有引用方的 import 路径
  - [x] SubTask 13.3: 运行 `npm run typecheck` 验证
  - [x] SubTask 13.4: 以 `refactor(community)` 类型提交

- [x] Task 14: 迁移 dream 功能域组件
  - [x] SubTask 14.1: 将 DreamGenerator（已拆分后的主文件 + 子组件）、SceneImage、SceneContainer、EndingScreen 迁移至 `src/components/dream/`
  - [x] SubTask 14.2: 更新所有引用方的 import 路径
  - [x] SubTask 14.3: 运行 `npm run typecheck` 验证
  - [x] SubTask 14.4: 以 `refactor(dream)` 类型提交

- [x] Task 15: 迁移 common 共享组件
  - [x] SubTask 15.1: 将 AudioToggle、ChoiceButton、ErrorBoundary、LaidBackToggle、LazyComponentWrapper、ModalActions、ModelSelector、PageLoader、ProgressBar、PWAInstallPrompt、PushNotificationSettings、NoirEffects、ContemplationInput 迁移至 `src/components/common/`
  - [x] SubTask 15.2: 同步迁移对应测试文件
  - [x] SubTask 15.3: 更新所有引用方的 import 路径
  - [x] SubTask 15.4: 运行 `npm run typecheck` + `npm run test` 验证
  - [x] SubTask 15.5: 以 `refactor(common)` 类型提交

## 阶段五：hooks 按功能域迁移

- [x] Task 16: 迁移 hooks 至功能域子目录
  - [x] SubTask 16.1: 将 useContemplation、useBreathSound、useTypewriter、useTextToSpeech 迁移至 `src/hooks/meditation/`（含测试文件）
  - [x] SubTask 16.2: 将 useQAHistory 迁移至 `src/hooks/a2a/`
  - [x] SubTask 16.3: 将 usePWA、usePushNotification、useWebVitals、use-mobile 迁移至 `src/hooks/platform/`
  - [x] SubTask 16.4: 将 useAudio、useAuth、useHotkeys、useLocalStorage、useTouch、useCommunity 迁移至 `src/hooks/common/`（含测试文件）
  - [x] SubTask 16.5: 更新所有引用方的 import 路径（24 个文件）
  - [x] SubTask 16.6: 运行 `npm run typecheck` + `npm run test` 验证（typecheck 零错误；test 失败均为预存问题，无新增失败）
  - [x] SubTask 16.7: 以 `refactor(hooks)` 类型提交（commit 8c2f812）

## 阶段六：最终验证与回归

- [x] Task 17: 全量验证
  - [x] SubTask 17.1: 执行 `npm run typecheck`，确认零错误
  - [x] SubTask 17.2: 执行 `npm run test`，确认无新增因重构导致的失败（预存 142 个失败为 jsdom/playwright 环境问题，与本次重构无关）
  - [x] SubTask 17.3: 执行 `npm run build`，确认 Vite 构建成功（4117 modules, 14.08s, dist/ 正常生成）
  - [x] SubTask 17.4: 修复 `-index.test.tsx` 中 6 处旧 vi.mock 路径 + 1 处旧 import 路径，以 `fix(test)` 类型提交（commit cba21e5）
  - [x] SubTask 17.5: 执行 `git log --oneline` 确认每个重构步骤对应独立提交（共 17 个提交），提交信息符合 Conventional Commits 规范

# Task Dependencies

- Task 1 → Task 2（先建立提交规范，再开始重构）
- Task 2 → Task 3-9（先建目录骨架，再拆分大文件）
- Task 3 → Task 11（A2ASidebar 拆分后再迁移到 a2a/ 目录）
- Task 7 → Task 14（DreamGenerator 拆分后再迁移到 dream/ 目录）
- Task 8 → Task 10（DeepBreathModal 拆分后再迁移到 meditation/ 目录）
- Task 9 → Task 10（index.tsx 拆分时引用的 meditation 子组件需先就位）
- Task 3-9 → Task 10-15（大文件拆分完成后，再统一迁移功能域）
- Task 10-15 → Task 16（组件迁移完成后再迁移 hooks，避免 import 路径多次变更）
- Task 16 → Task 17（所有重构完成后执行全量验证）

# 并行化机会

- Task 3-9（7 个大文件拆分）相互独立，可并行执行
- Task 10-15（6 个功能域迁移）在 Task 3-9 完成后相互独立，可并行执行

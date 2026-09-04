# Checklist

## 阶段一：原子提交策略
- [x] 当前未提交的 `A2ASidebar.tsx` 与 `components.css` 已作为单个 `feat(sidebar)` 提交归档
- [x] `d:\AI\.chaos\zhujianwudao\AGENTS.md` 已新增「原子提交操作规范」章节
- [x] 章节包含三查暂存法（查新增/查修改/查删除）三个子项
- [x] 章节包含 Conventional Commits 类型词表（feat/fix/docs/style/refactor/test/chore）
- [x] 章节包含 scope 词表（sidebar/meditation/a2a/auth/community/dream/routes/hooks/types/constants/commit-policy）
- [x] 章节包含提交信息模板与单一职责原则说明
- [x] AGENTS.md 章节以 `docs(commit-policy)` 类型独立提交

## 阶段二：目录骨架
- [x] `src/components/` 下已创建 6 个功能域子目录（meditation/a2a/auth/community/dream/common）
- [x] `src/hooks/` 下已创建 4 个功能域子目录（meditation/a2a/platform/common）
- [x] 已新建 `src/types/` 与 `src/constants/` 目录及 `index.ts` 桶文件
- [x] 目录骨架以 `chore(structure)` 类型独立提交

## 阶段三：超大文件拆分
- [x] `A2ASidebar.tsx` 已拆分，主文件单文件不超过 500 行（1011→438 行）
- [x] `A2ASidebar.tsx` 的类型已迁移至 `src/types/navigation.ts`
- [x] `A2ASidebar.tsx` 的常量与配置已迁移至 `src/constants/sidebar.ts`
- [x] `A2ASidebar.tsx` 的子组件已迁移至 `src/components/a2a/sidebar/`
- [x] `routes/a2a-demo.tsx` 已拆分，主文件单文件不超过 500 行（820→402 行）
- [x] `routes/project-status.tsx` 已拆分，主文件单文件不超过 500 行（752→369 行）
- [x] `routes/history.tsx` 已拆分，主文件单文件不超过 500 行（758→464 行）
- [x] `DreamGenerator.tsx` 已拆分，主文件单文件不超过 500 行（454→234 行）
- [x] `DeepBreathModal.tsx` 已拆分，主文件单文件不超过 500 行（510→355 行）
- [x] `routes/index.tsx` 已拆分，主文件单文件不超过 500 行（472→252 行）
- [x] 每个大文件拆分对应独立原子提交（共 7 个提交）

## 阶段四：业务组件迁移
- [x] meditation 功能域 12 个组件已迁移至 `src/components/meditation/`（17 文件含测试）
- [x] a2a 功能域组件已迁移至 `src/components/a2a/`
- [x] auth 功能域 3 个组件已迁移至 `src/components/auth/`
- [x] community 功能域 3 个组件已迁移至 `src/components/community/`
- [x] dream 功能域 4 个组件已迁移至 `src/components/dream/`（5 文件含测试）
- [x] common 功能域 13 个组件已迁移至 `src/components/common/`（17 文件含测试）
- [x] `src/components/ui/` 保持原状未动
- [x] 所有引用方的 import 路径已同步更新
- [x] 测试文件已随组件同步迁移
- [x] 每个功能域迁移对应独立原子提交（共 6 个提交）
- [x] 文件移动场景下旧路径删除已暂存（三查暂存法"查删除"通过）

## 阶段五：hooks 迁移
- [x] meditation hooks（4 个）已迁移至 `src/hooks/meditation/`
- [x] a2a hooks（1 个）已迁移至 `src/hooks/a2a/`
- [x] platform hooks（4 个）已迁移至 `src/hooks/platform/`
- [x] common hooks（6 个）已迁移至 `src/hooks/common/`
- [x] 所有引用方的 import 路径已同步更新（24 个引用方文件）
- [x] hooks 迁移以 `refactor(hooks)` 类型独立提交（commit 8c2f812）

## 阶段六：最终验证
- [x] `npm run typecheck` 零错误
- [x] `npm run test` 无新增因重构导致的失败（预存失败为 jsdom/playwright 环境问题）
- [x] `npm run build` 构建成功（4117 modules, 14.08s, dist/ 正常生成）
- [x] 测试文件 vi.mock 路径已全部更新至功能域新位置（commit cba21e5 fix(test)）
- [x] 首页（/）相关测试 mock 路径正确，组件导入路径正确（typecheck+build 双重验证）
- [x] `git log --oneline` 显示每个重构步骤对应独立提交（共 17 个原子提交）
- [x] 所有提交信息符合 Conventional Commits 规范（type(scope): 中文描述）
- [x] 无混合功能域的提交（每个提交只承载一个功能/修复/重构单元）
- [x] 目录结构符合功能域划分设计，components/ 和 hooks/ 根目录无遗留文件

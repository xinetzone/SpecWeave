---
id: "seven-concepts-codex-examples"
title: "08b、Codex/Agent开发实战：8个场景模板"
category: "knowledge"
date: "2026-07-14"
version: "1.0"
status: "completed"
source: "OpenAI Codex最佳实践"
---

# Codex/Agent开发实战：8个场景模板

---

## 1. 章节引言

本文是[08-codex-scenarios.md](08-codex-scenarios.md)的配套实战示例。在上一章我们学习了Codex场景的安全原则、标准结构和完整Prompt模板，本章提供8个最高频Codex开发场景的完整Prompt模板，每个都可以直接复制使用，每个都标注了安全注意事项。

建议先阅读08章理解安全原则，再使用本章的模板；如果只是想快速上手，可以直接复制对应场景的模板填空使用。

---

## 2. 8个Codex开发场景实战示例

下面是8个最高频的Codex场景，每个都是可以直接使用的完整Prompt，每个都有安全注意事项。

### 2.1 场景一：添加新页面/新组件

```
# Context
当前目录是一个Next.js 14 + TypeScript项目，用App Router，UI库是shadcn/ui。
- 组件目录：src/components/
- 页面目录：src/app/
- API路由：src/app/api/
- 类型在src/types/index.ts
- 已经有zod和react-hook-form，表单都用这个组合
- 已经有Toast提示组件，用toast()函数
- 不要用any，TypeScript strict模式

# Request
帮我加一个"项目设置"页面，具体功能：
1. 路由：/dashboard/settings
2. 三个Tab：基本信息、成员管理、危险操作
3. 基本信息Tab：修改项目名称、描述，有保存按钮
4. 成员管理Tab：展示成员列表，可以邀请（输入邮箱选角色）、移除成员
5. 危险操作Tab：删除项目，有二次确认，输入项目名称才能确认删除

完成标准：
- 所有代码有完整TypeScript类型
- 表单用react-hook-form+zod
- 所有异步操作有loading和toast提示
- Tab组件用shadcn/ui的Tabs
- 代码风格和现有页面一致

# Constraints
✅ 允许修改/新建：
- src/app/dashboard/settings/ 页面文件（新建）
- src/components/settings/ 下的组件（新建）
- src/app/api/projects/[id]/ 下的相关API（可以新增接口）
- src/types/index.ts 可以加Settings相关类型

❌ 绝对不要改：
- src/app/layout.tsx
- src/middleware.ts
- prisma/schema.prisma
- package.json，不要加新包
- 现有的其他dashboard页面

# Checkpoint
遇到以下情况立即停：
1. 需要改schema才能实现功能
2. 需要装新包
3. 需要改middleware或layout
4. API需要的权限控制你不确定怎么加

# Tools
- ✅ 读文件、写白名单内文件
- ✅ 运行npm run typecheck检查类型
- ❌ 禁止删文件、禁止装包、禁止危险命令

先列计划，确认后再动手。
```

**安全注意事项**：新页面一般风险不高，但还是要明确白名单，防止它"顺手"重构其他相关页面。

---

### 2.2 场景二：修复Bug

```
# Context
这是一个Python FastAPI后端项目。
- API路由在app/api/
- 服务层在app/services/
- 模型在app/models/
- 数据库用SQLAlchemy
- 测试在tests/目录，用pytest

# Request
修复一个Bug：用户反馈说，更新用户资料的时候，如果不传头像字段，会把现有头像清空。
重现步骤：
1. 调用PUT /api/users/me，只传name字段，不传avatar
2. 预期：name更新，avatar保持不变
3. 实际：avatar被设置成null了

帮我：
1. 先找到问题出在哪
2. 修复这个Bug
3. 写一个测试用例覆盖这个场景
4. 确保现有其他测试还能过

完成标准：
- Bug确实修复了，不传avatar时不会清空
- 有对应的测试用例
- 所有现有测试通过
- 不要重构其他代码，只修这个Bug

# Constraints
✅ 允许修改：
- 处理用户更新的API路由文件
- 相关的service文件，如果问题在service层
- 新增测试文件test_user_update.py，或者在现有测试文件里加用例

❌ 绝对不要改：
- 数据库模型
- 其他API接口
- requirements.txt，不要加新依赖
- 配置文件

# Checkpoint
遇到以下情况立即停：
1. 你发现Bug不是表面看起来那样，需要改模型或其他模块
2. 修复需要大重构，不是改几行能解决的
3. 现有测试过不了，不是你这次改的代码导致的
4. 你看不懂某个部分的逻辑，不确定怎么改

# Tools
- ✅ 读文件、写白名单内文件
- ✅ 运行pytest测试
- ❌ 禁止改模型、禁止加依赖、禁止删文件

注意：是修Bug，不是重构。改最少的代码解决问题。先找到根因，列修复计划，确认后再改。
```

**安全注意事项**：修Bug最容易"顺手重构"，一定要强调"改最少的代码"，只修这个Bug，不要改其他东西。

---

### 2.3 场景三：代码重构

```
# Context
这是一个React项目，src/utils/format.ts里有很多格式化函数，现在这个文件快500行了，有点乱。
这些函数被整个项目很多地方引用。

# Request
帮我重构src/utils/format.ts文件：
1. 按功能拆分成多个小文件：date.ts、currency.ts、text.ts、number.ts
2. 在src/utils/index.ts里统一导出，保持现有导入路径不变（其他文件import的地方不用改）
3. 删掉重复的函数
4. 给每个函数加上简单的JSDoc注释
5. 确保所有现有引用不会断

完成标准：
- 拆分后每个文件不超过100行
- 现有import { xxx } from '@/utils/format'还能正常工作（通过index.ts re-export）
- 没有重复函数
- 每个函数有JSDoc
- 类型完整，不要用any
- TypeScript编译不报错

# Constraints
✅ 允许修改/新建：
- src/utils/ 下的文件，可以新建拆分后的小文件
- src/utils/index.ts，可以修改re-export
- 可以删除原来的src/utils/format.ts（拆分完之后）

❌ 绝对不要改：
- src/utils/ 以外的任何文件（导入路径必须保持兼容，不需要改其他文件）
- 不要改函数的签名和逻辑，只是拆分和去重，不要改功能
- package.json，不要加新包
- 不要改其他utils文件

# Checkpoint
遇到以下情况立即停：
1. 你发现某个函数的逻辑有bug，要不要顺便修？→ 不要修，先告诉我
2. 有函数不知道放哪个分类里
3. 发现循环依赖问题
4. 需要改其他文件才能保持兼容

# Tools
- ✅ 读文件、写白名单内文件
- ✅ 运行npm run typecheck、npm run build验证
- ❌ 禁止修改utils以外的文件
- ❌ 禁止改变函数行为，只是拆分

重要：这只是结构性重构，不要改任何函数的逻辑和对外API。先列拆分计划，确认后再动手。
```

**安全注意事项**：重构风险高，因为涉及文件移动和删除，必须强调"对外API保持兼容、不改其他文件、不改变函数逻辑"。

---

### 2.4 场景四：编写单元测试

```
# Context
这是一个TypeScript项目，用Jest做测试。
- 被测试的文件：src/services/paymentService.ts
- 现有测试在tests/services/目录
- 测试框架：Jest + ts-jest
- 已经有jest配置好了

# Request
帮我给paymentService.ts写单元测试，要求：
1. 覆盖所有export的函数
2. 分支覆盖率达到80%以上
3. mock掉外部依赖（Stripe API、数据库调用）
4. 包含成功场景、失败场景、边界情况
5. 测试描述清晰，每个测什么一眼能看出来

完成标准：
- 测试文件在tests/services/paymentService.test.ts
- 可以直接运行npm test -- paymentService通过
- 不依赖外部网络，所有外部调用都mock
- 每个测试是独立的，不互相依赖
- 不要改被测试的源代码，只写测试

# Constraints
✅ 允许：
- 新建tests/services/paymentService.test.ts
- 如果需要，可以在tests/mocks/下加mock数据

❌ 绝对不要：
- 修改src/services/paymentService.ts（除非你发现明显bug，先告诉我）
- 修改package.json或jest配置
- 修改其他测试文件
- 不要写集成测试，只写单元测试

# Checkpoint
遇到以下情况立即停：
1. 你发现源代码有bug，测试过不了
2. 代码耦合度太高，不好mock，需要重构源代码才能测试
3. 需要新的mock库或工具
4. 不确定某个分支场景是什么意思

# Tools
- ✅ 读源代码文件
- ✅ 写测试文件
- ✅ 运行npm test -- paymentService验证
- ❌ 禁止修改源代码
- ❌ 禁止加新依赖

先看一下paymentService.ts的代码，列一下你打算测哪些场景，确认后再写测试。
```

**安全注意事项**：写测试风险低，但要强调"不要改源代码"——很多时候Agent发现代码不好测，会"顺手"重构源代码，这必须经过你同意。

---

### 2.5 场景五：添加API接口

```
# Context
这是一个Express + TypeScript后端项目。
- 路由在src/routes/
- 控制器在src/controllers/
- 服务层在src/services/
- 验证用zod
- 数据库用Prisma
- 现有API都有统一的响应格式：{ success: boolean, data?: any, error?: string }

# Request
帮我添加一组任务管理的CRUD API：
1. GET /api/tasks - 获取任务列表，支持分页、按状态筛选
2. GET /api/tasks/:id - 获取单个任务详情
3. POST /api/tasks - 创建新任务
4. PUT /api/tasks/:id - 更新任务
5. DELETE /api/tasks/:id - 删除任务

要求：
- 所有接口有zod验证
- 有统一的错误处理
- 创建和更新需要用户权限（只能操作自己的任务）
- 列表接口支持分页（page、limit）和状态筛选

完成标准：
- 所有API按REST规范设计
- 输入用zod验证，验证错误返回400
- 权限控制正确，用户不能操作别人的任务
- 返回格式符合项目现有统一格式
- 有基本的错误处理（任务不存在返回404等）

# Constraints
✅ 允许新建/修改：
- src/routes/tasks.ts（新建路由）
- src/controllers/taskController.ts（新建控制器）
- src/services/taskService.ts（新建服务层）
- src/schemas/taskSchema.ts（新建zod验证schema）
- src/routes/index.ts可以加一行注册路由

❌ 绝对不要改：
- prisma/schema.prisma（Task模型已经定义好了）
- 现有的中间件（auth、error handler等）
- package.json，不要加新包
- 其他路由、控制器、服务文件

# Checkpoint
遇到以下情况立即停：
1. Task模型的字段不够，需要加字段
2. 需要新的中间件
3. 不确定权限怎么校验，现有auth中间件怎么用
4. 发现现有代码的模式和你预期的不一样

# Tools
- ✅ 读现有路由/控制器/服务文件，理解现有模式
- ✅ 写白名单内的文件
- ✅ 可以运行npm run typecheck
- ❌ 禁止改schema、禁止加依赖、禁止改中间件

先读一下现有的一个CRUD模块（比如users），照着现有模式来做，不要自己发明新模式。列文件清单，确认后再开始。
```

**安全注意事项**：加API容易犯的错是自己发明新模式，一定要让它先看现有代码怎么写的，照着来。

---

### 2.6 场景六：编写/更新文档

```
# Context
这是一个开源工具项目，根目录有README.md。
项目是一个CLI工具，叫"fastgrep"，用Rust写的，用来快速搜索代码。
现在README只有基本介绍，需要完善使用文档。

# Request
帮我完善README.md，添加/更新以下内容：
1. 功能特性列表（Features）
2. 安装说明（Cargo安装、Homebrew安装、二进制下载）
3. 快速开始：3个最常用的命令示例
4. 完整用法说明，所有flags的解释
5. 配置文件说明
6. 贡献指南（简单的）
7. License

要求：
- 保持README现在的风格
- 命令示例要准确，基于src/cli.rs里实际定义的参数
- 不要瞎编功能，代码里有的才写
- 简洁明了，不要太长

# Constraints
✅ 允许修改：
- README.md

✅ 允许读：
- 可以读src/下的Rust代码，理解有哪些命令和参数
- 可以读Cargo.toml看版本和依赖

❌ 绝对不要改：
- 任何Rust源代码文件
- Cargo.toml
- 其他文档文件
- 不要改项目代码，只改README

# Checkpoint
遇到以下情况立即停：
1. 你看不懂某个参数是干嘛的
2. 代码里有功能但不确定怎么用
3. 发现README里现有的内容有错误

# Tools
- ✅ 读源代码（理解实际功能）
- ✅ 写README.md
- ❌ 禁止修改任何源代码文件
- ❌ 不要编代码里没有的功能

先读一下src/cli.rs，列出来所有支持的命令和参数，再开始写README。
```

**安全注意事项**：写文档也要注意"不要编功能"，必须让它先读代码，基于实际代码写文档，不要自己脑补。

---

### 2.7 场景七：依赖升级

```
# Context
这是一个React项目，package.json里react版本是18.2.0，想升到18.3.x最新的小版本。
- 用的是npm
- 项目目前能正常build和运行
- 用了react-router-dom、@tanstack/react-query等常见库

# Request
帮我把react和react-dom升级到最新的18.x.x小版本（注意是18.x，不是19）：
1. 先检查package.json里的当前版本
2. 升级react和react-dom
3. 检查有没有其他依赖因为这个升级需要升级 peer dependencies
4. 运行npm install
5. 运行npm run build确保能正常构建
6. 运行npm run test确保测试能过

如果升级过程中有问题，停下来告诉我，不要自己瞎改。

# Constraints
✅ 允许：
- 修改package.json里react和react-dom的版本
- 如果有必要，升级相关的peer dependencies（但要先告诉我要升哪些）
- 运行npm install、npm run build、npm run test

❌ 绝对不要：
- 不要升到React 19，只升18.x的最新小版本
- 不要升级其他不相关的依赖
- 不要改代码（如果有breaking change需要改代码，先停下来告诉我）
- 不要删除node_modules或lock文件重新装（除非我同意）

# Checkpoint
遇到以下情况立即停：
1. npm install有peer dependency冲突
2. build失败
3. 测试失败
4. 需要升级其他包才能兼容
5. 需要改代码才能通过build/test

# Tools
- ✅ 读package.json
- ✅ 运行npm相关命令
- ⚠️ 写package.json之前先告诉我你要改成什么版本
- ❌ 禁止改源代码
- ❌ 禁止升级到React 19
- ❌ 禁止升级无关依赖

重要：先告诉我你打算升哪个版本，可能需要动哪些依赖，确认后再动手执行升级。如果升级出问题，停下来，不要自己尝试改代码解决。
```

**安全注意事项**：依赖升级风险很高，很容易搞崩项目。必须严格限制版本范围，出问题立即停，不要让它自己改代码"修复"兼容问题。

---

### 2.8 场景八：配置修改

```
# Context
这是一个Next.js项目，现在想配置API请求代理，解决本地开发跨域问题。
- next.config.js在项目根目录
- 现在next.config.js只有基本的配置

# Request
帮我在next.config.js里加rewrites配置，把/api/*的请求代理到http://localhost:8000/api/*
本地开发用的，生产环境不需要。

要求：
- 只加开发环境的rewrites
- 保持现有配置不变，只加需要的部分
- 不要改其他配置

# Constraints
✅ 允许修改：
- next.config.js（只加rewrites配置）

❌ 绝对不要：
- 不要改其他配置文件（tsconfig、eslint等）
- 不要改源代码
- 不要加新依赖
- 不要改生产环境配置

# Checkpoint
遇到以下情况立即停：
1. 你发现现有next.config.js的结构比较复杂，不确定怎么加
2. 加完之后npm run dev起不来
3. 需要装什么额外的包

# Tools
- ✅ 读现有的next.config.js
- ⚠️ 修改之前先把你要加的配置给我看一下
- ✅ 修改后可以运行npm run build验证配置是否正确
- ❌ 禁止改其他配置文件
- ❌ 禁止改其他逻辑

先读一下现有的next.config.js，告诉我你打算怎么改，确认后再改。
```
**安全注意事项**：配置文件是核心文件，改坏了整个项目起不来。修改之前必须先看现有配置，把要改的内容给你看，确认后再动手。

## 3. 三场景对比总结

| 场景 | 适用任务 | Prompt结构 | 核心原则 |
|------|---------|-----------|---------|
| **Chat** | 问答、辅导、头脑风暴、简单翻译 | 背景+问题+形式要求 | 明确、有上下文、说清形式 |
| **Work** | 报告、文档、PRD、专业翻译 | 五段式Context/Request/Output/Constraints/Checkpoint | 结构完整、事实核验 |
| **Codex** | 写代码、改Bug、重构、加功能 | 六段式+文件白名单+工具白名单 | 安全第一、边界清晰、先计划后动手 |

## 4. 本章小结

**使用建议**：模板是起点不是终点，复制后根据具体项目调整；白名单一定要改成你自己项目的路径；安全注意事项都是踩坑经验，不要跳过；先读08章理解安全原则再用模板。

👉 [08-codex-scenarios.md](08-codex-scenarios.md)（基础指南） | 👉 [09-checklists-templates.md](09-checklists-templates.md)（Checklist合集）

---

*本文件版本：v1.0 | 创建日期：2026-07-14 | 状态：✅ 已完成 | 来源：OpenAI Codex最佳实践*

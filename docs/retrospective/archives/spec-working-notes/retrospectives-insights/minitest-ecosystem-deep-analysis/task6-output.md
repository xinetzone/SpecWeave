---
source: "d:\\AI\\.chaos\\libs\\minitap-ai\\demo-app, d:\\AI\\.chaos\\libs\\minitap-ai\\minisweeper, d:\\AI\\.trae\\specs\\retrospectives-insights\\minitest-ecosystem-deep-analysis\\task4-output.md"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task6-output.toml"
analysis_date: "2026-07-07"
task: "task6 - demo-app/minisweeper深度分析与测试Profile/环境变量安全机制提取"
---
# Minitest 生态系统深度分析报告（task6）

## 1. demo-app Flutter 扫雷游戏深度分析

### 1.1 lib/ 完整目录结构

`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/` 目录结构：

```
lib/
├── main.dart                          # 应用入口
├── models/
│   ├── cell.dart                      # 单元格数据模型
│   ├── difficulty.dart                # 难度级别定义
│   ├── game_state.dart                # 游戏状态枚举
│   ├── mood.dart                      # 情绪枚举（新增）
│   └── user.dart                      # 用户模型（新增）
├── controllers/
│   └── game_controller.dart           # 游戏逻辑与状态管理
├── screens/
│   ├── game_screen.dart               # 主游戏界面
│   └── difficulty_screen.dart         # 难度选择界面
└── widgets/
    ├── board_widget.dart              # 游戏棋盘UI
    └── cell_widget.dart               # 单元格UI组件
```

### 1.2 项目配置与依赖

文件：`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/pubspec.yaml`

| 配置项 | 值 |
|---|---|
| 项目名 | minesweeper |
| 版本 | 1.0.0+1 |
| Dart SDK | ^3.10.8 |
| Flutter SDK | 3.38.9 |
| 核心依赖 | provider: ^6.1.1 |
| UI图标 | cupertino_icons: ^1.0.8 |
| 开发依赖 | flutter_lints: ^6.0.0 |

### 1.3 MVC 架构分析

#### Model 层（纯数据）

**Cell 模型**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/cell.dart:1-24`）：
- 不可变坐标：`row`、`col`（final）
- 可变状态：`isMine`、`isRevealed`、`isFlagged`、`adjacentMines`
- 提供 `reset()` 方法重置状态

**Difficulty 模型**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/difficulty.dart:1-36`）：
- 使用静态常量定义三个难度级别
- `all` 静态列表便于遍历选择

**GameState 枚举**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/game_state.dart:1-6`）：
- ready → 初始就绪状态
- playing → 游戏进行中
- won → 胜利
- lost → 失败

**Mood 枚举扩展**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/mood.dart:1-56`）：
- 5种情绪：happy、calm、anxious、sad、neutral
- 通过 extension 提供 `label`、`color`、`icon` 属性

**User 模型**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/user.dart:1-70`）：
- 包含 id、name、avatarUrl、currentMood 字段
- 支持 copyWith 模式更新
- 提供 JSON 序列化/反序列化
- 实现了 == 运算符和 hashCode
- 完整的 toString 方法

#### Controller 层（状态管理）

**GameController**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/controllers/game_controller.dart:8-205`）继承自 `ChangeNotifier`，通过 Provider 注入：

核心私有状态：
- `_difficulty`：当前难度（默认 Beginner）
- `_board`：二维 Cell 数组
- `_gameState`：游戏状态枚举
- `_flagCount`：已标记旗子数
- `_revealedCount`：已揭示格子数
- `_elapsedSeconds`：计时器秒数
- `_timer`：Dart Timer 实例
- `_firstClick`：首次点击标记（用于安全布雷）

公开 getter：
- `difficulty`、`board`、`gameState`、`flagCount`、`remainingMines`、`elapsedSeconds`

#### View 层（UI组件）

**入口**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/main.dart:1-28`）：
- 使用 `ChangeNotifierProvider` 在根节点注入 GameController
- MaterialApp 使用 Material 3 主题，种子色为灰色

**GameScreen**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/screens/game_screen.dart:8-184`）：
- 顶部 AppBar 带设置按钮
- 中部信息栏：剩余雷数计数器 → 重置表情按钮 → 计时器
- 可滚动棋盘区域
- 底部胜利/失败消息

**DifficultyScreen**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/screens/difficulty_screen.dart:6-65`）：
- ListView 展示三个难度选项
- 选中项高亮显示（蓝色背景 + 勾选图标）
- 点击自动返回游戏界面

**BoardWidget**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/widgets/board_widget.dart:6-57`）：
- 响应式计算格子尺寸（clamp在20-40像素）
- 双向 SingleChildScrollView 支持大棋盘滚动
- 每个格子绑定 tap/longPress 回调

**CellWidget**（`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/widgets/cell_widget.dart:4-92`）：
- GestureDetector 处理点击/长按
- 数字采用经典扫雷配色（1蓝2绿3红4紫5橙6青7黑8灰）
- 已揭示雷显示红色背景
- 旗子用红色旗帜图标

### 1.4 Provider 状态管理

状态管理采用 Provider 6.x 方案：

1. **根注入**：`main.dart:15-16` 通过 `ChangeNotifierProvider(create: (_) => GameController())` 全局注入
2. **消费方式**：使用 `Consumer<GameController>` 进行局部重建，避免不必要的 UI 更新
3. **通知机制**：Controller 中状态变更后调用 `notifyListeners()` 触发 UI 刷新
4. **资源释放**：`dispose()` 方法中取消 Timer，防止内存泄漏

### 1.5 三个难度级别

定义于 `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/difficulty.dart:14-33`：

| 难度 | 名称 | 行数 | 列数 | 地雷数 |
|---|---|---|---|---|
| 初级 | Beginner | 9 | 9 | 10 |
| 中级 | Intermediate | 16 | 16 | 40 |
| 高级 | Expert | 16 | 30 | 99 |

### 1.6 核心游戏机制

#### 首次点击安全（First Click Safe）

实现于 `game_controller.dart:98-103`：
```dart
if (_firstClick) {
  _placeMines(row, col);  // 首次点击时才布雷
  _firstClick = false;
  _startTimer();
  _gameState = GameState.playing;
}
```
- 初始化时棋盘为空，不放置地雷
- 首次点击坐标被传入 `_placeMines`，该坐标被排除在布雷范围外
- 布雷后立即计算周围雷数并启动计时器

#### 长按标记（Long Press Flag）

实现于 `game_controller.dart:137-154`：
- `toggleFlag()` 方法切换旗子状态
- 已揭示格子不能标记
- 首次长按也会启动计时器（与点击逻辑一致）
- `_flagCount` 实时更新，用于剩余雷数显示

UI 层绑定在 `board_widget.dart:44-45`：
```dart
onTap: () => controller.revealCell(row, col),
onLongPress: () => controller.toggleFlag(row, col),
```

#### 自动展开（Flood Fill / Zero-Clear）

实现于 `game_controller.dart:118-135` 的 `_revealCellRecursive` 方法：
- DFS 深度优先遍历
- 遇到 `adjacentMines == 0` 的空格时，递归揭示所有8个方向邻居
- 停止条件：格子已揭示、已标记、或是地雷、或超出边界
- 揭示格子时递增 `_revealedCount`

#### 胜负判定

**失败条件**（`game_controller.dart:105-111`）：点击到地雷时调用 `_revealAllMines()` 显示所有雷，状态设为 lost。

**胜利条件**（`game_controller.dart:166-174`）：每次操作后检查 `_revealedCount == totalCells - mines`，即所有非雷格子都已揭示。

### 1.7 跨平台支持

根据 `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/README.md:77-80`：

- 支持平台：Android、iOS、Web、Windows、macOS、Linux
- 目录结构验证：存在 `android/`、`ios/`、`web/`、`windows/`、`macos/`、`linux/` 各平台目录
- 响应式布局：`board_widget.dart:16-24` 通过 MediaQuery 动态计算格子尺寸，适配不同屏幕
- 大棋盘滚动：使用双向 SingleChildScrollView 支持 Expert 级别（16×30）在小屏设备上滚动

### 1.8 测试目录结构

`file:///d:/AI/.chaos/libs/minitap-ai/demo-app/test/` 目录结构：

```
test/
├── widget_test.dart                   # 通用Widget测试
├── controllers/
│   └── game_controller_test.dart      # GameController单元测试
├── models/
│   ├── cell_test.dart                 # Cell模型测试
│   ├── difficulty_test.dart           # Difficulty模型测试
│   ├── mood_test.dart                 # Mood枚举测试
│   └── user_test.dart                 # User模型测试
└── widgets/
    └── cell_widget_test.dart          # CellWidget组件测试
```

测试分层策略：
- Model 层：纯数据逻辑单元测试
- Controller 层：游戏逻辑状态管理测试
- Widget 层：UI组件渲染与交互测试
- 覆盖率目标：README 声明遵循单元测试覆盖率不低于 80% 的规范

---

## 2. minisweeper Sweep 问题数据集分析

### 2.1 文件结构

`file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/` 目录结构：

```
minisweeper/
├── .git/                              # Git版本控制
├── LICENSE                            # Apache License 2.0
├── README.md                          # 项目说明与功能规格
└── minisweeper_issues.csv             # Sweep问题数据集（11个Issue）
```

### 2.2 README 功能规格分析

文件：`file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/README.md`

这是一个现代化、移动端优先的扫雷游戏功能规格文档，描述了一个待实现的移动应用：

#### 核心功能特性
- **经典扫雷玩法**：挖掘（揭示）、标记旗子、Chord（快速揭示）
- **移动端优先控制**：Dig/Flag 模式切换（无需长按）
- **难度预设**：初级/中级/高级 + 自定义棋盘大小与雷数
- **用户体验优化**：
  - 首次挖掘保证安全
  - 计时器 + 雷数计数器
  - 触觉反馈 + 声音开关（可选）
  - 暂停/恢复
- **统计功能**：各难度最佳时间、胜率、连胜

#### 控制机制设计
1. **模式切换**：底部切换按钮在 Dig（挖掘）和 Flag（标记）模式间切换
2. **Chord 快速揭示**：点击已揭示的数字，当周围旗子数等于数字时，揭示剩余未标记邻居
3. **长按辅助输入**：可选长按快速标记

#### 游戏规则
- 首次移动安全：首次点击后才布雷
- 随机布雷：遵守首次安全规则
- 洪水填充：点击0时自动展开直到遇到数字
- 旗子保护：Dig 模式下旗子防止误触
- Chord 风险：旗子标记错误时触发地雷结束游戏

### 2.3 minisweeper_issues.csv 数据集分析

文件：`file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/minisweeper_issues.csv`

共包含 **11个** 开发任务 Issue，采用 CSV 格式，三列：Title、Description、Labels。

#### Issue 清单与分类

| # | 标题 | 标签 | 模块 |
|---|---|---|---|
| 1 | Implement Grid Data Structure & Cell States | backend, core | 数据结构 |
| 2 | Implement First Click Safe Mine Generation | backend, algorithm | 算法（首次安全） |
| 3 | Implement Recursive Flood Fill (Zero-Clear) | backend, algorithm | 算法（自动展开） |
| 4 | Render Grid & Basic Touch Events | frontend, ui | UI渲染 |
| 5 | Implement Input Toggle (Flag Mode vs. Dig Mode) | frontend, ux | 交互模式 |
| 6 | Implement Long-Press as Secondary Input | frontend, ux | 长按输入 |
| 7 | Implement Chording (Tap on Number) | mechanic, gameplay | Chord机制 |
| 8 | Mobile Viewport Controls (Zoom & Pan) | frontend, mobile-specific | 缩放平移 |
| 9 | Haptic Feedback Integration | polish, mobile-specific | 触觉反馈 |
| 10 | Game Loop State Management (Win/Loss) | core, logic | 胜负状态 |
| 11 | Header UI (Smiley, Timer, Mine Counter) | ui, polish | 头部UI |

#### 数据集特征分析

1. **开发阶段分解**：按后端算法 → 前端UI → 交互体验 → 打磨优化的顺序排列
2. **验收标准格式**：每个 Issue 使用 `- [ ]` 复选框格式列出具体 Requirements
3. **标签分类体系**：
   - backend/frontend：前后端分层
   - core/mechanic/logic：核心玩法逻辑
   - algorithm：算法实现
   - ui/ux：界面与体验
   - gameplay：游戏机制
   - mobile-specific：移动端特有功能
   - polish：体验打磨
4. **Sweep 用途**：这是一个为 AI 代码生成工具（Sweep）准备的任务分解数据集，每个 Issue 都是独立的、可验证的开发任务

### 2.4 与 demo-app 的对比关系

| 维度 | demo-app（已实现） | minisweeper（规格/数据集） |
|---|---|---|
| 状态 | 完整可运行的 Flutter 应用 | 功能规格 + 11个Issue任务单 |
| 标记方式 | 长按标记 | 模式切换（主）+ 长按（辅） |
| Chord功能 | 未实现 | 明确要求实现 |
| 缩放平移 | 滚动（无缩放） | 双指缩放+平移 |
| 触觉反馈 | 无 | Light/Heavy/Selection三级反馈 |
| 暂停功能 | 无 | 支持暂停/恢复 |
| 统计功能 | 无 | 最佳时间/胜率/连胜 |
| 自定义难度 | 仅三个预设 | 支持自定义棋盘和雷数 |
| 用途 | minitest 演示应用 | Sweep AI 开发训练/基准数据集 |

---

## 3. 测试 Profile 四种场景模式（提取自 task4-output.md）

来源：`file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task4-output.md:116-174`

定义于 SKILL.md:195-222，共四种认证/账户配置模式，覆盖从匿名测试到真实账户的全场景。

### 3.1 模式一：@qa.minitap.ai 共享收件箱 OTP 自动读取（默认推荐）

**创建命令**：
```bash
minitest --app $APP test-profile create \
  --name "Pro User" --username "pro@qa.minitap.ai" \
  --about "Pro subscription active, has saved items, payment method on file"
```

**设计要点**：
- 用户名格式：`<prefix>@qa.minitap.ai`，**不设置密码**
- 所有 `@qa.minitap.ai` 地址的邮件投递到共享收件箱
- 测试 Agent 运行时自动读取登录验证码/OTP，无需管理真实凭证
- 留空 username 则自动生成随机地址
- 安全校验：非 `@qa.minitap.ai` 域且无密码的账户会被拒绝创建

**适用场景**：大多数测试场景，快速创建测试账户，无需手动处理验证码。

### 3.2 模式二：BYO 账户（Bring Your Own）—— stdin 密码输入

**创建命令**：
```bash
printf "%s" "$PASSWORD" | minitest --app $APP test-profile create \
  --name "Pro User" --username "real-user@example.com" --password-stdin --about "..."
```

**设计要点**：
- 通过 **stdin 管道传递密码**，避免密码出现在 shell 历史记录或进程列表中
- 安全警示：`--password` 内联传值会被 shell 日志记录，不推荐使用
- 两个密码标志互斥：`--password` 和 `--password-stdin` 不能同时使用
- 密码清除：更新时使用 `update --clear-password` 清除已有密码

**适用场景**：使用用户提供的真实账户进行测试，应用需要密码登录且不支持 OAuth。

### 3.3 模式三：特定状态账户预配置（如 Premium 订阅用户）

**使用方式**：
```bash
# 创建带密码的 @qa.minitap.ai persona
# 然后请用户将该 email+password 在后端关联到 pro/特定状态账户
```

**设计要点**：
- 使用 `<something>@qa.minitap.ai` + **显式设置密码**
- `@qa.minitap.ai` 域保持收件箱可读（用于接收 OTP 验证码）
- 设置密码使得用户可以使用该凭证登录后端进行状态预配置
- 协作流程：创建 profile → 将凭证提供给用户 → 用户在后端将账户关联到特定状态（如 Premium、已保存内容、绑定支付方式等）

**适用场景**：需要测试特定账户状态（如已订阅、有历史数据、有权限限制）的场景。

### 3.4 模式四：无 Persona 绑定（匿名模式）

**设计要点**：
- User Story 未绑定 profile 时，Agent 默认以**匿名用户**身份运行（跳过登录流程）
- 自动降级机制：如果测试流程强制要求认证，运行时自动生成 `<random>@qa.minitap.ai` + 临时密码
- 自动完成注册流程并读取收件箱获取确认邮件/OTP 码
- 无需预先配置即可运行未绑定场景，降低测试准备门槛

**适用场景**：测试游客流程、注册流程、无需登录的功能，或快速冒烟测试。

### 3.5 补充机制

- **默认 Profile**：使用 `test-profile set-default <profile_id>` 设置默认账户，运行 Story 时省略 `--profile` 参数自动绑定
- **第三方 OAuth**：使用 Minitap 共享账户池绑定到对应 Story（同样使用 `@qa.minitap.ai` 域）
- **about 字段注入**：`--about` 参数的内容会注入到测试 Agent 运行时 prompt，描述该 profile 的差异化特征（如"已订阅Pro"、"有3个保存的项目"等）
- **绑定时机**：创建 Story 时用 `--profile` 参数绑定，创建后用 `user-story-binding set-profile` 命令绑定

---

## 4. 环境变量安全管理五重保护机制（提取自 task4-output.md）

来源：`file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task4-output.md:287-309`

定义于 SKILL.md:507-540，Env Set 命令设计了五重安全机制，全方位防止秘密泄露和意外修改。

### 4.1 第一重：Masked 掩码显示（默认）

**机制说明**：
- `minitest --app $APP env list` 命令默认将所有环境变量值掩码显示为 `********`
- 防止执行 list 命令时意外暴露敏感值到终端输出或 CI 日志
- 显式查看需要主动添加 `--show` 标志

**示例**：
```bash
minitest --app $APP env list           # 输出：API_TOKEN=********
minitest --app $APP env list --show    # 输出：API_TOKEN=abc123（明文）
```

### 4.2 第二重：单值 Reveal 暴露（逐字打印）

**机制说明**：
- `minitest --app $APP env get <KEY>` 命令逐字打印单个环境变量的值到 stdout
- 不添加额外格式、前缀或换行，可安全用于 shell 脚本赋值
- 诊断信息输出到 stderr，不污染 stdout 管道

**安全用法**：
```bash
API_TOKEN=$(minitest --app $APP env get API_TOKEN)  # 安全赋值到变量
echo "$API_TOKEN"  # 在脚本内安全使用
```
- 相比 `list --show` 一次性暴露所有变量，`get` 遵循最小权限原则，仅暴露需要的单个值

### 4.3 第三重：Read-Merge-Write 读-合并-写模式

**机制说明**：
- `env set` 和 `env unset` 操作不是覆盖式写入，而是采用读-合并-写模式：
  1. 先从后端获取当前环境变量的完整集合
  2. 在本地应用本次变更（新增/更新/删除指定 key）
  3. 将完整的全量 map 发送回后端
- **关键安全特性**：不会覆盖或清除其他未在本次命令中指定的 key
- 支持幂等操作，重复 set 相同值不会产生副作用

**对比风险场景**：如果采用简单的 PUT 覆盖，并发操作或部分提交可能导致其他环境变量丢失。

**示例**：
```bash
# 假设当前有 KEY_A=1, KEY_B=2
minitest --app $APP env set KEY_C=3 --yes
# 结果：KEY_A=1, KEY_B=2, KEY_C=3（KEY_A和KEY_B保留）
```

### 4.4 第四重：--yes 强制确认机制

**机制说明**：
- 所有产生变更的写操作命令（`set`/`unset`/`clear`）都需要显式提供 `--yes`/`-y` 标志，否则命令拒绝执行
- 属于"安全带"机制，防止 Agent 自动化或 CI 作业意外修改 secrets
- 配合交互式使用时，没有 `--yes` 会输出提示并以非零退出码终止
- 其他破坏性操作（如 delete）使用 `--force` 标志，语义类似但更强调破坏性

**示例**：
```bash
minitest --app $APP env set API_TOKEN abc123        # 拒绝执行，提示需要 --yes
minitest --app $APP env set API_TOKEN abc123 --yes  # 确认执行
```

### 4.5 第五重：--dry-run 预览模式

**机制说明**：
- `--dry-run` 标志打印即将发生的变更 diff，但**不实际修改后端数据**
- Diff 格式使用标准前缀：
  - `+` 表示新增 key
  - `~` 表示修改已有 key 的值
  - `-` 表示删除 key
- 用于在执行前审查变更，确认符合预期后再去掉 `--dry-run` 真正执行
- 特别适合 CI/CD 流水线中的审批环节，先预览再应用

**示例**：
```bash
minitest --app $APP env set API_TOKEN abc123 --dry-run
# 输出预览：
# + API_TOKEN=abc123
# （后端未被修改）

minitest --app $APP env set API_TOKEN abc123 --dry-run --yes
# 即使带 --yes，--dry-run 仍然只预览不执行
```

### 4.6 五重保护机制协同效应

| 保护层 | 防护目标 | 威胁场景 |
|---|---|---|
| Masked显示 | 防止list命令批量泄露 | 终端日志、CI输出被记录时暴露所有secret |
| 单值Reveal | 最小权限暴露 | 脚本只需要一个变量却看到所有 |
| Read-Merge-Write | 防止意外覆盖 | 并发修改、部分提交导致其他变量丢失 |
| --yes确认 | 防止自动化误操作 | Agent/CI无人值守时意外修改secret |
| --dry-run预览 | 变更前审查 | 错误key、错误值被设置前无法发现 |

**典型安全工作流**：
1. `env list` 查看当前配置（掩码状态）
2. `env set NEW_KEY value --dry-run` 预览变更
3. 人工审查 diff 输出（`+`/`~`/`-`）
4. 确认无误后 `env set NEW_KEY value --yes` 执行
5. 脚本中使用 `env get KEY` 安全赋值到变量

---

## 5. 文件引用索引

| 文件路径 | 内容 |
|---|---|
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/README.md` | Flutter扫雷游戏说明文档 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/pubspec.yaml` | 项目依赖配置 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/main.dart` | 应用入口与Provider配置 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/cell.dart` | Cell数据模型 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/difficulty.dart` | 难度级别定义 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/game_state.dart` | 游戏状态枚举 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/mood.dart` | Mood情绪枚举 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/models/user.dart` | User用户模型 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/controllers/game_controller.dart` | 游戏逻辑Controller |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/screens/game_screen.dart` | 主游戏界面 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/screens/difficulty_screen.dart` | 难度选择界面 |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/widgets/board_widget.dart` | 棋盘Widget |
| `file:///d:/AI/.chaos/libs/minitap-ai/demo-app/lib/widgets/cell_widget.dart` | 单元格Widget |
| `file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/README.md` | Sweep数据集功能规格 |
| `file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/minisweeper_issues.csv` | 11个开发任务Issue数据集 |
| `file:///d:/AI/.chaos/libs/minitap-ai/minisweeper/LICENSE` | Apache License 2.0 |
| `file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task4-output.md` | task4分析报告（Profile与Env安全来源） |

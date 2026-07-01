---
id: "dependency-management"
source: "AGENTS.md#临时依赖管理"
x-toml-ref: "../../.meta/toml/.agents/protocols/dependency-management.toml"
---
# 临时依赖管理流程

本流程定义了项目中临时依赖的存放位置、使用规范、清理机制以及禁止提交条款，确保临时依赖与中间产物不会污染版本控制系统，保持仓库整洁与构建可重现性。

## 存放位置规范

| 目录用途 | 存放路径 | 说明 |
|---|---|---|
| 第三方库依赖 | `vendor/` | 存放手动引入的第三方库源码或二进制文件，按库名组织子目录 |
| 任务中间产物 | `.temp/` | 存放任务执行过程中的临时文件、缓存、日志等中间产物 |
| 虚拟环境 | `.venv/` | 存放 Python 虚拟环境，按项目隔离，避免全局污染 |

### vendor/ 标准目录结构

```
vendor/
├── README.md                # 依赖总览文档（必须）
├── VERSION.md               # 版本清单文件（必须）
├── library-a/               # 按库名组织子目录
│   ├── README.md            # 该库的元数据文档（必须）
│   └── ...                  # 库文件
└── library-b/
    ├── README.md
    └── ...
```

### 其他临时目录结构示例

```
.temp/                      # 任务中间产物
│   ├── cache/               # 缓存文件
│   ├── logs/                # 日志文件
│   └── output/             # 临时输出
.venv/                      # Python 虚拟环境
│   ├── Scripts/             # Windows 下虚拟环境脚本
│   └── Lib/                 # 虚拟环境库文件
```

## vendor/ 目录管理规范

### 引入流程

1. **必要性评估**：优先使用包管理器（pip、npm、yarn 等）管理依赖；仅当无法通过包管理器安装、或需要定制修改时，才放入 `vendor/`。
2. **创建标准结构**：首次引入 vendor 依赖时，需创建标准目录结构：
   - `vendor/README.md`：使用项目提供的模板，记录整体依赖清单
   - `vendor/VERSION.md`：使用项目提供的模板，记录各依赖版本
   - 每个依赖子目录必须包含 `README.md` 元数据文件
3. **填写元数据**：每个依赖的 `README.md` 必须包含以下信息：
   - 库名称与版本号
   - 来源地址（GitHub URL、下载链接等）
   - 引入日期
   - 引入原因/用途
   - 许可证类型
   - 修改记录（如有定制修改）
4. **更新版本清单**：将新依赖添加到 `vendor/VERSION.md` 的版本清单中。

### 元数据模板

项目在 `.agents/templates/` 目录下提供标准模板：

- `vendor-README.md.template`：vendor 根目录 README 模板
- `vendor-VERSION.md.template`：版本清单模板
- `vendor-lib-README.md.template`：单个依赖库的 README 模板

### 使用规范

1. **按需引入**：仅在项目确实需要且无法通过包管理器安装时引入。
2. **版本锁定**：`vendor/VERSION.md` 中明确记录每个依赖的精确版本号。
3. **禁止修改上游源码**：除非必要且记录了修改原因和内容，否则不得随意修改 vendor 中第三方库的源码。
4. **最小化原则**：只引入必要的文件，剔除无关的文档、测试、示例等，减小体积。
5. **许可合规**：确认第三方库的许可证允许项目使用方式，在 README 中记录许可证类型。

## 其他临时目录使用规范

1. **中间产物命名规范**：`.temp/` 中的文件应使用有意义的命名，包含任务标识与时间戳，避免无意义临时文件堆积。
2. **虚拟环境隔离**：每个项目应使用独立的 `.venv/` 虚拟环境，禁止跨项目共享虚拟环境；虚拟环境名称统一为 `.venv`，便于工具识别。
3. **禁止混用**：`vendor/` 仅存放第三方依赖，`.temp/` 仅存放中间产物，禁止混用或存放无关文件。

## 清理机制

1. **定期审计 vendor/ 依赖**：每周由 orchestrator 或维护者运行 `check-vendor.py` 脚本审计 vendor 目录：
   - 检查元数据完整性
   - 检查是否有未使用的依赖
   - 验证 .gitignore 规则有效性
2. **清理无用依赖**：移除不再使用的第三方库；清理前应确认无代码引用。
3. **项目完成后清理 .temp/**：任务完成后，相关智能体应清理 `.temp/` 中由该任务产生的中间产物；项目交付前应清空整个 `.temp/` 目录。
4. **虚拟环境按项目隔离**：每个项目维护独立的 `.venv/` 虚拟环境；项目归档或删除时，应同步删除对应的 `.venv/` 目录。
5. **缓存自动过期**：`.temp/cache/` 中的缓存文件建议设置过期时间（如 7 天），超期自动清理。
6. **日志轮转**：`.temp/logs/` 中的日志文件应实施轮转策略，单文件超过 10MB 或保留超过 30 天时自动清理。
7. **清理记录**：重大清理操作应记录清理时间、清理内容与执行者，便于追溯。

## vendor/ 验证脚本

项目提供 `python .agents/scripts/check-vendor.py` 脚本，用于自动化验证 vendor 目录合规性：

| 检查项 | 说明 |
|---|---|
| 目录结构检查 | 验证是否存在必需的 README.md 和 VERSION.md |
| 元数据完整性 | 检查每个依赖子目录是否有 README.md 且包含必需字段 |
| 版本清单一致性 | 验证 VERSION.md 中的清单与实际目录一致 |
| .gitignore 规则 | 确认 vendor/ 已在 .gitignore 中配置忽略 |
| 引用检查（可选） | 扫描代码中是否有引用 vendor 路径 |

运行方式：`python .agents/scripts/check-vendor.py [--fix] [--scan-refs]`

- `--fix`：自动创建缺失的模板文件
- `--scan-refs`：扫描代码中对 vendor 的引用

## 禁止提交条款

以下目录与文件明确禁止提交至 Git 仓库：

| 禁止提交项 | 原因 |
|---|---|
| `vendor/` | 第三方库体积大，应通过包管理器或下载脚本获取 |
| `.temp/` | 中间产物为临时文件，无版本控制价值 |
| `__pycache__/` | Python 编译缓存，可自动生成 |
| `.venv/` | 虚拟环境与机器相关，应按项目独立创建 |
| `node_modules/` | npm 依赖目录，应通过 package.json 恢复 |
| `*.pyc` | Python 编译文件，可自动生成 |
| `*.log` | 日志文件，无版本控制价值 |
| `.DS_Store` | macOS 系统文件，与项目无关 |
| `Thumbs.db` | Windows 系统缩略图缓存，与项目无关 |

### 配套保障措施

1. **.gitignore 已配置忽略规则**：项目根目录的 `.gitignore` 文件已配置上述目录与文件的忽略规则，确保 `git status` 不会显示这些文件。
2. **自动化验证脚本**：
   - `check-gitignore.py`：验证 .gitignore 规则覆盖和 git status 违规
   - `check-vendor.py`：验证 vendor 目录结构和元数据完整性
3. **CI 流水线校验**：持续集成流水线将在推送阶段再次校验仓库内容，确保禁止提交项未被意外纳入版本控制。
4. **违规处理**：若发现禁止提交项已被提交至仓库，应立即通过 `git rm --cached` 移除并提交修正，同时排查 `.gitignore` 规则是否失效。

## Git 子模块依赖管理

Git 子模块（git submodule）是管理外部完整代码仓库的推荐方式，分为两种模式：
- **third_party**：第三方只读子模块，适用于引用外部独立项目、跟踪其版本历史，不需要在本地修改源码
- **owned_collab**：自有协作子模块，适用于引用自有/协作开发的独立项目，允许在本地修改并提交回子模块仓库

### 适用场景对比

| 管理方式 | 适用场景 | 版本控制 | 本地修改 | 版本策略 | 代码引用 |
|---|---|---|---|---|---|
| 包管理器（pip/npm） | 稳定发布的第三方库 | 通过 lock 文件锁定版本 | 不需要 | 锁定版本 | 正常 import |
| vendor/ 手动管理 | 无法通过包管理器获取的库/需要定制修改 | 手动记录版本到 VERSION.md | 允许（需记录修改） | 固定版本 | 允许引用 |
| git submodule (third_party) | 第三方只读独立项目（完整 Git 仓库） | 通过 gitlink 固定 commit | **禁止** | 固定 commit | 禁止直接 import |
| git submodule (owned_collab) | 自有协作独立项目（完整 Git 仓库） | 通过 gitlink 跟踪分支 | 允许（需 push 到子模块仓库） | 跟踪分支 | 条件导入+萃取 |

### 引入流程

1. 评估必要性：确认无法通过包管理器引入，且需要保留其版本历史；确定子模块类型（third_party/owned_collab）
2. 添加子模块：
   - third_party：`git submodule add <repo-url> vendor/<name>`
   - owned_collab：`git submodule add -b <branch> <repo-url> vendor/<name>`（如 `-b main`）
3. 配置 .gitignore：确保 vendor/* 规则下有 `!vendor/<name>/` 白名单（子模块自动处理）
4. 更新元数据：在 vendor/VERSION.md 中添加条目，记录类型、commit 哈希/跟踪分支、版本标签、来源、许可证、用途
5. 更新 vendor/README.md：在依赖清单表中添加条目
6. 提交：`.gitmodules`、`vendor/<name>` gitlink、`vendor/README.md`、`vendor/VERSION.md` 一并提交

### 元数据要求

子模块类型的依赖**不在子模块目录内创建 README.md**（会导致 submodule dirty），而是通过以下文件管理元数据：

- **vendor/VERSION.md**：必须包含「类型」列（third_party/owned_collab）、「跟踪分支」列、精确的 commit 哈希、版本标签、来源地址、引入日期、许可证、用途备注
- **vendor/README.md**：依赖清单表中包含子模块名称、类型、当前版本、引入日期、用途简述
- **.agents/VENDOR-INTEGRATION.md**：详细的集成规范、边界原则、更新流程
- **.gitmodules 配置**：owned_collab 类型必须在 .gitmodules 中配置 `branch = <branch-name>` 字段

### 版本管理

- **[third_party] 固定 commit**：锁定在已验证的 commit 上，不跟踪上游分支；定制需求应通过外部适配层或向上游贡献实现
- **[owned_collab] 跟踪分支**：跟踪指定分支（如 main），通过 `git submodule update --remote` 按需更新
- **更新流程**：遵循 VENDOR-INTEGRATION.md 第6章的4步更新法
- **克隆初始化**：新克隆仓库后需执行 `git submodule update --init`；对于 owned_collab 子模块需确保 branch 配置正确

### 禁止事项

- ❌ [third_party] 在 submodule 目录内创建、修改、删除文件；[owned_collab] 允许但必须 commit/push 到子模块仓库
- ❌ [all] 将 submodule 内的 Python 包安装到主项目虚拟环境
- ❌ [third_party] 在主项目代码中直接 import submodule 内的模块；[owned_collab] 允许条件导入（try/except ImportError）
- ❌ [all] 提交 submodule 内的 modified content 到主仓库（修改必须先 push 到子模块仓库）
- ❌ [all] 在主项目 CI/测试中运行 submodule 的测试套件

### 验证检查

运行 `python .agents/scripts/repo-check.py vendor` 可验证子模块配置合规性。后续将提供增强的集成验证脚本，包含 submodule 工作树清洁度、边界违规、非法引用等深度检查。

> **详细操作规范**：见 [VENDOR-INTEGRATION.md](../VENDOR-INTEGRATION.md)，包含边界划分、交互接口、版本控制、更新流程、环境隔离、模式萃取、故障排查等完整指南。

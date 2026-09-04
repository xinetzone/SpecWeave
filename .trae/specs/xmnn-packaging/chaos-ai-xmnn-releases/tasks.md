# xmnn-releases 版本化发布产物目录 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建目录骨架与基础文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `external/chaos/ai/xmnn-releases/` 目录
  - 创建子目录：`scripts/`、`templates/`
  - 创建 `.gitignore` 文件（排除 whl/tar 等大文件，保留文本文件）
  - 注意：`latest/` 和 `vX.Y.Z/` 不作为静态目录创建，而是作为模板结构在 AGENTS.md 中说明，首次发布时由脚本创建
- **Acceptance Criteria Addressed**: [AC-1, AC-7]
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证 xmnn-releases/ 目录存在
  - `programmatic` TR-1.2: 验证 scripts/ 和 templates/ 子目录存在
  - `programmatic` TR-1.3: 验证 .gitignore 存在且包含 *.whl、*.tar 排除规则
  - `programmatic` TR-1.4: 验证 .gitignore 不排除 *.md、*.json、*.sh、*.template 文件
- **Notes**: 使用 mkdir -p 创建目录；.gitignore 白名单模式保留脚本和模板

## [x] Task 2: 创建 AGENTS.md 规范入口
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 参照 xmnn-runtime/AGENTS.md 的结构创建 xmnn-releases/AGENTS.md
  - 包含：启动协议（步骤1-4）、项目概述、嵌套路由关系图、上下文路由表、核心约束、目录结构说明、快速开始、引用父级规范、变更日志
  - 核心约束需涵盖：版本号命名规范（SemVer）、version.json 必填字段、产物校验要求、脚本规范
  - 目录结构说明需清晰展示 latest/ 和 vX.Y.Z/ 的组织方式
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 验证 AGENTS.md 存在且包含"启动协议"关键词
  - `programmatic` TR-2.2: 验证 AGENTS.md 引用父级 ../AGENTS.md
  - `human-judgement` TR-2.3: 评审AGENTS.md结构完整性，需包含：启动协议、项目概述、嵌套路由图、上下文路由表、核心约束、目录结构、快速开始、变更日志
  - `human-judgement` TR-2.4: 评审核心约束是否覆盖版本号规范、元数据字段、校验要求

## [x] Task 3: 创建 version.json 模板
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `templates/version.json.template` 文件
  - 包含字段：version（语义版本号）、build_date（ISO 8601）、python_version、tvm_version、vta_version、xmnn_version、git_commit（短hash）、whl_filename、whl_sha256、base_image（基础镜像tag）、installed_components（已安装组件列表）
  - 提供示例值和字段注释
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: 验证模板文件存在
  - `programmatic` TR-3.2: 验证JSON为有效格式
  - `programmatic` TR-3.3: 验证包含所有必填字段（version, build_date, python_version, tvm_version, vta_version, xmnn_version, git_commit, whl_filename, whl_sha256）

## [x] Task 4: 创建客户侧安装脚本 install.sh
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `scripts/install.sh`
  - 功能：接收whl文件路径参数 → 校验whl文件存在 → 校验sha256（如有校验和文件）→ pip install --force-reinstall → 自动调用verify.sh验证安装
  - 日志模式：参考项目现有彩色日志（INFO/WARN/ERROR/SUCCESS颜色标记）
  - 错误处理：set -e -o pipefail，关键步骤失败时输出明确错误信息
  - 参数：--whl <path>（必填）、--skip-verify（可选，跳过验证）、--help（帮助信息）
  - 支持相对路径和绝对路径
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 验证脚本存在且可执行（chmod +x）
  - `human-judgement` TR-4.2: 评审脚本包含参数解析、whl存在性检查、pip install、验证调用、错误处理
  - `human-judgement` TR-4.3: 评审日志输出使用彩色标记（与现有项目日志风格一致）
  - `programmatic` TR-4.4: 验证 bash -n install.sh 语法检查通过

## [x] Task 5: 创建客户侧验证脚本 verify.sh
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `scripts/verify.sh`
  - 功能：验证XMNN运行时环境是否正常（不依赖Docker）
  - 验证项（复用verify-runtime.sh逻辑）：
    1. python3 可执行
    2. import tvm 成功
    3. import vta 成功
    4. import xmnn 成功
    5. xmnn._libs 目录存在且包含.so文件
    6. libtvm.so 可加载（ctypes.CDLL）
    7. Python版本与预期一致（可选检查）
  - 输出：每项 [PASS]/[FAIL]，末尾统计 "Result: X/Y PASSED"
  - 返回值：全部通过返回0，有失败返回1
  - 支持 --python <path> 指定Python解释器路径
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 验证脚本存在且可执行
  - `human-judgement` TR-5.2: 评审验证项覆盖tvm/vta/xmnn import、_libs/目录、libtvm.so加载
  - `programmatic` TR-5.3: 验证 bash -n verify.sh 语法检查通过
  - `human-judgement` TR-5.4: 评审输出格式包含[PASS]/[FAIL]标记和最终统计

## [x] Task 6: 更新父级 AGENTS.md 上下文路由
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 读取并更新 `external/chaos/ai/AGENTS.md`
  - 在镜像矩阵/目录表格中添加 xmnn-releases 行
  - 在上下文路由表中添加 xmnn-releases 入口（指向 xmnn-releases/AGENTS.md）
  - 在项目概述中补充"四层结构"说明（原三层：开发→构建→运行时，新增第四层：发布产物）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-6.1: 验证父级AGENTS.md中包含"xmnn-releases"字符串
  - `programmatic` TR-6.2: 验证路由表中包含指向 xmnn-releases/AGENTS.md 的条目
  - `human-judgement` TR-6.3: 评审更新内容与现有表格格式一致，不破坏原有结构

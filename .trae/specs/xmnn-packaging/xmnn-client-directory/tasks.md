# xmnn-client 面向工具链使用者的分发目录 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 创建 xmnn-client/ 目录基础结构
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `external/chaos/ai/` 下创建 `xmnn-client/` 目录
  - 创建子目录：`examples/`、`scripts/`
  - 创建 `.gitignore` 文件（排除 latest/、*.whl、*.whl.sha256 等大文件/产物）
  - 参考 xmnn-releases/.gitignore 保持一致但更精简
- **Acceptance Criteria Addressed**: [AC-1, AC-8]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在：`test -d external/chaos/ai/xmnn-client`
  - `programmatic` TR-1.2: examples/ 和 scripts/ 子目录存在
  - `programmatic` TR-1.3: .gitignore 存在且排除 *.whl、*.whl.sha256、latest/
  - `programmatic` TR-1.4: 目录下无 .whl 文件（开发模式零拷贝）
- **Notes**: 不创建 .agents/ 目录（面向用户不需要开发规范容器）；不创建 latest/ 目录（开发模式下不物理存储whl）

## [ ] Task 2: 创建 AGENTS.md（AI协作者入口）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 xmnn-client/AGENTS.md
  - 包含"启动协议"关键词和标准启动步骤
  - 正确引用父级 `../AGENTS.md`（chaos-ai-npu 路由入口）
  - 明确本目录定位：面向工具链**使用者**（终端用户），非开发者/构建者
  - 明确平台约束：仅支持 Linux 原生 + Windows WSL2，不支持 macOS 原生
  - 路由表只包含用户侧任务：安装(install.sh)、验证(verify.sh)、Hello World、WSL2使用指引、standalone打包
  - 包含核心约束：双模式whl查找、bash-only脚本、计数器规范、版本检测方式
  - 在嵌套路由关系图中与 xmnn-releases、xmnn-runtime 并列
- **Acceptance Criteria Addressed**: [AC-1, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-2.1: AGENTS.md 包含"启动协议"关键词
  - `human-judgement` TR-2.2: 正确引用 ../AGENTS.md 作为父级
  - `human-judgement` TR-2.3: 路由表不包含"添加新版本"、"构建镜像"、"extract-release"等开发者任务
  - `human-judgement` TR-2.4: 明确说明"仅支持Linux/WSL2"平台约束
  - `programmatic` TR-2.5: AGENTS.md 文件存在且非空

## [ ] Task 3: 创建 verify.sh 验证脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 verify.sh，基于现有 [xmnn-releases/scripts/verify.sh](file:///d:/spaces/SpecWeave/external/chaos/ai/xmnn-releases/scripts/verify.sh) 适配
  - 遵循现有脚本规范：`#!/bin/bash` + `set -e -o pipefail`
  - source 父级 `../scripts/lib/logging.sh` 使用统一彩色日志
  - 7项验证：Python可执行、import tvm、import vta、import xmnn、_libs目录存在、libtvm.so ctypes加载、Python≥3.14
  - 版本检测使用 `from importlib.metadata import version; version('xmnn')`（Nuitka兼容）
  - _libs路径：`os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), '../_libs'))`
  - libtvm.so路径：同上目录下的 `libtvm.so`
  - 计数器使用 `PASS_COUNT=$((PASS_COUNT + 1))`（禁止 `((PASS_COUNT++))`）
  - 支持 `--python <path>` 参数指定Python解释器
  - 支持 `--help`/`-h`
  - 输出 `X/7 PASSED` 或 `X/7 PASSED, Y/7 FAILED`，exit code 0/1
  - 脚本开头使用 `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` 获取目录
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-3.1: verify.sh 存在且可执行（chmod +x）
  - `programmatic` TR-3.2: `bash verify.sh --help` 输出使用说明
  - `programmatic` TR-3.3: 计数器代码检查：不包含 `((PASS_COUNT++))` 或 `((VAR++))` 后置递增
  - `programmatic` TR-3.4: 版本检测代码使用 importlib.metadata（grep检查）
  - `programmatic` TR-3.5: 在已安装xmnn的环境中运行返回所有PASS和exit code 0
  - `human-judgement` TR-3.6: 使用统一彩色日志函数（source logging.sh）

## [ ] Task 4: 创建 install.sh 安装脚本（双模式whl查找）
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**: 
  - 创建 install.sh，基于现有 [xmnn-releases/scripts/install.sh](file:///d:/spaces/SpecWeave/external/chaos/ai/xmnn-releases/scripts/install.sh) 但增加双模式查找
  - 遵循现有脚本规范：shebang + set -e -o pipefail + source lib/logging.sh
  - **双模式whl查找逻辑**（按优先级）：
    1. 若指定 `--whl <path>`：使用指定路径
    2. 若 `./latest/xmnn.whl` 存在（standalone模式）：使用本地whl
    3. 若 `../xmnn-releases/latest/xmnn.whl` 存在（开发模式）：使用releases whl
    4. 以上都不存在：报错退出，提示用户运行 sync-from-releases.sh 或指定 --whl
  - 安装步骤：前置检查（whl存在、Python可用、pip可用）→ SHA256校验（若.sha256文件存在）→ `pip install <whl> --force-reinstall --no-deps` → 自动调用 verify.sh（除非 --skip-verify）
  - 参数：`--whl <path>`、`--python <path>`、`--skip-verify`、`--help`/`-h`
  - 零参数默认行为：自动查找whl并安装+验证
  - 安装成功后提示下一步：运行 `python examples/hello-world.py`
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-8]
- **Test Requirements**:
  - `programmatic` TR-4.1: install.sh 存在且可执行
  - `programmatic` TR-4.2: `bash install.sh --help` 输出使用说明
  - `programmatic` TR-4.3: 开发模式：在无 ./latest/ 有 ../xmnn-releases/latest/ 时，自动找到releases whl
  - `programmatic` TR-4.4: standalone模式优先：若 ./latest/xmnn.whl 存在则优先使用本地
  - `programmatic` TR-4.5: 无whl时给出明确错误信息和解决建议
  - `programmatic` TR-4.6: 零参数运行成功后自动调用verify.sh
  - `human-judgement` TR-4.7: 脚本遵循现有彩色日志规范

## [ ] Task 5: 创建 sync-from-releases.sh（standalone打包脚本）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 scripts/sync-from-releases.sh
  - 功能：将 xmnn-releases/latest/ 下的所有文件（xmnn.whl、xmnn.whl.sha256、version.json、release-notes.md）拷贝到 xmnn-client/latest/
  - 用途：创建 standalone 分发包（发给客户时使用，客户机器不需要 xmnn-releases）
  - 前置检查：确认 ../xmnn-releases/latest/ 存在且包含whl
  - 删除旧的 xmnn-client/latest/ 再重新创建（确保干净）
  - 使用 cp -r 拷贝所有文件
  - 输出拷贝的文件列表和总大小
  - 支持 `--help`
  - 遵循脚本规范：shebang + set -e + source logging.sh
- **Acceptance Criteria Addressed**: [AC-3, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: scripts/sync-from-releases.sh 存在且可执行
  - `programmatic` TR-5.2: 运行后 xmnn-client/latest/ 目录包含 xmnn.whl、sha256、version.json
  - `programmatic` TR-5.3: 同步后在 xmnn-client/ 下运行 `bash install.sh` 能成功安装（standalone模式）
  - `programmatic` TR-5.4: --help 输出使用说明

## [ ] Task 6: 创建 Hello World 示例
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 examples/hello-world.py
  - 功能：
    1. 尝试 import tvm、import vta、import xmnn
    2. 使用 importlib.metadata.version 获取 xmnn/tvm 版本号并打印
    3. 打印各模块文件路径（方便用户确认加载位置）
    4. 简单验证：创建一个 trivial TVM 计算（如向量加法）并build/run，证明runtime工作
    5. 输出 "✅ XMNN environment is ready!" 成功信息
  - import失败时给出友好的错误提示和排查建议
  - 代码简洁（≤50行），有注释
  - 注意：Nuitka编译后 xmnn.__version__ 不存在，必须用 importlib.metadata
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: examples/hello-world.py 存在
  - `programmatic` TR-6.2: 在已安装环境中 `python examples/hello-world.py` exit code 0
  - `programmatic` TR-6.3: 输出包含 XMNN 版本号和成功提示
  - `programmatic` TR-6.4: 版本检测使用 importlib.metadata（代码检查）
  - `human-judgement` TR-6.5: 代码简洁易懂，适合作为第一个示例

## [ ] Task 7: 创建 README.md（平台分节快速开始）
- **Priority**: high
- **Depends On**: Task 2, 3, 4, 5, 6
- **Description**: 
  - 文件最开头为"快速开始"区块（≤15行），按平台分三小节：
    - **Linux**：一行命令 `bash install.sh && python examples/hello-world.py`
    - **Windows (WSL2)**：前提说明（需WSL2+Ubuntu）→ 进入WSL → cd到目录 → `bash install.sh`
    - **macOS**：不支持原生，请使用 Docker（xmnn-runtime镜像）或 Linux VM
  - 后续章节（简洁）：
    - 验证安装（verify.sh用法）
    - Standalone分发包（sync-from-releases.sh用法，面向分发场景）
    - 安装指定版本（--whl参数用法）
    - 常见问题（简短FAQ，如import失败、_libs找不到、版本检测）
  - 明确说明：这是面向**使用者**的目录，开发者/发布管理者请去 [xmnn-releases/](../xmnn-releases/)
  - **不包含**：构建说明、Docker镜像构建、extract-release用法、Nuitka编译、开发者流程
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 快速开始区块位于文件最开头，≤15行
  - `human-judgement` TR-7.2: Linux小节第一行命令可直接复制粘贴执行（零参数）
  - `human-judgement` TR-7.3: Windows小节明确说明WSL2前置条件
  - `human-judgement` TR-7.4: macOS小节明确说明不支持原生，指向Docker方案
  - `human-judgement` TR-7.5: 不包含任何开发者构建/发布/extract相关内容
  - `human-judgement` TR-7.6: 提供指向 xmnn-releases/ 的链接（说明开发者去那里）
  - `human-judgement` TR-7.7: 语言简洁，非专业用户可理解

## [ ] Task 8: （可选）在 extract-release.sh 中添加同步钩子
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 修改 [xmnn-releases/scripts/extract-release.sh](file:///d:/spaces/SpecWeave/external/chaos/ai/xmnn-releases/scripts/extract-release.sh)
  - 在脚本末尾（Step 5 更新latest/之后）添加可选同步步骤：
    - 检测 `../../xmnn-client/` 目录是否存在
    - 若存在，调用 `../../xmnn-client/scripts/sync-from-releases.sh`
    - 若不存在或同步失败，仅输出WARN日志，不终止发布流程（set -e下不能因同步失败阻塞发布）
  - 保持最小修改：不改变现有5步流程，仅在末尾追加
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-8.1: extract-release.sh 末尾有条件同步逻辑（检测xmnn-client目录存在）
  - `programmatic` TR-8.2: 同步失败不触发exit（使用 || true 或 warn级日志）
  - `human-judgement` TR-8.3: 修改是增量的，不影响现有5步流程

## [ ] Task 9: 更新父级 AGENTS.md 路由表
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 修改 [external/chaos/ai/AGENTS.md](file:///d:/spaces/SpecWeave/external/chaos/ai/AGENTS.md)
  - 在"嵌套路由关系"图中添加 xmnn-client/ 条目（第五层/并行层，面向使用者）
  - 在"上下文路由表"中添加 xmnn-client 行
  - 在"核心规范入口"表中添加 xmnn-client 行
  - 在项目概述中说明：xmnn-client 面向使用者，xmnn-releases 面向开发者，两者并行
  - 在快速开始中可选添加client安装示例
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 路由表包含 xmnn-client 条目
  - `human-judgement` TR-9.2: 嵌套路由图包含 xmnn-client
  - `human-judgement` TR-9.3: 正确区分 xmnn-client（使用者）vs xmnn-releases（开发者）

## [ ] Task 10: 端到端验证测试
- **Priority**: high
- **Depends On**: Task 3, 4, 5, 6, 7
- **Description**: 
  - 在有 xmnn-releases/latest/whl 的环境中执行：
    1. 目录结构检查（AC-1）
    2. `bash install.sh`（开发模式零参数）→ 验证安装+自动verify（AC-2, AC-9）
    3. `python examples/hello-world.py` → 验证成功（AC-5）
    4. `bash scripts/sync-from-releases.sh` → standalone打包（AC-3）
    5. 模拟standalone环境（临时遮蔽releases路径）→ install.sh仍能工作（AC-3）
    6. README和AGENTS.md人工审核（AC-4, AC-7）
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-8, AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: 目录结构检查通过（所有必要文件存在）
  - `programmatic` TR-10.2: install.sh 开发模式全流程 PASS
  - `programmatic` TR-10.3: hello-world.py 运行成功
  - `programmatic` TR-10.4: sync-from-releases.sh 后 standalone 安装成功
  - `programmatic` TR-10.5: verify.sh 7/7 PASSED
  - `human-judgement` TR-10.6: README平台指引清晰、AGENTS.md规范

# xmnn-client 面向工具链使用者的分发目录 - Product Requirement Document

## Overview
- **Summary**: 在 `external/chaos/ai/` 下创建 `xmnn-client/` 目录，作为面向 XMNN 工具链终端使用者（非开发者）的极简分发包。与现有面向开发者的 `xmnn-releases/` 并行存在，使用者无需了解构建过程、Docker镜像矩阵、发布流程即可一键安装验证。
- **Purpose**: 解决现有 xmnn-releases 混合开发者/使用者视角导致的认知负担问题；为不同平台用户提供清晰的使用指引（Linux原生，Windows通过WSL2）；避免大文件双份拷贝浪费。
- **Target Users**: 
  - 使用 XMNN 工具链的算法工程师（不需要构建工具链本身）
  - 客户现场部署工程师（需要快速安装验证）
  - Linux 原生用户 + Windows 10+ WSL2 用户
  - AI 协作者（为用户提供使用支持时查阅）

## Goals
- 创建 `xmnn-client/` 目录结构，与 `xmnn-releases/` 并行
- 提供 Linux 环境下的 bash 安装/验证脚本（install.sh、verify.sh）
- 安装脚本默认零参数即可安装最新稳定版，安装后自动验证
- 为 Windows 用户提供 WSL2 使用指引和可选的 WSL 启动包装器
- README 包含"30秒快速开始"，按平台给出最短路径命令
- 提供 Hello World 示例验证安装成功
- 建立双模式whl查找机制（开发模式引用releases，standalone模式自包含whl用于分发）
- 提供 AGENTS.md 作为 AI 协作者入口（仅用户支持相关路由）

## Non-Goals (Out of Scope)
- 不修改现有 `xmnn-releases/` 的任何文件或功能（除了可能的同步钩子）
- 不重复存储 whl 大文件（默认通过相对路径引用 xmnn-releases）
- 不提供 GUI 安装器（仅 CLI 脚本）
- 不包含构建工具链、Docker 镜像构建、Nuitka 编译相关内容
- 不包含 .agents/rules/ 开发规范、templates/ 发布模板
- 不替代 xmnn-runtime/ Docker 镜像（Docker 用户继续使用 xmnn-runtime）
- 不提供 Windows 原生 .bat 安装脚本（xmnn 仅支持 Linux，Windows 必须通过 WSL2）
- 不支持 macOS 原生环境（需通过 Linux VM 或 Docker 使用）

## Background & Context

现有四层镜像矩阵：
- L0: chaos-ai-npu（开发镜像，源码挂载）
- L1: xmnn-whl-builder（whl打包镜像，Nuitka编译）
- L2: xmnn-runtime（客户运行时镜像，Docker环境）
- L3: xmnn-releases（发布产物目录，**面向开发者管理发布**）

**关键平台约束**：XMNN 编译产物（Nuitka编译的tvm/vta/xmnn）仅支持 Linux 平台。非 Linux 平台的使用方式：
- **Windows 10+**：通过 WSL2（Windows Subsystem for Linux 2）运行 Ubuntu 子系统，在 WSL2 内使用
- **macOS**：通过 Docker（xmnn-runtime镜像）或 Linux VM 使用
- **Linux**：原生支持，直接运行 bash 脚本

xmnn-releases 当前混合了两种视角：
- 开发者视角：extract-release.sh、.agents/rules/release.md、templates/version.json.template、AGENTS.md 开发者路由
- 使用者视角：install.sh、verify.sh、README.md 使用说明

问题：
1. 使用者进入 xmnn-releases 会被大量开发者文件干扰
2. 现有 README 没有清晰的平台指引（Windows 用户不知道需要 WSL2）
3. README 包含大量开发者文档（提取新版本、Docker构建等），真正用户需要的"安装"信息被淹没
4. 没有 Hello World 示例，用户安装后不知道怎么验证可用
5. 没有 standalone 分发模式，无法单独打包发给客户

## Functional Requirements
- **FR-1**: 创建 `xmnn-client/` 目录，包含 AGENTS.md（用户支持路由）
- **FR-2**: 提供 `install.sh`（Linux/WSL2 bash），零参数默认安装最新版
- **FR-3**: 提供 `verify.sh`（Linux/WSL2 bash），验证环境完整性（7项检查）
- **FR-4**: 安装脚本安装完成后自动调用验证脚本
- **FR-5**: install.sh 支持双模式whl查找：
  - 开发模式（默认）：从 `../xmnn-releases/latest/` 读取 whl
  - Standalone模式：从 `./latest/` 读取 whl（分发打包时使用 sync-from-releases.sh 拷贝）
- **FR-6**: 提供 `scripts/sync-from-releases.sh` 用于创建分发包时将 whl 同步到 xmnn-client/latest/
- **FR-7**: README.md 按平台分节：Linux（直接运行）、Windows（WSL2前置→运行）、macOS（Docker/VM说明）
- **FR-8**: 提供 examples/hello-world.py 最小示例
- **FR-9**: 可选：提供简单的 `wsl-install.bat` Windows包装器（调用 `wsl -d <distro> bash install.sh`），帮助不熟悉WSL命令的用户
- **FR-10**: 在 xmnn-releases/scripts/extract-release.sh 末尾增加同步钩子（可选，仅当xmnn-client/存在时执行）
- **FR-11**: 更新父级 external/chaos/ai/AGENTS.md 路由表，增加 xmnn-client 入口

## Non-Functional Requirements
- **NFR-1（易用性）**: Linux用户从解压到运行hello-world.py ≤ 3分钟；Windows WSL2用户 ≤ 10分钟（含WSL2安装前提）
- **NFR-2（平台明确）**: 仅支持 Linux 原生运行；Windows 必须通过 WSL2（Ubuntu 20.04+）；README 明确说明不支持 macOS 原生
- **NFR-3（零认知）**: Linux用户不阅读额外文档，仅复制README第一行命令即可完成安装
- **NFR-4（可验证）**: 所有脚本 exit code 0 表示成功，非0表示失败
- **NFR-5（可分发）**: 通过 sync-from-releases.sh 打包后，xmnn-client/ 目录可独立分发给客户（包含whl），不依赖 xmnn-releases
- **NFR-6（可维护）**: 开发模式下零同步开销，whl不重复存储
- **NFR-7（AI友好）**: AGENTS.md 遵循 SpecWeave 嵌套路由协议，包含"启动协议"关键词

## Constraints
- **Technical**: 
  - XMNN 仅支持 Linux 平台（硬约束），Windows 必须 WSL2
  - Shell 脚本为 bash，遵循现有日志函数模式（source lib/logging.sh）
  - 脚本必须支持 `--help` 参数
  - 开发模式下 whl 不重复存储（引用 ../xmnn-releases/latest/）
  - Standalone 模式下 whl 存放于 ./latest/（用于分发，.gitignore排除）
  - 计数器必须使用 `VAR=$((VAR + 1))` 而非 `((VAR++))`（set -e 兼容性）
  - 版本检测使用 `importlib.metadata.version('xmnn')`（Nuitka兼容）
  - _libs路径使用 `os.path.join(os.path.dirname(tvm.__file__), '../_libs')`
- **Business**: 
  - 现有开发者工作流不能被破坏
  - xmnn-releases 的 extract-release.sh 修改必须最小化
- **Dependencies**:
  - 开发模式依赖 xmnn-releases/latest/ 存在 whl 文件
  - WSL2 用户需要已安装 WSL2 和 Ubuntu（README中给出指引）
  - 依赖父级 scripts/lib/logging.sh 日志库

## Assumptions
- Linux 用户已有 Python 3.14+ 环境（conda 或系统 Python）
- Windows WSL2 用户在 WSL2 Ubuntu 内有 Python 3.14+ 环境
- xmnn-releases 和 xmnn-client 在同一父目录下（同级）——开发模式前提
- 分发给最终客户时，使用 sync-from-releases.sh 创建 standalone 包，客户机器不需要 xmnn-releases
- WSL2 默认发行版为 Ubuntu（或用户通过 `wsl -d Ubuntu` 指定）

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: xmnn-client/ 目录已创建
- **When**: 列出目录内容
- **Then**: 包含 AGENTS.md、README.md、install.sh、verify.sh、examples/、scripts/sync-from-releases.sh、.gitignore
- **Verification**: `programmatic`
- **Notes**: 不包含 .agents/rules/、templates/、extract-release.sh、install.bat（WSL引导可选）等开发者文件

### AC-2: Linux零参数安装成功
- **Given**: xmnn-releases/latest/ 有有效 whl 文件，Linux/WSL2环境
- **When**: 在 xmnn-client/ 下运行 `bash install.sh`（无参数）
- **Then**: 自动找到 ../xmnn-releases/latest/ 的whl → SHA256校验 → pip install → 自动运行verify.sh → 7/7 PASSED → exit code 0
- **Verification**: `programmatic`

### AC-3: Standalone模式安装成功
- **Given**: 运行 sync-from-releases.sh 后，xmnn-client/latest/ 包含whl
- **When**: 将 xmnn-client/ 拷贝到无 xmnn-releases 的环境，运行 `bash install.sh`
- **Then**: 自动从 ./latest/ 找到whl并安装验证成功
- **Verification**: `programmatic`

### AC-4: README平台指引清晰
- **Given**: 用户打开 README.md
- **When**: 根据操作系统查找安装方式
- **Then**: Linux用户看到一行可复制的bash命令；Windows用户看到WSL2前置条件+进入WSL后的命令；macOS用户看到Docker/VM说明
- **Verification**: `human-judgment`
- **Notes**: 快速开始区块 ≤ 15行，按平台分节

### AC-5: Hello World 示例可运行
- **Given**: 安装成功
- **When**: 在WSL2/Linux中运行 `python examples/hello-world.py`
- **Then**: 输出 XMNN/TVM 版本信息和"XMNN environment is ready!"，exit code 0
- **Verification**: `programmatic`

### AC-6: 发布同步钩子工作
- **Given**: xmnn-client/ 目录已存在，在 xmnn-releases 中运行 extract-release.sh 发布新版本
- **When**: 发布流程完成
- **Then**: xmnn-client/latest/ 自动同步（若使用standalone模式同步）；开发模式无需同步
- **Verification**: `programmatic`

### AC-7: AGENTS.md 符合规范
- **Given**: 打开 xmnn-client/AGENTS.md
- **When**: AI 协作者读取
- **Then**: 包含"启动协议"关键词，正确引用父级 AGENTS.md，路由表只包含用户侧任务（安装、验证、Hello World、WSL指引、故障排查），明确说明"仅支持Linux/WSL2"
- **Verification**: `human-judgment`

### AC-8: 开发模式零whl拷贝
- **Given**: 开发模式下（未运行sync-from-releases.sh）
- **When**: 检查 xmnn-client/ 目录
- **Then**: xmnn-client/ 下无 *.whl 文件，不占用额外磁盘空间
- **Verification**: `programmatic`

### AC-9: verify.sh 7项检查通过
- **Given**: 已成功安装xmnn
- **When**: 运行 `bash verify.sh`
- **Then**: 7/7 PASSED（Python可执行、import tvm、import vta、import xmnn、_libs目录、libtvm.so加载、Python≥3.14），exit code 0
- **Verification**: `programmatic`

## Open Questions
- [ ] 目录命名确认：使用 `xmnn-client/` 还是其他名称（如 `xmnn-dist/`、`xmnn-user/`）？
- [ ] 是否需要提供 `wsl-install.bat` Windows包装器？还是README中直接给出 `wsl -d Ubuntu bash install.sh` 命令即可？
- [ ] macOS 用户是明确标注"不支持，需使用Docker"还是也提供VM指引？
- [ ] check-update 功能是否需要？还是后续迭代？
- [ ] examples/ 除了 hello-world.py 是否需要其他示例（如简单的模型推理示例）？
- [ ] WSL2 前置条件是只给链接（微软官方文档）还是在README中写简要步骤？

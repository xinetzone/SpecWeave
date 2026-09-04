# xmnn-package - 自洽独立用户分发包 - Product Requirement Document

## Overview
- **Summary**: 创建一个完全自洽、零外部依赖、零外部引用的终端用户分发包目录 `xmnn-package/`，可独立复制到任意位置、打包分发。包含自包含的安装脚本、验证脚本、Docker镜像加载脚本、whl包、完整文档和示例代码。
- **Purpose**: 现有 `xmnn-client/` 存在路径耦合（引用 `../xmnn-releases`、`../xmnn-runtime`）、文档耦合（大量外部AGENTS.md引用）、流程耦合（需先sync），用户需要理解五层镜像矩阵。本项目创建一个真正可独立分发的"软件包"，用户拿到即可使用，无需访问开发仓库、无需理解构建流程。
- **Target Users**: XMNN工具链的终端用户（算法工程师、部署工程师），不需要了解Docker构建、Nuitka编译、版本管理等开发者流程。

## Goals
- 创建 `xmnn-package/` 目录结构（git跟踪的模板蓝图）
- 所有脚本零外部路径引用（无 `../` 跳出包目录）
- 提供 `package.sh` 一键打包脚本，从开发仓库资源自动生成可分发的自洽包
- 自洽包内置：whl包（lib/）、Docker镜像tar（docker/，可选）、脚本（bin/）、文档（docs/）、示例（examples/）
- 文档完全自包含，无外部链接引用
- 支持两种使用方式：1) 本地pip安装 2) Docker运行
- 提供3步快速开始：解压 → 安装/加载镜像 → 运行Hello World
- Windows WSL2用户完整指引

## Non-Goals (Out of Scope)
- 不修改现有 `xmnn-client/` 目录（保留为开发仓库内工具）
- 不将Docker镜像tar或whl大文件纳入git（由打包脚本动态生成）
- 不提供Windows原生.bat脚本（继续使用WSL2）
- 不支持macOS原生安装（使用Docker方式）
- 不包含构建工具链（LLVM/cmake/gcc等）
- 不实现自动在线升级功能（仅提供版本检测提示）

## Background & Context
现有五层镜像矩阵中，`xmnn-client/`（L5）仍然是开发仓库的一部分：
- `install.sh` 双模式查找（`./latest/` → `../xmnn-releases/latest/`），存在外部路径依赖
- `AGENTS.md` 有20+处外部引用（父级AGENTS、xmnn-runtime、xmnn-releases）
- 没有内置Docker镜像，用户需自行构建或从registry拉取
- 文档引导用户跳转到其他目录，认知负担重

用户需要的是一个"软件安装包"式的体验——类似下载一个zip，解压后按照README就能用，不需要知道开发仓库的结构。

## Functional Requirements
- **FR-1**: 包目录结构标准化（bin/、lib/、docker/、docs/、examples/）
- **FR-2**: `bin/install.sh` 零参数安装，仅查找包内 `lib/` 下的whl，无外部路径
- **FR-3**: `bin/verify.sh` 环境验证，10+项检查，输出针对性修复建议
- **FR-4**: `bin/docker-setup.sh` Docker镜像管理：自动检测本地是否有xmnn-runtime镜像，没有则从 `docker/` 目录load或提示从registry拉取
- **FR-5**: `bin/hello-world.sh` 一键运行Hello World示例
- **FR-6**: 所有脚本日志函数完全自包含，不source外部lib
- **FR-7**: `docs/` 目录包含完整自包含文档：README.md（快速开始）、INSTALL.md（详细安装）、DOCKER.md（Docker使用）、WSL2.md（Windows指引）、TROUBLESHOOTING.md（故障排查）
- **FR-8**: `examples/hello-world.py` 独立可运行示例
- **FR-9**: `package.sh` 一键打包脚本，从xmnn-releases和xmnn-runtime自动生成可分发的自洽包目录
- **FR-10**: 自洽包根目录包含 `version.json` 元数据
- **FR-11**: 自洽包根目录包含 `README.md`，3步快速开始，无外部链接
- **FR-12**: `.gitignore` 排除大文件（whl、tar、tar.gz、zip）

## Non-Functional Requirements
- **NFR-1**: 核心包（不含Docker镜像tar）大小 < 500MB
- **NFR-2**: 安装脚本执行时间 < 2分钟（pip install为主）
- **NFR-3**: 验证脚本执行时间 < 30秒
- **NFR-4**: 所有脚本支持 `--help` 参数
- **NFR-5**: 所有脚本幂等（可重复执行）
- **NFR-6**: 所有脚本 `set -e -o pipefail`，使用 `VAR=$((VAR+1))` 计数器模式
- **NFR-7**: TTY自动检测，非TTY环境不输出ANSI颜色码
- **NFR-8**: 文档语言为中文
- **NFR-9**: 打包脚本执行时间 < 5分钟（不含Docker export时间）

## Constraints
- **Technical**: 
  - 仅支持Linux原生和Windows WSL2（Ubuntu）
  - 必须使用bash脚本，不提供.bat
  - Python版本要求3.14+（与项目约束一致）
  - Docker方式可选，非强制依赖
  - 脚本中禁止使用 `../` 引用包目录外的路径
  - 脚本禁止source外部文件
  - 文档中禁止引用包目录外的文件路径
- **Business**: 交付物需可通过网盘/邮件分发给客户
- **Dependencies**: 
  - 打包脚本依赖 xmnn-releases/latest/ 有whl包
  - Docker镜像导出依赖 xmnn-runtime:latest 镜像已构建
  - 运行时依赖用户有Python 3.14+或Docker环境

## Assumptions
- 用户在Linux或WSL2 Ubuntu环境中操作
- 用户知道如何打开终端/WSL2
- Docker镜像tar包作为可选组件单独提供（不强制包含在核心包中）
- 打包脚本由开发者在开发环境中运行，终端用户拿到的是打包后的结果
- 现有xmnn-client保留作为开发工具链的一部分，不删除

## Acceptance Criteria

### AC-1: 目录结构自洽性
- **Given**: 打包生成的自洽包目录
- **When**: 将目录复制到任意路径（如 `/tmp/xmnn-package-v1.0.0/` 或Windows的 `D:\xmnn-package\`）
- **Then**: 所有脚本和文档正常工作，无"文件未找到"错误，无外部路径引用
- **Verification**: `programmatic`
- **Notes**: 使用grep检查所有脚本中无 `\.\./` 模式，文档中无 `\.\./` 路径引用

### AC-2: 零参数安装可用
- **Given**: 自洽包目录已复制到目标位置
- **When**: 在包根目录执行 `bash bin/install.sh`
- **Then**: 自动找到lib/下的whl包，完成pip安装，SHA256校验通过，自动运行验证
- **Verification**: `programmatic`

### AC-3: 环境验证完整
- **Given**: XMNN已安装
- **When**: 执行 `bash bin/verify.sh`
- **Then**: 执行10+项检查（Python版本、import tvm/vta/xmnn、_libs目录、libtvm.so加载、版本检测等），输出PASS/FAIL统计
- **Verification**: `programmatic`

### AC-4: Docker方式可用
- **Given**: 用户有Docker环境
- **When**: 执行 `bash bin/docker-setup.sh`
- **Then**: 自动检测本地镜像，若docker/目录有tar包则load，否则提示拉取或使用本地pip安装
- **Verification**: `programmatic`

### AC-5: 文档自包含
- **Given**: 自洽包docs/目录
- **When**: 用户阅读README.md
- **Then**: 3步快速开始清晰完整，无需跳转到其他目录或外部URL即可完成安装和验证
- **Verification**: `human-judgment`

### AC-6: 一键打包脚本可用
- **Given**: xmnn-releases/latest/有whl，xmnn-runtime:latest镜像已构建
- **When**: 在xmnn-package/目录执行 `bash package.sh --version vX.Y.Z`
- **Then**: 在上级目录生成 `xmnn-package-vX.Y.Z/`，包含所有必要文件，可直接分发
- **Verification**: `programmatic`

### AC-7: WSL2指引完整
- **Given**: Windows用户
- **When**: 阅读docs/WSL2.md
- **Then**: 清晰说明如何安装WSL2、如何进入目录、常见问题解决
- **Verification**: `human-judgment`

### AC-8: Hello World端到端
- **Given**: 安装完成
- **When**: 执行 `bash bin/hello-world.sh` 或 `python examples/hello-world.py`
- **Then**: 成功运行，输出XMNN版本信息和计算结果
- **Verification**: `programmatic`

### AC-9: 脚本自包含无外部依赖
- **Given**: 所有bin/下的脚本
- **When**: 检查脚本内容
- **Then**: 无source外部文件，日志函数内嵌定义，无对包目录外路径的硬编码引用
- **Verification**: `programmatic`

### AC-10: version.json元数据完整
- **Given**: 打包生成的自洽包
- **When**: 查看根目录version.json
- **Then**: 包含version、build_date、python_version、xmnn_version、whl_filename、whl_sha256、package_type字段
- **Verification**: `programmatic`

## Open Questions
- [ ] 新目录命名：`xmnn-package/` 是否合适？还是 `xmnn-dist/` / `xmnn-bundle/` / `xmnn-standalone/`？
- [ ] 是否需要同时提供zip/tar.gz打包选项，还是仅生成目录由用户自行压缩？
- [ ] Docker镜像默认是否包含在打包结果中？还是通过 `--with-docker` 参数显式指定？
- [ ] 现有xmnn-client/是否需要标注为"开发用"或添加指向新package的说明？

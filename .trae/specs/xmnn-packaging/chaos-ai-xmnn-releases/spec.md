# xmnn-releases 版本化发布产物目录 - Product Requirement Document

## Overview
- **Summary**: 在 `external/chaos/ai/` 下创建 `xmnn-releases/` 目录，作为 XMNN 客户版本产物的版本化存放仓库。该目录用于存放从 xmnn-whl-builder 构建链产出的 wheel 文件、版本元数据、校验和、发布说明以及客户侧安装/验证脚本，提供脱离 Docker 镜像构建上下文的、可直接交付给客户的文件集合。
- **Purpose**: 现有三层镜像矩阵（chaos-ai-npu → xmnn-whl-builder → xmnn-runtime）覆盖了构建和运行时，但缺乏一个专门存放**已构建、版本化、可交付**产物的目录。wheel 文件封装在 Docker 镜像内部（/opt/xmnn-dist/），客户无法直接获取；版本信息、校验和、发布说明散落各处，缺乏统一管理。本目录填补这一空白。
- **Target Users**: 
  - 内部发布工程师：从构建链提取产物到此目录，打标签发布
  - 客户/现场工程师：从此目录获取特定版本的 whl 和安装脚本进行部署
  - AI 智能体：按 AGENTS.md 路由规范操作此目录

## Goals
- 创建 `xmnn-releases/` 目录骨架，遵循项目 AGENTS.md 嵌套路由规范
- 建立按版本号组织的产物存放结构（vX.Y.Z/ 子目录）
- 提供 latest/ 指针指向最新稳定版本
- 包含版本元数据（version.json）和校验和（sha256）
- 包含客户侧安装脚本和验证脚本
- 更新父级 AGENTS.md 的上下文路由表和镜像矩阵，纳入新目录

## Non-Goals (Out of Scope)
- **不**实现自动从 Docker 镜像提取 whl 的 CI 脚本（后续迭代）
- **不**实现 Docker 镜像 tar 导出（docker save）的存放（后续按需添加）
- **不**修改 xmnn-whl-builder 或 xmnn-runtime 的构建逻辑
- **不**实现版本管理系统（如 Git tag 自动创建）
- **不**包含 npuusertools 等客户侧源码（那是运行时 bind mount 的内容）

## Background & Context

### 现有镜像矩阵
| 层级 | 目录 | 镜像名 | 用途 |
|------|------|--------|------|
| L0 | 根目录 | chaos-ai-npu | 开发镜像（含LLVM/cmake/gcc/onnx/pytorch） |
| L1 | xmnn-whl-builder/ | xmnn-whl-builder | Nuitka编译→wheel打包，whl存于镜像内/opt/xmnn-dist/ |
| L2 | xmnn-runtime/ | xmnn-runtime | 客户轻量运行时（基于conda-latest，从whl-builder COPY whl安装） |

### 缺失环节
- whl 文件构建后存放在 Docker 镜像层中，需 `docker cp` 或挂载卷才能提取
- 没有统一位置存放版本元数据（XMNN_VERSION、PYTHON_VERSION、构建时间、git hash等）
- 没有统一的客户侧安装/验证脚本
- 历史版本产物无组织存放

### 设计原则
- **命名一致性**：遵循 `xmnn-<purpose>` 命名约定（xmnn-whl-builder、xmnn-runtime → xmnn-releases）
- **嵌套路由**：拥有自己的 AGENTS.md，遵循工作区发现协议
- **版本化**：按语义版本号（vX.Y.Z）组织子目录
- **可校验**：每个 whl 附带 sha256 校验和
- **最小可行**：先创建骨架和模板，不填充实际构建产物

## Functional Requirements
- **FR-1**: 创建 `xmnn-releases/` 目录，遵循项目嵌套路由规范，包含 AGENTS.md 入口
- **FR-2**: 目录结构包含 `latest/` 指针目录、`vX.Y.Z/` 版本子目录模板、`scripts/` 客户脚本目录
- **FR-3**: 提供 `version.json` 模板，包含版本号、构建时间、Python版本、依赖组件版本、git hash、校验和等字段
- **FR-4**: 提供客户侧 `install.sh` 脚本（pip install + 验证）
- **FR-5**: 提供客户侧 `verify.sh` 脚本（基于 runtime 的 verify-runtime.sh 逻辑，适用于非Docker环境）
- **FR-6**: 更新父级 `ai/AGENTS.md`，在镜像矩阵和目录结构中纳入 xmnn-releases
- **FR-7**: 提供 `.gitignore`，合理控制大文件（whl/二进制tar）是否纳入版本控制

## Non-Functional Requirements
- **NFR-1**: 目录结构必须清晰，客户无需阅读文档即可理解如何找到特定版本
- **NFR-2**: AGENTS.md 必须包含完整的启动协议和上下文路由表，AI智能体可自动发现
- **NFR-3**: 脚本必须有错误处理和日志输出，与项目现有日志增强模式一致
- **NFR-4**: 所有模板和脚本不得包含硬编码路径，使用相对路径和环境变量

## Constraints
- **Technical**: 
  - 遵循现有 xmnn-* 目录约定
  - AGENTS.md 必须包含"启动协议"关键词
  - shell脚本使用bash，兼容客户可能的Ubuntu/CentOS环境
  - Python版本与runtime镜像一致（conda base环境）
- **Business**: 
  - 客户侧脚本应足够简单，支持现场工程师独立操作
  - 版本号遵循语义化版本（SemVer）
- **Dependencies**:
  - 依赖 xmnn-whl-builder 的构建输出（/opt/xmnn-dist/*.whl）
  - 依赖 xmnn-runtime 的 verify-runtime.sh 验证逻辑

## Assumptions
- **A1**: 客户使用场景以 xmnn-runtime Docker镜像为主，whl文件用于镜像内pip升级或独立conda环境安装
- **A2**: whl文件较大（可能>100MB），默认不纳入git版本控制（通过.gitignore排除），由发布流程单独管理
- **A3**: 初始版本只创建目录骨架和模板，不填充实际版本产物（待构建链产出后由发布脚本填充）
- **A4**: 客户侧验证脚本复用 xmnn-runtime/verify-runtime.sh 的核心逻辑，但适配非Docker环境

## Acceptance Criteria

### AC-1: 目录创建与基本结构
- **Given**: ai/ 目录下不存在 xmnn-releases/
- **When**: 执行创建操作
- **Then**: xmnn-releases/ 目录存在，包含 AGENTS.md、.gitignore、scripts/、templates/ 子目录
- **Verification**: `programmatic`
- **Notes**: 通过文件系统检查验证

### AC-2: AGENTS.md 规范完整性
- **Given**: xmnn-releases/AGENTS.md 已创建
- **When**: AI智能体读取该文件
- **Then**: 文件包含启动协议（步骤1-4）、上下文路由表、核心约束、引用父级规范、变更日志
- **Verification**: `human-judgment`
- **Notes**: 参照 xmnn-runtime/AGENTS.md 的结构和深度

### AC-3: 版本元数据模板
- **Given**: templates/version.json.template 已创建
- **When**: 查看模板内容
- **Then**: 包含 version、build_date、python_version、tvm_version、vta_version、xmnn_version、git_commit、whl_sha256、whl_filename 字段
- **Verification**: `programmatic`
- **Notes**: JSON格式，字段完整

### AC-4: 客户侧安装脚本
- **Given**: scripts/install.sh 已创建
- **When**: 检查脚本
- **Then**: 支持指定whl路径、执行pip install、自动运行验证、有彩色日志输出、错误处理
- **Verification**: `human-judgment`
- **Notes**: 参考项目现有build.sh日志增强模式

### AC-5: 客户侧验证脚本
- **Given**: scripts/verify.sh 已创建
- **When**: 检查脚本
- **Then**: 执行核心验证项（import tvm/vta/xmnn、_libs/目录、libtvm.so可加载、Python版本）、输出PASS/FAIL计数
- **Verification**: `human-judgment`
- **Notes**: 复用 xmnn-runtime/verify-runtime.sh 的验证逻辑

### AC-6: 父级 AGENTS.md 更新
- **Given**: ai/AGENTS.md 已更新
- **When**: 查看镜像矩阵和目录结构
- **Then**: 镜像矩阵/目录列表中包含 xmnn-releases，上下文路由表包含对应入口
- **Verification**: `programmatic`

### AC-7: .gitignore 配置合理
- **Given**: xmnn-releases/.gitignore 已创建
- **When**: 检查规则
- **Then**: 排除 *.whl、*.tar、*.tar.gz 等大文件，但保留 *.md、*.json、*.sh、*.template 等文本文件
- **Verification**: `programmatic`

## Open Questions
- [ ] whl文件是否需要纳入git LFS管理？（当前假设：不需要，通过.gitignore排除，由外部发布流程管理）
- [ ] 是否需要提供Docker镜像导出（docker save）存放位置？（当前假设：不需要，后续按需添加）
- [ ] latest/ 使用symlink还是文件拷贝？（Windows环境对symlink支持有限，建议使用文件拷贝或专门的update-latest.sh脚本）

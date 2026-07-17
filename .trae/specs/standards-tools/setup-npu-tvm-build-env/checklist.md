# NPU TVM 容器化构建环境与 XMNN Git 版本控制 - Verification Checklist

## Docker 环境构建验证

- [x] Dockerfile.conda 存在于 `external/xmhub/npu_tvm/docker/` 目录
- [x] Dockerfile 基于 continuumio/miniconda3 基础镜像
- [x] Dockerfile 配置了国内镜像源（apt 阿里云源、conda 中科大USTC源、pip 阿里云源）
- [x] Dockerfile 创建了独立的非 root 用户（builder）运行构建
- [x] Docker 镜像可成功构建（`docker build -f Dockerfile.conda -t npu-tvm-build:latest .` 无报错）
- [x] 容器内 conda 命令可用，`conda --version` 正常输出版本（26.5.3）
- [x] 容器内 `which conda` 返回 `/opt/conda/bin/conda`
- [x] 容器内 Python 版本 >= 3.14（`python --version` → Python 3.14.6）
- [x] 容器内 pip 使用阿里云源配置正确（pip.conf: mirrors.aliyun.com）
- [x] 容器内 ninja 版本 >= 1.10（`ninja --version` → 1.13.2）
- [x] 容器内 cmake 版本 >= 3.18（`cmake --version` → 4.4.0）
- [x] 容器内 LLVM 版本 >= 22（`llvm-config --version` → 22.1.8）
- [x] 容器内 LLVM_CONFIG 环境变量正确指向 llvm-config（/opt/conda/envs/tvm-build/bin/llvm-config）
- [x] 容器内 gcc/g++ 可用（`gcc --version` → GCC 14.2.0）
- [x] 容器内 conda-build 可用（`conda build --version` → 26.5.0）
- [x] Dockerfile 层排序符合规范（ARG/FROM → ENV → 源 → 系统包 → conda包 → pip包 → 用户 → WORKDIR）
- [x] Dockerfile 注释清晰，关键配置有说明

## Docker 辅助脚本验证

- [x] build_conda.sh 脚本存在且有执行权限
- [x] run_conda.sh 脚本存在且有执行权限
- [x] .dockerignore 文件存在且排除了 build/、__pycache__/、.git 等
- [x] run_conda.sh 正确挂载 npu_tvm 源码目录到容器内 /workspace/npu_tvm
- [x] run_conda.sh 启动后容器内可访问挂载的源码文件
- [x] 脚本包含使用说明注释
- [x] 脚本自动检测 wslc/docker 容器工具，优先 wslc
- [x] run_conda.sh 支持 --non-interactive 模式自动激活 conda 环境
- [x] QUICKSTART.md 新手快速上手指南存在

## CMake 配置验证

- [x] 容器内可成功执行 cmake configure 配置 npu_tvm
- [x] cmake 使用 Ninja 生成器（`-G Ninja`），生成 build.ninja 文件
- [x] cmake 正确找到 LLVM 22（USE_LLVM=/opt/conda/envs/tvm-build/bin/llvm-config, TVM_LLVM_VERSION=221）
- [x] cmake 正确配置 VTA（USE_VTA=ON）
- [x] cmake 正确配置 RPC（USE_RPC=ON）
- [x] cmake 正确配置 Threads（USE_THREADS=ON）
- [x] cmake 正确配置 CUDA=OFF（CPU 版本）
- [x] cmake 正确配置 OpenMP（USE_OPENMP=ON）
- [x] CMAKE_MAKE_PROGRAM 指向 ninja（/opt/conda/envs/tvm-build/bin/ninja）
- [x] CMAKE_BUILD_TYPE=Release 配置正确
- [x] Python3 正确识别（/opt/conda/envs/tvm-build/bin/python3.14, version 3.14.6）

## conda build 验证

- [x] 容器内可启动 conda build 命令（conda-build 26.5.0 已安装）
- [x] conda recipe 路径正确可访问（conda/recipe/ 目录存在）
- [x] 环境变量（TVM_HOME、PYTHONPATH）在文档中有说明

## xmnn Git 仓库验证

- [x] `external/xmhub/xmnn/` 目录已创建
- [x] 目录内存在 `.git/` 子目录（`git init` 成功）
- [x] 默认分支为 main（`git branch` 验证）
- [x] 存在 develop 分支（`git branch -a` 验证）
- [x] 当前在 main 分支上

## xmnn 仓库配置验证

- [x] `.gitignore` 文件存在
- [x] `.gitignore` 包含 Python 忽略规则（__pycache__/、*.pyc、*.so、*.egg-info/、dist/、build/）
- [x] `.gitignore` 包含虚拟环境忽略规则（.venv/、venv/、env/）
- [x] `.gitignore` 包含 CMake/C++ 忽略规则（build/、cmake-build-*/、*.o、*.a、CMakeCache.txt）
- [x] `.gitignore` 包含 IDE 忽略规则（.vscode/、.idea/）
- [x] `.gitignore` 包含日志和测试覆盖率忽略规则
- [x] `.gitignore` 包含系统文件忽略规则（.DS_Store、Thumbs.db）
- [x] `.gitignore` 测试验证：创建的测试文件不被 git status 追踪
- [x] `.gitattributes` 文件存在
- [x] `.gitattributes` 配置了行尾符自动处理（* text=auto）
- [x] `.gitattributes` 标记了二进制文件类型（*.so、*.a、*.whl、图片文件）

## xmnn 提交规范验证

- [x] `.gitmessage` 提交信息模板文件存在
- [x] `.gitmessage` 包含 Conventional Commits 格式说明
- [x] git config commit.template 配置正确（install-hooks.sh 自动配置）
- [x] scripts/ 目录存在
- [x] commit-msg hook 脚本可用（scripts/install-hooks.sh 可安装）
- [x] install-hooks.sh 正确复制 hook 到 .git/hooks/ 并配置 commit.template
- [x] 安装 hook 后，不符合规范的提交被拦截（"bad commit" 无法提交）
- [x] 符合规范的提交可成功（"test: verify hook works" 可提交）
- [x] hook 错误提示信息清晰易懂
- [x] hook 脚本修复了 set -e 导致的 exit code 问题（移除 -e 选项）

## xmnn 初始文档与提交验证

- [x] README.md 文件存在且内容完整
- [x] README.md 包含项目简介（XMNN 是 NPU TVM 配套的深度学习推理工具链）
- [x] README.md 包含分支策略说明（main/develop/feature/*/hotfix/*/release/*）
- [x] README.md 包含提交规范说明（Conventional Commits type 含义表）
- [x] README.md 包含功能开发流程和紧急修复流程
- [x] README.md 包含分支命名规范和标签管理说明
- [x] README.md 包含常用 Git 操作速查表
- [x] 首次提交已完成（`git log --oneline` 显示 2 个提交）
- [x] 首次提交信息符合 Conventional Commits 规范（"chore: 初始化 XMNN 仓库配置"）
- [x] initial-commit 标签存在（`git tag` 验证）
- [x] 工作区干净（`git status` 显示无未提交变更）

## 文档验证

- [x] Docker 使用文档存在（README.conda.md）
- [x] 新手快速上手指南存在（QUICKSTART.md，3步上手）
- [x] 文档包含环境说明（工具链精确版本：conda 26.5.3、Python 3.14.6、ninja 1.13.2、cmake 4.4.0、LLVM 22.1.8、GCC 14.2.0）
- [x] 文档包含镜像构建命令（可直接复制执行）
- [x] 文档包含容器运行命令（含目录挂载说明，支持 wslc/docker 双工具）
- [x] 文档包含环境验证步骤（检查所有工具版本）
- [x] 文档包含 CMake 配置与编译步骤（含配置成功标志）
- [x] 文档包含 conda build 打包步骤
- [x] 文档包含常见问题排查（LLVM 路径、权限、网络问题、Python 版本降级、Docker 空间不足）
- [x] 文档包含镜像源配置说明和切换方法
- [x] xmnn Git 工作流文档存在（README.md 完整覆盖）
- [x] 文档包含分支模型说明（main/develop/feature/*/hotfix/*/release/*）
- [x] 文档包含 Hook 安装方法
- [x] 文档中所有命令语法正确，路径与实际一致

## 端到端验证

- [x] Docker 镜像构建成功（npu-tvm-build:latest, 5.66GB）
- [x] 新启动容器内所有工具版本检查通过（conda 26.5.3、Python 3.14.6、ninja 1.13.2、cmake 4.4.0、LLVM 22.1.8、gcc 14.2.0、conda-build 26.5.0）
- [x] 容器内 cmake configure npu_tvm 成功，build.ninja 生成，所有模块正确识别
- [x] xmnn 仓库所有配置项验证通过（分支 main/develop、.gitignore、commit-msg hook、README、initial-commit tag）
- [x] 所有创建的文件路径正确，无遗漏
- [x] tasks.md 中所有任务标记为已完成
- [x] checklist.md 中所有检查项标记为已完成

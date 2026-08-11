# Chaos AI 可移植Docker镜像优化 - Verification Checklist

> 状态标记说明：[x] = 代码层已实现（可通过代码审查确认）；[ ] = 需要实际构建/运行容器验证

## 基础构建与可移植性
- [ ] 镜像可在无本地基础镜像链的环境独立构建成功（需docker build验证）
- [x] Dockerfile使用 `# syntax=docker/dockerfile:1.7-labs` 语法声明
- [x] 基础镜像是ubuntu:26.04官方镜像，不依赖devcontainer-base本地镜像
- [x] 时区配置正确（三层保证：tzdata + ln -sf + ENV TZ=Asia/Shanghai）
- [x] 支持国内镜像源构建参数（APT_MIRROR/CONDA_MIRROR/PIP_MIRROR）

## 用户与权限安全
- [ ] 默认运行用户是ai（非root），`docker run <image> whoami` 输出ai（需运行验证）
- [x] 支持通过AI_UID/AI_GID构建参数自定义用户ID/组ID
- [x] sshd配置PermitRootLogin no，禁止root通过SSH登录
- [x] GRANT_SUDO构建参数控制是否给ai用户sudo权限（默认yes）
- [x] umask默认配置为0027，新文件默认权限640/750
- [x] /workspace挂载点预创建且属主为ai:ai
- [x] fix-permissions.sh脚本存在，支持dry-run/verbose/quiet模式，含详细诊断日志

## Conda环境管理
- [x] Miniconda正确安装到/opt/conda
- [x] py314专用conda环境已创建，Python 3.14+
- [ ] py314环境默认激活，CONDA_DEFAULT_ENV=py314（需运行验证）
- [ ] pip安装包默认进入py314环境site-packages（需运行验证）
- [ ] 用户可正常执行 `conda create` 创建新环境（需运行验证）
- [x] conda clean -ya、pip cache purge在Stage 7执行

## 多入口环境一致性
- [x] conda-init.sh登录shell自动激活py314环境
- [ ] SSH非交互式登录也能正确加载conda环境（需运行验证）
- [x] Jupyter配置使用py314环境的Python解释器
- [x] 镜像中不创建/opt/venv目录（无双环境混淆）
- [x] ENV PATH中/opt/conda/envs/py314/bin优先于base/bin
- [ ] SSH/cmd/Jupyter三个入口中which python指向同一路径（需运行验证）

## NPU工具链兼容
- [x] chaos-ai-init.sh逻辑保留，COPY到/opt/bin/chaos-ai-init.sh
- [x] /workspace/npu_tvm、/workspace/npuusertools、/workspace/models、/workspace/project挂载点预创建
- [ ] PYTHONPATH配置与原有逻辑兼容（需挂载NPU工具链后运行验证）

## 工具链预装
- [x] LLVM/Clang 22.1.8通过conda-forge安装到py314环境
- [x] CMake ≥4.4.0通过conda-forge安装
- [x] Ninja ≥1.13.2通过conda-forge安装
- [x] patchelf系统包已安装
- [x] scikit-build-core、nuitka、invoke、build等XMNN构建工具在pip install列表中
- [x] pytest、cloudpickle、attrs、torch、onnx等依赖包已在pip install列表中
- [x] JupyterLab/notebook已安装到py314环境（httpx≥0.28）

## 服务与配置
- [x] supervisord主配置+include模式，conf.d/管理sshd/dockerd/jupyter服务
- [x] Docker CE安装（DinD支持），daemon.json含国内镜像加速
- [x] ENTRYPOINT为空数组 `[]`，允许用户覆盖CMD
- [x] CMD默认启动start.sh（内部exec supervisord），保持与现有使用方式兼容
- [x] daemon.json Docker配置存在（DNS/registry-mirrors/storage-driver/log-driver）
- [x] OpenMP环境变量已设置（OMP_NUM_THREADS=4, KMP_DUPLICATE_LIB_OK=TRUE）
- [x] start.sh增强：7阶段诊断启动、ERR trap、步骤计时、彩色日志、二进制预检、挂载诊断
- [x] fix-permissions.sh增强：前后状态扫描、dry-run预览、verbose详情、变更对比、验证阶段

## 文档与元数据
- [x] /opt/docs/conda-environment-guide.md环境管理文档存在（COPY自docs/portable/）
- [x] /etc/chaos-ai-portable-build-info构建元数据文件（Stage 7生成，含版本/路径/镜像源信息）
- [x] Dockerfile分层清晰，8阶段构建，每阶段有标题注释和计时器
- [x] BuildKit cache mount已配置（apt/conda/pip缓存复用）
- [x] 原子化拆分：config/、scripts/、docs/portable/独立目录管理

## 最终验证（需实际构建运行）
- [ ] `docker run --rm <image> python --version` 输出Python 3.14.x
- [ ] `docker run --rm <image> bash -lc 'which python'` 指向py314/bin/python
- [ ] 镜像启动后Jupyter可正常访问（端口8888）
- [ ] SSH可正常登录（端口22）
- [ ] 容器内创建文件到挂载卷时权限为640（umask 0027生效）
- [ ] fix-permissions.sh可正确修复挂载目录权限
- [ ] Docker DinD在--privileged模式下可启动dockerd

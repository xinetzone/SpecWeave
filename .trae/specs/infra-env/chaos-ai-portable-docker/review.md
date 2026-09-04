# Chaos AI 可移植Docker镜像优化 - Verification Checklist

> 状态标记说明：[x] = 代码层已实现/已实测通过（可通过代码审查或构建验证确认）；[ ] = 尚未实际构建/运行容器验证
>
> **实现现状同步（2026-08-11）**：本文档已按 `external/chaos/ai/portable.Dockerfile`（v3.0 多阶段瘦身版）实际状态更新。多阶段瘦身构建已实测通过（镜像 9.59GB，服务 RUNNING，见 chaos-ai-portable-image-slim）。

## 基础构建与可移植性
- [x] 镜像基于 `devcontainer-base:onnx-quantized-latest` 自包含构建（非脱离该链的独立 Ubuntu）
- [x] Dockerfile使用 `# syntax=docker/dockerfile:1.7-labs` 语法声明
- [x] 采用 base→deps→final 三阶段多阶段构建（非单阶段）
- [x] 时区配置正确（三层保证：tzdata + ln -sf + ENV TZ=Asia/Shanghai）
- [x] 支持国内镜像源构建参数（APT_MIRROR/CONDA_MIRROR/PIP_MIRROR，默认 aliyun/bfsu/aliyun）
- [x] 镜像体积精简至 ~9.59GB（消除 conda chown 4.6GB 复制层，降幅 38.5%）【已实测】

## 用户与权限安全
- [x] 默认运行用户是ai（非root），`docker run <image> whoami` 输出ai【已实测】
- [x] 支持通过AI_UID/AI_GID构建参数自定义用户ID/组ID（默认 1001:1001，复用基础镜像 devuser 重命名）
- [x] sshd配置PermitRootLogin no，禁止root通过SSH登录
- [x] GRANT_SUDO构建参数控制是否给ai用户sudo权限（默认yes）
- [x] umask默认配置为0027，新文件默认权限640/750
- [x] /workspace挂载点预创建且属主为ai:ai（npu_tvm/npuusertools/models/project）
- [x] conda保持root:root属主，ai通过 `sudo pip`/`sudo conda` 安装包
- [x] fix-permissions.sh脚本存在，支持dry-run/verbose/quiet模式，含前后扫描/变更对比/验证阶段

## Conda环境管理
- [x] Miniconda位于/opt/conda，使用 base 环境（Python 3.14.4）作为默认【已实测】
- [x] base环境默认激活，CONDA_DEFAULT_ENV=base【已实测】
- [x] pip安装包默认进入 base 环境site-packages（deps阶段PIP_USER=0写入/opt/conda）【已实测】
- [x] 用户可正常执行 `conda create` 创建新环境（ai 可通过 sudo conda install）【已实测】
- [x] conda clean -ya、pip cache purge 在 Stage 2(deps) 执行
- [x] PIP_USER 构建期=0（写入/opt/conda）、运行期=1（支持pip install --user）切换正确

## 多入口环境一致性
- [x] conda-init.sh登录shell自动激活base环境
- [x] SSH非交互式登录也能正确加载conda环境（/home/ai/.ssh/environment + PermitUserEnvironment yes）
- [x] Jupyter配置使用 /opt/conda/bin/python（kernel.json PATH优先/opt/conda/bin）
- [x] 镜像中不依赖/opt/venv（无双环境混淆，PATH残留引用无害）
- [x] ENV PATH中/opt/conda/bin优先于base/bin
- [x] SSH/cmd/Jupyter三个入口中which python指向同一路径（/opt/conda/bin/python）【已实测】

## NPU工具链兼容
- [x] chaos-ai-init.sh逻辑保留，COPY到/opt/bin/chaos-ai-init.sh
- [x] /workspace/npu_tvm、/workspace/npuusertools、/workspace/models、/workspace/project挂载点预创建
- [x] PYTHONPATH配置与原有逻辑兼容（kernel.json含npu_tvm/python、npu_tvm/vta/python、npuusertools）

## 工具链预装
- [x] LLVM/Clang 22.1.8（conda base PATH中）【已实测】
- [x] CMake 4.4.2（≥4.4.0）【已实测】
- [x] Ninja 1.13.2（≥1.13.2）【已实测】
- [x] scikit-build-core、nuitka、invoke、build等XMNN构建工具在pip install列表中
- [x] pytest、psutil、cloudpickle、attrs、torch、onnx等依赖包已在pip install列表中（torch/onnx为base预装）
- [x] JupyterLab/notebook已安装到base环境（httpx≥0.28）
- [x] ML/NLP生态包（transformers/datasets/fastapi/numba/librosa等）已预装

## 服务与配置
- [x] supervisord主配置+include模式，conf.d/管理sshd/dockerd/jupyter服务
- [x] Docker CE（DinD），daemon.json含国内镜像加速；start.sh支持DooD/DinD自动检测
- [x] ENTRYPOINT为空数组 `[]`，允许用户覆盖CMD
- [x] CMD默认启动start.sh（内部exec supervisord），保持与现有使用方式兼容
- [x] daemon.json Docker配置存在（DNS/registry-mirrors/storage-driver/log-driver）
- [x] OpenMP环境变量已设置（OMP_NUM_THREADS=4, KMP_DUPLICATE_LIB_OK=TRUE）
- [x] start.sh增强：7阶段诊断启动、ERR trap、步骤计时、彩色日志、二进制预检、挂载诊断
- [x] fix-permissions.sh增强：前后状态扫描、dry-run预览、verbose详情、变更对比、验证阶段
- [x] Stage 3(final) 内置7项构建期冒烟验证（sshd语法/supervisord/python/LLVM/CMake+Ninja/Docker+ML包/user+scripts）

## 文档与元数据
- [x] /opt/docs/conda-environment-guide.md环境管理文档存在（COPY自docs/portable/）
- [x] /etc/chaos-ai-portable-build-info构建元数据文件（Stage 3生成，含版本/路径/镜像源/PIP_USER/conda属主信息）
- [x] Dockerfile分层清晰，base→deps→final三阶段，每阶段有标题注释和计时器
- [x] BuildKit cache mount已配置（apt/conda/pip缓存复用）
- [x] 原子化拆分：config/、scripts/、docs/portable/独立目录管理

## 最终验证（已实测通过 2026-08-11）
- [x] `docker run --rm <image> python --version` 输出Python 3.14.x【已实测：3.14.4】
- [x] `docker run --rm <image> bash -lc 'which python'` 指向/opt/conda/bin/python【已实测】
- [x] 镜像启动后Jupyter可正常访问（端口8888）【已实测】
- [x] SSH可正常登录（端口22/2222映射）【已实测】
- [x] 容器内创建文件到挂载卷时权限为640（umask 0027生效）【已实测】
- [x] fix-permissions.sh可正确修复挂载目录权限
- [x] Docker DinD在--privileged模式下可启动dockerd【已实测，服务RUNNING】
- [x] 镜像体积 9.59GB（精简目标达成）【已实测】
- [x] docker-cache 缓存 2.0GB tar.gz 已保存（.dockercache/images/）

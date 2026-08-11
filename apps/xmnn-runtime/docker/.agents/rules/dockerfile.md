---
id: "xmnn-runtime-dockerfile-rules"
title: "Dockerfile 运行时构建规范"
source: "docker/Dockerfile"
---
# Dockerfile 运行时构建规范（xmnn-runtime/docker）

<a id="基础约定"></a>
## 基础约定

- 文件名为 `Dockerfile`（位于 `docker/` 子目录），首行声明 BuildKit 语法：`# syntax=docker/dockerfile:1.7-labs`
- **基础镜像**：`npu-tvm-build:conda`（外部预构建镜像，conda环境名`tvm-build`，Python 3.14.6）
- **构建上下文**：xmnn-runtime项目根目录（`../`，即`docker build -f docker/Dockerfile .`）
- **SHELL**：`SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- 构建日志使用英文，结构化前缀：`[BUILD]`/`[INFO]`/`[OK]`/`[TIMER]`/`[VALIDATE]`/`[ERROR]`
- 中文环境：Asia/Shanghai时区（继承或设置）
- 非root用户：`ai`（UID/GID默认1000，可通过ARG调整）
- 无tini：ENTRYPOINT直接为entrypoint.sh（无tini init包装）
- 无SSH/Jupyter/supervisord：纯运行时镜像

<a id="构建参数"></a>
## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| DEBIAN_FRONTEND | noninteractive | apt非交互模式 |
| CONDA_ENV_NAME | tvm-build | conda环境名 |
| AI_UID | 1000 | ai用户UID |
| AI_GID | 1000 | ai用户GID |
| WORKSPACE_DIR | /workspace | 工作目录 |

<a id="6阶段结构runtime-logical-layering-v13"></a>
## 6阶段结构（Runtime Logical Layering v1.3）

变化频率从低到高排列，最大化层缓存复用：

1. **Stage 1/6**：系统包（tzdata/sudo/gosu等）+ 时区Asia/Shanghai + APT镜像源（aliyun）→ 变化频率：**最低**
2. **Stage 2/6**：pip额外依赖（pandas/matplotlib/openpyxl/tqdm/tomlkit）→ 变化频率：**低**
3. **Stage 3/6**：ai用户/组创建 + sudoers配置 + workspace目录权限 → 变化频率：**中**
4. **Stage 4/6**：COPY wheels + xmnn wheel安装 + _libs依赖ldd验证 + 核心导入验证 + TE compute验证 → 变化频率：**中高（★热点）**
5. **Stage 5/6**：COPY entrypoint.sh + chmod + bash语法验证 → 变化频率：**高**
6. **Stage 6/6**：build-info元数据 + 最终验证 + 耗时汇总表 + 清理 → 变化频率：**最低**

<a id="层缓存优化"></a>
## 层缓存优化

- **BuildKit缓存挂载**：
  - apt缓存：`--mount=type=cache,target=/var/cache/apt,sharing=locked`
  - apt列表：`--mount=type=cache,target=/var/lib/apt/lists,sharing=locked`
  - pip缓存：`--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- **COPY隔离**：wheels和init文件在Stage 4 COPY，entrypoint.sh在Stage 5 COPY，确保entrypoint变更不触发xmnn重装
- **变化频率排序**：严格按低→高排列Stage顺序，高频变更在最后阶段

## 构建计时（Build Timing）

每个Stage结束时输出`[TIMER]`标记本阶段耗时+累计耗时：
- Stage 1初始化计时器：`START=<timestamp>`写入`/tmp/.build-timer`
- 每个Stage结束：`S<N>=<timestamp>`追加到计时器文件
- Stage 6输出格式化耗时汇总表（╔═╗框线表格）
- Stage 4标注`★ hotspot`（xmnn安装+验证是最耗时阶段）

<a id="非-root-用户规范"></a>
## 非root用户规范

- 用户名为`ai`，默认UID/GID=1000（通过ARG AI_UID/AI_GID可调）
- 用户创建时检测UID/GID冲突，冲突时自动分配新ID
- 加入sudo组，NOPASSWD:ALL（`/etc/sudoers.d/90-ai`，权限0440）
- WORKDIR为`${WORKSPACE_DIR}`（/workspace），权限2775（setgid）
- 最终USER为ai（通过ENTRYPOINT的gosu切换）

## 镜像源配置

- apt源：sed替换`deb.debian.org`/`security.debian.org`为`mirrors.aliyun.com`
- pip源：ENV设置`PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple`
- conda源：基础镜像已配置

## 验证检查点

- **Stage 4验证**（构建时验证）：
  - ldd检查tvm/_libs/*.so无"not found"依赖
  - 核心导入：`import tvm, vta, xmnn`
  - TE compute验证：`te.compute`简单计算测试
- **Stage 5验证**：`bash -n entrypoint.sh`语法检查
- **Stage 6最终验证**：再次确认核心导入+entrypoint语法+build-info元数据

## 环境变量

| 变量 | 值 | 说明 |
|------|---|------|
| PIP_INDEX_URL | https://mirrors.aliyun.com/pypi/simple | pip阿里云镜像 |
| PIP_TRUSTED_HOST | mirrors.aliyun.com | pip信任主机 |
| PYTHONUNBUFFERED | 1 | Python无缓冲输出 |
| TVM_FFI | ctypes | TVM FFI后端 |
| PATH | conda环境bin优先 | PATH包含tvm-build环境 |
| LD_LIBRARY_PATH | conda环境lib目录 | 动态库搜索路径 |

<a id="安全规范"></a>
## 反模式

- ❌ 不要使用ENTRYPOINT tini包装（本镜像无tini，依赖基础镜像或docker run --init）
- ❌ 不要在Stage 4之后COPY无关文件（会破坏缓存导致xmnn重装）
- ❌ 不要在entrypoint.sh中安装包（运行时不做构建操作）
- ❌ 不要省略bash -n语法验证（Stage 5必须执行）

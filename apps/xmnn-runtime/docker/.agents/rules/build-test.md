---
id: "xmnn-runtime-build-test-rules"
title: "构建与测试流程"
source: "docker/build.sh + docker/verify.sh + docker/build.ps1"
---
# 构建与测试流程（xmnn-runtime/docker）

## 构建前提

- **基础镜像**：必须预先构建`npu-tvm-build:conda`镜像
- **wheels目录**：`wheels/`目录下必须存在`xmnn-*.whl`文件
- **BuildKit**：必须启用DOCKER_BUILDKIT=1（build.sh自动设置）
- **构建上下文**：xmnn-runtime项目根目录（不是docker/子目录）

## 构建命令速查

### Linux/macOS（build.sh）

```bash
# 默认构建（标签xmnn-runtime-skeleton:test）
cd docker/ && bash build.sh

# 指定镜像标签
bash build.sh xmnn-runtime:v1.0

# 启用结构化JSON日志
bash build.sh xmnn-runtime:v1.0 --json
```

### PowerShell（build.ps1）

```powershell
cd docker/
.\build.ps1
```

build.sh自动加载`lib/logging.sh`统一日志库，支持：
- 彩色分级日志（log_info/log_ok/log_warn/log_error）
- JSON事件日志输出到`/tmp/xmnn-runtime-events.jsonl`
- 构建计时（build_duration_seconds指标）
- 镜像大小记录（image_size_mb指标）

## 构建产物

- 镜像标签：`<IMAGE_TAG>`（默认xmnn-runtime-skeleton:test）
- build-info文件：容器内`/etc/xmnn-runtime-build-info`（BUILD_DATE/BASE_IMAGE/CONDA_ENV_NAME等）
- 构建日志：控制台输出含[TIMER] Stage耗时和最终汇总表

## 运行

```bash
# 交互式shell（自动适配/workspace权限）
docker run -it --rm -v $(pwd):/workspace xmnn-runtime-skeleton:test

# 指定UID/GID
docker run -it --rm -e HOST_UID=$(id -u) -e HOST_GID=$(id -g) \
  -v $(pwd):/workspace xmnn-runtime-skeleton:test

# 运行Python脚本
docker run --rm -v $(pwd):/workspace xmnn-runtime-skeleton:test \
  python your_script.py

# 使用init进程（推荐，无内置tini）
docker run -it --rm --init -v $(pwd):/workspace xmnn-runtime-skeleton:test
```

## 验证

### build.sh自动验证

构建过程中Stage 4/6自动执行验证：
1. xmnn wheel安装成功
2. tvm/_libs/*.so动态库ldd无"not found"
3. 核心导入：import tvm, vta, xmnn
4. TE compute测试（简单数组*2运算）

Stage 5/6自动验证：
5. entrypoint.sh bash -n语法正确
6. build-info元数据生成

### verify.sh验证

```bash
bash docker/verify.sh
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| 基础镜像不存在 | `docker images npu-tvm-build:conda` | 需先构建npu-tvm-build:conda |
| wheels/为空 | `ls wheels/xmnn-*.whl` | 需要先生成xmnn wheel包 |
| 构建上下文错误 | build.sh日志中Context路径 | 必须在xmnn-runtime根目录执行build |
| 权限问题（容器内无法写/workspace） | `ls -la /workspace` | 未正确设置HOST_UID/HOST_GID，entrypoint会自动适配 |
| TVM导入失败 | `python -c "import tvm"` | LD_LIBRARY_PATH未包含tvm/_libs，检查entrypoint |
| ldd not found | `ldd <so_path>` | 基础镜像缺少依赖库 |
| pip install慢 | 查看pip输出 | 检查PIP_INDEX_URL是否为阿里云镜像 |
| gosu: command not found | `which gosu` | Stage 1未安装gosu包，检查Dockerfile |

## Dockerfile语法检查

```powershell
# 使用项目根目录的自动化测试脚本
powershell -ExecutionPolicy Bypass -File ../../../.agents/scripts/test-dockerfiles.ps1 -File docker/Dockerfile -Context ..
```

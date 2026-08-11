---
id: "caffe-ffi-build-test-rules"
title: "构建与测试流程"
source: "AGENTS.md#构建与运行"
---
# 构建与测试流程（caffe-ffi-jupyter）

## 重要：构建前提

**必须先构建jupyter-ssh-base基础镜像**：
```bash
cd ../jupyter-ssh-base
bash build.sh
```
build.sh会自动检测jupyter-ssh-base:1.1是否存在，不存在时给出明确错误提示。

**必须在WSL2/Linux环境中构建**（需要编译C++扩展，Windows Docker Desktop无法完成）。

## 构建命令速查

```bash
# 标准构建（WSL2中执行）
bash scripts/build.sh

# 国内镜像源加速
bash scripts/build.sh --cn

# 指定镜像标签
bash scripts/build.sh -t my-caffe-ffi:latest

# 无缓存构建（用于调试）
bash scripts/build.sh --no-cache
```

build.sh会自动处理：
- WSL环境检测与警告
- 基础镜像jupyter-ssh-base:1.1存在性检查
- 构建上下文为SpecWeave根目录（../../），正确COPY caffe-ffi源码
- Dockerfile语法检查
- BuildKit自动启用
- 构建后自动验证

## Docker Compose运行

```bash
# 启动（首次启动自动生成随机Jupyter token）
cd compose/
docker compose up -d

# 查看Jupyter token
docker compose logs jupyter | grep "token="

# 停止
docker compose down

# 重新构建后重启
docker compose up -d --build
```

## 访问

| 服务 | URL | 凭据 |
|-----|-----|------|
| Jupyter Lab | http://localhost:8888 | 首次启动自动生成token（查看日志获取） |
| SSH | ssh -p 2222 jupyteruser@localhost | 默认密码：jupyter（务必修改） |

## 验证caffe-ffi安装

```bash
# 在容器内执行（通过SSH或docker exec）
/opt/conda/envs/caffe-ffi/bin/python -c "import caffe_ffi; print(caffe_ffi.__version__)"

# 验证动态库可解析（无"not found"错误）
ldconfig -p | grep -E 'tvm|caffe'

# 验证C++扩展链接
find /opt/conda/envs/caffe-ffi/lib/python3.14/site-packages/caffe_ffi -name "*.so" -exec ldd {} \; | grep "not found"
# 应该没有输出（所有依赖都能找到）

# 验证Jupyter内核注册
docker compose exec jupyter /opt/venv/bin/jupyter kernelspec list
# 应列出：python3（默认venv）+ caffe-ffi（conda环境）
```

## Dockerfile语法检查

```powershell
# 使用项目根目录的自动化测试脚本（检查FROM依赖）
powershell -ExecutionPolicy Bypass -File ../../.agents/scripts/test-dockerfiles.ps1 -File Dockerfile
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| 基础镜像不存在 | `docker images jupyter-ssh-base` | 未先构建jupyter-ssh-base |
| 构建上下文错误 | 查看build.sh中CONTEXT路径 | 必须是SpecWeave根目录 |
| caffe-ffi编译失败 | 查看构建日志Stage 3 | 缺少编译依赖或protobuf版本不匹配，检查--cn镜像源 |
| 内核不显示caffe-ffi | `jupyter kernelspec list` | ipykernel未安装或--prefix路径错误 |
| import caffe_ffi报错 | `ldd <so_path>` | RPATH或LD_LIBRARY_PATH/ldconfig配置缺失，动态库找不到 |
| conda activate失败 | `source conda.sh && conda info` | Miniconda未正确安装或路径错误 |
| pip install未使用编译环境 | 查看Stage 3日志 | 必须在builder阶段（有build-essential）编译，不是runtime阶段 |
| 在Windows上构建失败 | `uname -a` | 必须在WSL2/Linux环境，C++编译需要Linux工具链 |

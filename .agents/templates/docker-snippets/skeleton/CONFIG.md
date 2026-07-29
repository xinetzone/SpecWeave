# {{PROJECT_NAME}} Runtime Docker Image — 项目骨架

> 基于 **Build-Env-Reuse** 模式（基础镜像环境直用）
> 已验证：2026-07-22 — xmnn-runtime:test 五条红线全通

## 文件清单

```
docker/runtime/
├── Dockerfile              # 镜像构建文件
├── entrypoint.sh           # 入口点脚本（UID/GID映射+conda激活+环境变量）
├── _pkg_init.py            # Python包自初始化脚本（安装到site-packages）
├── pkg_init.pth            # .pth文件（Python启动时自动执行_init）
├── build.sh                # 一键构建脚本
├── verify.sh               # 五条红线快速验证（bash版）
├── run_redlines.py         # 五条红线自动化验证（Python版，无pytest依赖）
├── .dockerignore           # 构建上下文排除规则
└── CONFIG.md               # 配置变量说明（本文件）
```

## 快速开始

### 1. 替换配置变量

编辑 `Dockerfile`、`entrypoint.sh`、`_pkg_init.py`、`pkg_init.pth`，替换所有 `{{PLACEHOLDER}}` 变量。

| 占位符 | 说明 | XMNN示例值 |
|--------|------|-----------|
| `{{PROJECT_NAME}}` | 项目名 | xmnn |
| `{{BUILD_IMAGE_NAME}}` | build镜像名 | npu-tvm-build |
| `{{BUILD_IMAGE_TAG}}` | build镜像tag | conda |
| `{{CONDA_ENV_NAME}}` | conda环境名 | tvm-build |
| `{{PYTHON_VERSION}}` | Python版本（如3.14） | 3.14 |
| `{{PKG_NAME}}` | 包名（用于_init.pth命名） | xmnn |
| `{{PYPI_PACKAGE_NAME}}` | PyPI分发包名 | xmnn |
| `{{LIB_DIR}}` | 包内_libs所在目录名 | tvm |
| `{{CORE_MODULE_COMMA_SEPARATED}}` | 核心import模块（逗号分隔） | tvm, vta, xmnn |
| `{{EXTRA_PIP_PACKAGES}}` | 额外pip包 | pandas matplotlib openpyxl tqdm tomlkit |
| `{{VERIFY_PIP_DEPS}}` | pip安装后验证的包名（逗号分隔，加引号） | 'numpy','scipy','pandas' |
| `{{WHEEL_RELATIVE_PATH}}` | wheel相对Dockerfile的路径 | packaging/dist |
| `{{WHEEL_NAME_PATTERN}}` | wheel文件glob | xmnn-*.whl |
| `{{TIMEZONE_SETUP}}` | 时区设置命令（可为空） | `ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; echo "Asia/Shanghai" > /etc/timezone;` |
| `{{BUILTIN_VERIFY_EXTRA}}` | 构建时额外验证步骤（可为空） | 见下方"功能验证示例" |
| `{{HW_PATH_ENV_VAR}}` | 硬件路径环境变量名（entrypoint.sh中） | VTA_HW_PATH |
| `{{HW_DIR}}` | 硬件配置目录名（site-packages内） | vta |

### 2. 放置wheel文件

将编译好的wheel文件放到 `{{WHEEL_RELATIVE_PATH}}/` 目录下（相对于Docker构建上下文根）。

### 3. 重命名init文件

将骨架中的 `_pkg_init.py` 和 `pkg_init.pth` 重命名为你的包名：

```bash
# 例如包名为 myproject：
mv _pkg_init.py _myproject_init.py
mv pkg_init.pth myproject_init.pth
# 然后修改Dockerfile中对应的COPY路径
```

### 4. 构建镜像

```bash
# 使用build.sh
bash docker/runtime/build.sh -t myproject-runtime:1.0 .

# 或直接docker build
docker build -f docker/runtime/Dockerfile -t myproject-runtime:1.0 .
```

### 5. 验证镜像

**方式一：bash快速验证（verify.sh）**

```bash
# 基础用法
bash docker/runtime/verify.sh myproject-runtime:1.0

# 指定模块
bash docker/runtime/verify.sh myproject-runtime:1.0 --modules myapp,myapp2

# conda环境镜像（需要绕过entrypoint指定python路径）
bash docker/runtime/verify.sh myproject-runtime:1.0 \
    --python /opt/conda/envs/myenv/bin/python \
    --entrypoint-override

# 跳过功能测试
bash docker/runtime/verify.sh myproject-runtime:1.0 --skip-func
```

**方式二：Python自动化验证（run_redlines.py）**

```bash
# 基础用法
python docker/runtime/run_redlines.py --image myproject-runtime:1.0

# conda环境镜像（指定python路径和环境变量）
python docker/runtime/run_redlines.py \
    --image myproject-runtime:1.0 \
    --python /opt/conda/envs/myenv/bin/python \
    --modules myapp,myapp2 \
    --env MY_LIB_PATH=/opt/conda/envs/myenv/lib/python3.14/site-packages

# 跳过功能测试和非root测试
python docker/runtime/run_redlines.py --image myproject-runtime:1.0 --skip-func --skip-r4
```

### 6. 运行容器

```bash
# 交互模式
docker run --rm -it -v $(pwd):/workspace myproject-runtime:1.0

# 执行命令
docker run --rm -v $(pwd):/workspace myproject-runtime:1.0 python -c "import myapp; print('OK')"
```

## 功能验证示例

在 `{{BUILTIN_VERIFY_EXTRA}}` 中可添加构建时验证代码。以下是TVM项目的示例：

```bash
# 替换 {{BUILTIN_VERIFY_EXTRA}} 为：
echo "Verifying TVM TE compute..."; \
python -c "import tvm; from tvm import te; import numpy as np; n = te.var('n'); A = te.placeholder((n,), name='A'); B = te.compute((n,), lambda i: A[i] * 2.0, name='B'); s = te.create_schedule(B.op); mod = tvm.build(s, [A, B], 'llvm', name='double_array'); ctx = tvm.cpu(0); a = tvm.nd.array(np.array([1.0, 2.0, 3.0], dtype='float32'), ctx); b = tvm.nd.array(np.zeros(3, dtype='float32'), ctx); mod(a, b); result = b.numpy().tolist(); assert result == [2.0, 4.0, 6.0], f'Expected [2.0,4.0,6.0], got {result}'; print('  TE compute: [1,2,3] * 2 = [2.0,4.0,6.0] OK')"; \
```

注意：`RUN` 中多行命令必须用 `\` 续行，Python代码必须在同一行或使用 `python -c "..."` 单行格式。

## 设计原则

1. **直接复用build镜像**：不新建conda环境，直接使用build镜像中已配置好的环境
2. **分层缓存优化**：远程pip依赖在COPY wheel之前安装，利用Docker层缓存
3. **非root运行**：entrypoint自动检测挂载目录UID/GID，用gosu降权执行
4. **内置验证**：Dockerfile构建过程中验证import和ldd依赖，失败即停止构建
5. **.pth自初始化**：通过.pth文件设置环境变量，不依赖Docker ENV
6. **UID/GID冲突处理**：用户创建时自动检测并处理已存在的UID/GID
7. **双重验证**：提供bash和Python两种验证方式，适配不同场景
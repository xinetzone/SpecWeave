# DevContainer Base - __VARIANT_NAME__ 变体

&gt; __VARIANT_DESCRIPTION__

## ✨ 特性

- **基础镜像继承**：完全继承 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - 系统 Python venv 位于 `/opt/venv`（Jupyter 等服务使用）
- **__VARIANT_NAME__ 特有功能**：（在此处描述变体提供的功能）

## 📁 目录结构

```
variants/__VARIANT_NAME__/
├── Dockerfile              # __VARIANT_NAME__ 变体构建文件
├── .env.example            # 构建参数配置模板
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

首先需要构建基础镜像 `devcontainer-base:latest`（或依赖的变体镜像）：

```bash
# 在 devcontainer-base 根目录构建基础镜像
cd /path/to/devcontainer-base
bash scripts/build.sh --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant __VARIANT_NAME__

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant __VARIANT_NAME__ --cn

# 构建后验证
bash variants/build.sh --variant __VARIANT_NAME__ --cn --verify
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
docker build -f variants/__VARIANT_NAME__/Dockerfile \
  -t devcontainer-base:__VARIANT_NAME__-latest .

# 国内镜像源构建
docker build -f variants/__VARIANT_NAME__/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:__VARIANT_NAME__-latest .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-__VARIANT_NAME__ \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:__VARIANT_NAME__-latest
```

### 命令模式（调试/一次性任务）

```bash
docker run -it --rm --privileged devcontainer-base:__VARIANT_NAME__-latest bash
```

### DooD 模式（生产/CI 环境，无需 --privileged）

```bash
docker run -d \
  --name devcontainer-__VARIANT_NAME__-dood \
  -p 2223:22 \
  -p 8889:8888 \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:__VARIANT_NAME__-latest
```

## ✅ 验证

```bash
# 变体特有的验证命令
docker run --rm devcontainer-base:__VARIANT_NAME__-latest __EXTRA_VALIDATION__

# 验证系统 venv 仍然存在
docker run --rm devcontainer-base:__VARIANT_NAME__-latest which python
# 输出应包含: /opt/venv/bin/python

# 验证 Jupyter 仍然可用
docker run --rm devcontainer-base:__VARIANT_NAME__-latest /opt/venv/bin/jupyter --version

# 验证 Docker 可用
docker run --rm --privileged devcontainer-base:__VARIANT_NAME__-latest docker --version

# 查看构建信息
docker run --rm devcontainer-base:__VARIANT_NAME__-latest cat /etc/__VARIANT_BUILD_INFO_NAME__
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna（清华）/official（官方） |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |
| `MINICONDA_VERSION` | `latest` | Miniconda 版本（如需要 conda） |
| `PYTHON_VERSION` | `3.14` | Python 版本（如需要） |
| （在此处添加变体特有参数） | | |

## 📋 新增变体 Checklist

按照以下 5 步创建新变体：

1. **复制模板目录**
   ```bash
   cp -r variants/_template variants/&lt;your-variant-name&gt;
   ```

2. **修改 Dockerfile**
   - 替换所有 `__VARIANT_NAME__`、`__VARIANT_DESCRIPTION__` 等占位符
   - 设置正确的 `__BASE_VARIANT__`（留空或填依赖的变体名）
   - 在 `__EXTRA_INSTALL_STEPS__` 区域添加自定义安装逻辑
   - 在 `__EXTRA_VALIDATION__` 区域添加验证命令
   - 设置正确的 `__VARIANT_BUILD_INFO_NAME__`
   - 根据需要调整 Stage 数量和计时器逻辑

3. **更新 .env.example**
   - 在 `__EXTRA_BUILD_ARGS__` 区域添加变体特有的构建参数
   - 删除不需要的参数（如不需要 conda 可删除 Miniconda 相关配置）

4. **更新 README.md**
   - 替换占位符为实际变体信息
   - 完善特性描述、使用说明
   - 更新构建参数表格
   - 添加变体特有的使用文档

5. **注册变体到构建脚本**
   - 编辑 `variants/build.sh`
   - 在 `VARIANTS` 数组中添加新变体，格式为：
     ```bash
     # 无依赖：
     "&lt;variant-name&gt;:&lt;variant-description&gt;:"
     # 有依赖（例如依赖 conda）：
     "&lt;variant-name&gt;:&lt;variant-description&gt;:conda"
     ```
   - 在 `VARIANT_VALIDATE` 数组中添加验证命令：
     ```bash
     VARIANT_VALIDATE["&lt;variant-name&gt;"]="&lt;validation-command&gt;"
     ```

## ⚠️ 注意事项

1. **服务兼容性**：SSH、Docker、Podman、Jupyter 所有服务均继承自基础镜像，使用系统 venv 运行，安装新软件时不要破坏这些服务。

2. **PATH 优先级**：默认 PATH 中 `/opt/venv/bin` 优先，确保 Jupyter 等服务正常。如果需要将新工具加入 PATH，请谨慎评估对服务的影响。

3. **权限**：确保 devuser 能够正常访问安装的工具和文件。

4. **清理**：安装完成后清理缓存（apt、pip、conda、临时文件）以减小镜像体积。

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter）
- （在此处添加相关变体链接）

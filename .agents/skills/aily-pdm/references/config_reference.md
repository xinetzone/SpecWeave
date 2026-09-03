# PDM 配置参考

## 配置文件位置

PDM按以下顺序搜索配置文件：

1. `<PROJECT_ROOT>/pdm.toml` - 项目配置
2. `<CONFIG_ROOT>/config.toml` - 用户配置
3. `<SITE_CONFIG_ROOT>/config.toml` - 站点配置

**CONFIG_ROOT位置**:
- Linux: `~/.config/pdm`
- macOS: `~/Library/Application Support/pdm`
- Windows: `%USERPROFILE%\AppData\Local\pdm`

## 核心配置项

### 项目配置 (pdm.toml)

```toml
[python]
path = ".venv/bin/python"  # Python解释器路径
providers = ["venv", "pyenv", "asdf"]  # Python查找顺序

[mirror]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"  # 镜像源

[distribution]
package = true  # 是否作为可分发包处理
```

### 用户配置 (config.toml)

```toml
[repository.pypi]
url = "https://pypi.org/simple"
username = "__token__"

[repository.testpypi]
url = "https://test.pypi.org/legacy/"
username = "__token__"

[cache]
enable = true
method = "symlink"  # symlink, hardlink, copy
```

## pyproject.toml 配置

### 项目元数据 (PEP 621)

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "A short description of the package"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Author Name", email = "author@example.com"}
]
requires-python = ">=3.9"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
doc = [
    "mkdocs>=1.5.0",
]

[project.urls]
Homepage = "https://github.com/user/repo"
Documentation = "https://docs.example.com"
Repository = "https://github.com/user/repo"
```

### 动态字段

```toml
[project]
name = "my-package"
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "my_package.__version__"}
# 或
version = {file = ["version.txt"]}
```

### 构建系统

```toml
[build-system]
requires = ["pdm-backend", "setuptools>=61.0"]
build-backend = "pdm.backend"
```

### 控制台脚本入口

```toml
[project.scripts]
my-cli = "my_package.cli:main"
```

## PDM特定配置

### 依赖覆盖

```toml
[tool.pdm.resolution.overrides]
package-a = "1.0.0"
package-b = ">=2.0.0,<3.0.0"
package-c = {version = "1.0.0", link = "https://example.com/package.whl"}
```

### 源配置

```toml
[[tool.pdm.source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[[tool.pdm.source]]
name = "private"
url = "https://private.pypi.org/simple"
verify_ssl = true
username = "user"  # 或使用环境变量
```

### 解析选项

```toml
[tool.pdm.resolution]
allow-prereleases = false
respect-source-order = false

[tool.pdm]
excludes = ["test-package"]  # 从锁定文件排除
ignore_package_warnings = ["tensorflow-*"]
```

### 安装选项

```toml
[tool.pdm]
install_cache = true
cache_method = "symlink"
distribution = true

[tool.pdm.options]
add = ["--no-isolation"]
install = ["--no-self"]
```

### 插件配置

```toml
[tool.pdm]
plugins = [
    "pdm-packer",
    "-e file:///${PROJECT_ROOT}/my_plugin"
]
```

## 环境变量

### 索引配置

```bash
export PDM_PYPI_URL="https://pypi.org/simple"
export PDM_PRIVAT_PYPI_USERNAME="user"
export PDM_PRIVAT_PYPI_PASSWORD="pass"
```

### 发布配置

```bash
export PDM_PUBLISH_REPO="pypi"
export PDM_PUBLISH_USERNAME="__token__"
export PDM_PUBLISH_PASSWORD="token-value"
export PDM_PUBLISH_CA_CERTS="/path/to/ca.pem"
```

### 项目配置

```bash
export PDM_PROJECT="/path/to/project"
export PDM_PYTHON="python3.11"
export PDM_IN_VENV="my-venv"
```

### 锁定文件

```bash
export PDM_LOCKFILE="/path/to/pdm.lock"
export PDM_FROZEN_LOCKFILE="1"
```

## 命令行配置

### pdm config

```bash
# 列出所有配置
pdm config

# 获取单个配置
pdm config pypi.url

# 设置配置（全局）
pdm config pypi.url "https://pypi.org/simple"

# 设置配置（项目本地）
pdm config --local pypi.url "https://private.pypi.org/simple"

# 删除配置
pdm config --local --unset pypi.url
```

### 常用配置示例

```bash
# 使用清华镜像
pdm config pypi.url "https://pypi.tuna.tsinghua.edu.cn/simple"

# 使用阿里镜像
pdm config pypi.url "https://mirrors.aliyun.com/pypi/simple/"

# 启用安装缓存
pdm config install.cache on
pdm config install.cache_method hardlink

# 配置Python提供者
pdm config python.providers "pyenv,asdf"
```

## 私有仓库配置

### 带认证的私有源

```toml
[[tool.pdm.source]]
name = "private"
url = "https://${PRIVATE_USER}:${PRIVATE_PASS}@private.pypi.org/simple"
```

### Azure Artifacts

```toml
[[tool.pdm.source]]
name = "azure-feed"
url = "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple/"
```

### 使用keyring存储密码

```bash
# 安装keyring
pdm self add keyring

# 配置Azure Artifacts keyring
pdm self add artifacts-keyring
```

## HTTPS证书配置

```bash
# 索引CA证书
pdm config pypi.ca_certs /path/to/ca_bundle.pem

# 仓库CA证书
pdm config repository.private.ca_certs /path/to/ca_bundle.pem
```

### 使用系统信任存储

```bash
# 安装truststore
pdm self add truststore

# 使用系统证书
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## 依赖组配置

### dependency-groups (推荐)

```toml
[dependency-groups]
dev = ["pytest", "black", "mypy"]
test = ["pytest", "pytest-cov"]
doc = ["mkdocs", "mkdocs-material"]
lint = ["flake8", "ruff"]
```

### optional-dependencies (兼容性)

```toml
[project.optional-dependencies]
dev = ["pytest>=7.0.0"]
all = ["package[dev]", "package[doc]"]
```

## 脚本配置

```toml
[tool.pdm.scripts]
# 基础命令
start = "flask run"
serve = {cmd = "uvicorn main:app --reload"}

# Shell脚本
lint = {shell = "flake8 . || true"}
deploy = {shell = "echo deploy | bash deploy.sh"}

# Python函数
main = {call = "package.module:main"}
init-db = {call = "package.db:init"}

# 组合脚本
check = {composite = ["lint", "type-check", "test"]}

# 带环境变量
dev = "flask run"
dev.env = {FLASK_ENV = "development", DEBUG = "1"}

# 带环境文件
dev.env_file = ".env"

# 自定义工作目录
test.cwd = "tests"
```

## 钩子脚本

```toml
[tool.pdm.scripts]
pre_install = "echo 'Pre-install task'"
post_install = "echo 'Post-install task'"
pre_lock = "echo 'Pre-lock task'"
post_lock = "echo 'Post-lock task'"
pre_build = "echo 'Pre-build task'"
post_build = "echo 'Post-build task'"
pre_publish = "echo 'Pre-publish task'"
post_publish = "echo 'Post-publish task'"

# 前后脚本
pre_test = "echo 'Before tests'"
test = "pytest"
post_test = "echo 'After tests'"
```

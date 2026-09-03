# PDM CLI 命令参考

## 核心命令

### init - 初始化项目

```bash
pdm init [options]
```

**选项**:
- `-n <name>`, `--name <name>`: 项目名称
- `--python <python>`: Python版本要求
- `--license <license>`: 许可证类型
- `--author <author>`: 作者信息
- `-t <template>`, `--template <template>`: 项目模板

### add - 添加依赖

```bash
pdm add [options] <packages>
```

**选项**:
- `-G <group>`, `--group <group>`: 添加到可选依赖组
- `-d`, `--dev`: 添加到开发依赖组
- `-e`, `--editable`: 可编辑模式安装
- `--save-minimum`: 保存最低版本约束
- `--save-compatible`: 保存兼容版本约束
- `--save-exact`: 保存精确版本
- `--save-wildcard`: 不约束版本
- `--pre`, `--prerelease`: 允许预发布版本

### remove - 删除依赖

```bash
pdm remove [options] <packages>
```

**选项**:
- `-G <group>`, `--group <group>`: 从指定组删除
- `-d`, `--dev`: 从开发依赖组删除

### install - 安装依赖

```bash
pdm install [options]
```

**选项**:
- `-G <group>`, `--group <group>`: 安装指定组
- `-d`, `--dev`: 包含开发依赖
- `--prod`, `--production`: 仅生产依赖
- `--no-self`: 不安装项目本身
- `--no-editable`: 非编辑模式安装
- `--clean`: 清理未锁定包

### lock - 锁定依赖

```bash
pdm lock [options]
```

**选项**:
- `--refresh`: 刷新所有依赖版本
- `-u`, `--unconstrained`: 忽略版本约束
- `--override <file>`: 依赖覆盖文件

### sync - 同步工作集

```bash
pdm sync [options]
```

**选项**:
- `--clean`: 清理未锁定包
- `--only-keep`: 仅保留选定包
- `--dry-run`: 仅显示差异

### update - 更新依赖

```bash
pdm update [options] [packages]
```

**选项**:
- `--update-reuse`: 复用现有锁定版本
- `--update-eager`: 递归更新
- `--update-all`: 更新所有
- `-u`, `--unconstrained`: 忽略版本约束
- `--dry-run`: 仅显示差异

## 脚本相关

### run - 运行脚本

```bash
pdm run [options] <script> [args...]
```

**选项**:
- `-l`, `--list`: 列出所有脚本
- `-s`, `--site-packages`: 加载site-packages
- `-k <skip>`: 跳过指定钩子

## 包管理

### list - 列出依赖

```bash
pdm list [options] [patterns...]
```

**选项**:
- `--tree`: 显示依赖树
- `--reverse`: 反向依赖
- `--fields <fields>`: 输出字段
- `--format <format>`: 输出格式(csv/json/markdown/freeze)

### outdated - 检查过时依赖

```bash
pdm outdated [options]
```

### show - 显示包信息

```bash
pdm show [options] [package]
```

**选项**:
- `--name`: 显示名称
- `--version`: 显示版本
- `--summary`: 显示摘要
- `--license`: 显示许可证

## Python管理

### python - Python版本管理

```bash
pdm python [command] [options]
```

**子命令**:
- `install <version>`: 安装Python版本
- `list`: 列出可用版本
- `remove <version>`: 删除版本
- `find`: 查找Python解释器

### use - 切换Python版本

```bash
pdm use [options] [python]
```

**选项**:
- `-f`, `--first`: 选择第一个匹配
- `--auto-install-min`: 自动安装最小版本
- `--auto-install-max`: 自动安装最大版本

## 虚拟环境

### venv - 虚拟环境管理

```bash
pdm venv [command] [options]
```

**子命令**:
- `create [python]`: 创建虚拟环境
- `list`: 列出虚拟环境
- `remove <env>`: 删除虚拟环境
- `activate <env>`: 激活虚拟环境
- `purge`: 清理所有虚拟环境

**创建选项**:
- `-n <name>`, `--name <name>`: 虚拟环境名称
- `-f`, `--force`: 强制重新创建
- `--with-pip`: 同时安装pip

## 构建和发布

### build - 构建分发包

```bash
pdm build [options]
```

**选项**:
- `-d <dir>`, `--dest <dir>`: 输出目录
- `--no-isolation`: 禁用构建隔离
- `-C <setting>`, `--config-setting <setting>`: 构建配置

### publish - 发布到PyPI

```bash
pdm publish [options]
```

**选项**:
- `--no-build`: 不构建，仅发布
- `-r <repo>`, `--repository <repo>`: 发布仓库
- `--username <username>`: 用户名
- `--password <password>`: 密码
- `--ca-certs <file>`: CA证书

## 项目信息

### info - 显示项目信息

```bash
pdm info [options]
```

**选项**:
- `--env`: 显示环境信息
- `--python`: 显示Python信息

### import - 导入项目

```bash
pdm import [options] <file>
```

**支持格式**:
- requirements.txt
- Pipfile
- Poetry pyproject.toml
- Flit pyproject.toml
- setup.py

## 配置管理

### config - 配置管理

```bash
pdm config [options] [key] [value]
```

**选项**:
- `-g`, `--global`: 全局配置
- `--local`: 本地项目配置
- `-l`, `--list`: 列出配置

### cache - 缓存管理

```bash
pdm cache [command]
```

**子命令**:
- `list`: 列出缓存
- `info`: 缓存信息
- `remove <path>`: 删除缓存
- `clear`: 清空缓存

## PDM自管理

### self - PDM自身管理

```bash
pdm self [command]
```

**子命令**:
- `update`: 更新PDM
- `add <packages>`: 添加PDM依赖
- `remove <packages>`: 删除PDM依赖
- `list`: 列出PDM依赖

### completion - Shell补全

```bash
pdm completion <shell>
```

**支持Shell**: bash, zsh, fish, powershell

## 其他命令

### search - 搜索PyPI

```bash
pdm search <query>
```

### fix - 修复项目

```bash
pdm fix [options]
```

### clear - 清除缓存

```bash
pdm clear [options]
```

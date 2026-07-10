---
id: "idempotent-shell-config"
source: ".agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"

[bindings]
rules = []
references = []
skills = []
---
# Shell 幂等配置修改：先删后增 + 原子替换

## 模式概述

Shell 脚本中追加/修改配置时，必须设计为幂等操作（重复执行产生相同结果）；文件写入使用临时文件+mv 原子替换，避免中途写入失败损坏原文件。脚本头部必须启用严格模式。

## 问题现象

- 追加配置行时重复执行导致重复行（如 AllowUsers 行追加多次）
- 多步操作失败后残留副作用（半修改状态）
- 直接写入文件中途失败，原文件被截断损坏
- 未启用严格错误处理，命令失败后脚本继续执行产生连锁错误

## 解决方案

```bash
#!/bin/bash
set -euo pipefail

# ❌ 错误做法：直接追加，重复执行产生重复行
echo "AllowUsers dev" >> /etc/ssh/sshd_config
echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# ✅ 正确做法：先删除旧行（不管是否存在），再追加（幂等）
sed -ri "/^AllowUsers /d" /etc/ssh/sshd_config
echo "AllowUsers dev" >> /etc/ssh/sshd_config

sed -ri "s/^#?PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config

# ✅ 文件替换的原子写法：先写临时文件再mv（避免中途写入失败损坏原文件）
tmp=$(mktemp)
sed -e 's/foo/bar/g' config.yaml > "$tmp"
mv "$tmp" config.yaml  # 原子替换
```

## 关键检查点

1. **脚本头部必须有 `set -euo pipefail`**：
   - `-e`：命令失败立即退出
   - `-u`：使用未定义变量时报错
   - `-o pipefail`：管道中任一命令失败即视为失败
2. **"追加"类操作先 sed 删除旧行**：模式 `/^KEY /d`，再追加
3. **"替换"类操作用 sed `s/^#?KEY.*/VALUE/`**：覆盖原值和注释值
4. **文件写入使用 tempfile + mv 原子替换**：避免中途失败损坏原文件

## 幂等操作模式

### 追加类配置（如 AllowUsers）

```bash
# 模式：先删后增
sed -ri "/^配置键 /d" 目标文件
echo "配置键 值" >> 目标文件
```

### 替换类配置（如 PermitRootLogin）

```bash
# 模式：正则替换，覆盖注释和非注释行
sed -ri "s/^#?配置键.*/配置键 新值/" 目标文件
```

### 原子文件修改

```bash
# 模式：临时文件 -> mv 原子替换
tmp=$(mktemp)
# ... 对 $tmp 进行所有修改 ...
sed -e 's/foo/bar/g' input.yaml > "$tmp"
mv "$tmp" input.yaml  # 原子操作，要么成功要么不修改
```

## 正反例

### 正例

```bash
#!/bin/bash
set -euo pipefail

# 幂等修改 SSH 配置
sed -ri "/^AllowUsers /d" /etc/ssh/sshd_config
echo "AllowUsers dev admin" >> /etc/ssh/sshd_config

sed -ri "s/^#?PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config

# 原子更新配置文件
tmp=$(mktemp)
cat > "$tmp" <<'EOF'
# 生成的配置
key: value
EOF
mv "$tmp" /etc/app/config.yaml
```

### 反例

```bash
#!/bin/bash
# ❌ 无严格模式：命令失败继续执行
# ❌ 直接追加：重复执行重复行
# ❌ 直接重定向：中途失败文件损坏

echo "AllowUsers dev" >> /etc/ssh/sshd_config  # 执行N次就有N行
cat > /etc/app/config.yaml <<EOF  # 如果cat中途失败，原文件丢失
new config
EOF
```

## 适用场景

- 系统配置文件修改（sshd_config、nginx.conf 等）
- Dockerfile 中的配置设置
- 安装脚本、初始化脚本
- CI/CD 流水线中的配置生成

## 注意事项

1. **mktemp 必须在同一文件系统**：`mv` 是原子操作仅当源和目标在同一文件系统；`mktemp` 默认在 `/tmp`，若目标在其他挂载点，用 `mktemp -p "$(dirname "$target")"`
2. **sed -i 兼容性**：GNU sed 和 BSD sed 的 `-i` 参数语法不同（BSD 需要 `-i ''`），跨平台脚本需注意
3. **临时文件清理**：如果脚本在 `mktemp` 之后 `mv` 之前可能失败，需要 trap 清理：`trap 'rm -f "$tmp"' EXIT`
4. **heredoc 引号**：使用 `<<'EOF'`（单引号）避免变量扩展；需要扩展时用 `<<EOF`
5. **Dockerfile 中**：根据项目约定，使用 `printf '%s\n'` 替代 heredoc 以避免行接续语法陷阱

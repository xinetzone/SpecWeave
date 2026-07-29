---
id: "env-var-alias-backward-compat"
source: "jupyter-ssh-base entrypoint.sh ENABLE_SUDO_NOPASSWD→GRANT_SUDO 别名兼容"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/env-var-alias-backward-compat.toml"
---
# 环境变量别名向后兼容模式

## 问题

重命名环境变量时，旧名称已在文档/脚本/用户配置中广泛使用，直接删除旧变量会导致已有用户的配置失效。但 Dockerfile 中 `ENV` 已为新变量设置了默认值，用 `[ -z "${NEW_VAR:-}" ]` 检查"新变量是否未设置"会失败——因为默认值总是存在。

典型症状：
- 设置了 `OLD_VAR=1` 但功能不生效
- 旧文档中的环境变量名在新版本中"静默失效"
- 用 `-z` 检查新变量时永远为 false（因为 ENV 已设默认值）

## 解决方案

用"检查新变量是否仍为默认值"替代"检查新变量是否为空"，确保旧变量名仅在用户未显式设置新变量时才生效：

```bash
# 正确：检查新变量是否仍为默认值
if [ -n "${OLD_VAR:-}" ] && [ "${NEW_VAR:-default}" = "default" ]; then
    export NEW_VAR="${OLD_VAR}"
fi
```

关键点：
1. `${NEW_VAR:-default}` 而非 `${NEW_VAR}` — 防止新变量完全未定义时出错
2. `= "default"` 而非 `= "no"` — 默认值必须与 Dockerfile ENV 中设置的值一致
3. 旧变量优先级低于新变量 — 用户显式设置新变量时，旧变量被忽略

## 代码

### ❌ 反模式：用 `-z` 检查新变量

```bash
# Dockerfile: ENV GRANT_SUDO=no
# 问题：-z 永远为 false，别名永远不会生效
if [ -n "${ENABLE_SUDO_NOPASSWD:-}" ] && [ -z "${GRANT_SUDO:-}" ]; then
    export GRANT_SUDO=yes
fi
```

### ✅ 推荐模式：检查是否仍为默认值

```bash
# Dockerfile: ENV GRANT_SUDO=no
# 正确：仅在用户未显式设置 GRANT_SUDO 时，才从旧变量映射
if [ -n "${ENABLE_SUDO_NOPASSWD:-}" ] && [ "${GRANT_SUDO:-no}" = "no" ]; then
    if [ "${ENABLE_SUDO_NOPASSWD}" = "1" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "yes" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "true" ]; then
        export GRANT_SUDO=yes
    fi
fi
```

## 适用场景

- Docker 镜像 ENTRYPOINT 脚本中重命名环境变量
- 配置文件迁移时保持旧参数名兼容
- CLI 工具重命名选项但需保持向后兼容

## 成熟度

L2 已验证 — jupyter-ssh-base 项目中 `ENABLE_SUDO_NOPASSWD=1` 和 `JUPYTER_CORS_ORIGIN` 两个别名均通过集成测试验证。

## 交叉引用

- 来源：jupyter-ssh-base 项目完工复盘 [retrospective-jupyter-ssh-base-20260724](../../reports/project-reports/retrospective-jupyter-ssh-base-20260724/README.md#L88-L123)
- 关联模式：docker-ssh-noninteractive-path-fix（同项目 Docker 最佳实践系列）
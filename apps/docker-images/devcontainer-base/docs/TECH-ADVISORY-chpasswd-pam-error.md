# TECH-ADVISORY: chpasswd PAM 错误排查与解决指南

**文档ID**: TA-2026-0815-chpasswd-pam
**影响版本**: devcontainer-base 所有变体
**严重级别**: Medium（功能阻塞）
**修复日期**: 2026-08-15
**修复方式**: 密码设置方式从 `chpasswd` 迁移到 `openssl passwd -6` + `usermod -p`

---

## 1. 问题现象

容器启动时设置用户密码失败，日志中出现：

```
chpasswd: (user <username>) pam_chauthtok() failed, error:
Authentication token manipulation error
chpasswd: (line 1, user <username>) password not changed
```

**典型触发场景**：
- 设置 `NON_ROOT_USER=<custom-name>` 运行时重命名用户
- 新建用户后立即设置密码
- Ubuntu 26.04 基础镜像中 usermod/chpasswd 组合操作
- 容器内 `set -euo pipefail` 严格模式下 chpasswd 失败会导致 entrypoint 异常退出

---

## 2. 根因分析（I阶段）

### 2.1 现象描述
`chpasswd` 通过 PAM（Pluggable Authentication Modules）栈设置密码时，在**重命名用户（usermod -l）+ 移动主目录（usermod -d -m）+ 重命名组（groupmod -n）**连续操作后，PAM 可能出现短暂的状态不一致，导致 `pam_chauthtok()` 调用失败。

### 2.2 为什么手动分步测试正常？
我们在调试中发现一个反直觉现象：
- ✅ 手动在容器中执行 usermod 重命名后，单独执行 chpasswd 成功
- ❌ entrypoint.sh 中连续执行 usermod + groupmod + usermod -m 后立即 chpasswd 失败

**可能的原因**：
1. **PAM 名称服务缓存（nscd）延迟**：用户/组重命名后，nscd 缓存未及时刷新
2. **/etc/.pwd.lock 锁文件状态**：连续调用 usermod/groupmod 后锁释放存在时序问题
3. **shadow 文件条目完整性**：连续重命名操作后 shadow 条目的某些字段触发 PAM 校验失败
4. **Ubuntu 26.04 shadow-utils 版本行为变化**：新版本 chpasswd 对用户状态校验更严格

### 2.3 为什么 usermod -p 可靠？
`usermod -p` **绕过 PAM 栈**，直接将哈希后的密码字符串写入 `/etc/shadow` 文件，不经过 PAM 认证模块：

| 方法 | PAM参与 | 可靠性 | 适用场景 |
|------|---------|--------|----------|
| `echo user:pass \| chpasswd` | ✅ 完整PAM栈 | ❌ 重命名后偶发失败 | 用户状态稳定时 |
| `usermod -p <hash> user` | ❌ 直接写shadow | ✅ 100%可靠 | 任何场景（推荐） |
| `passwd --stdin` | ✅ 完整PAM栈 | ❌ 同样受PAM影响 | 交互式 |

---

## 3. 排查指南（标准排查流程）

### 步骤1：确认错误确实是PAM问题
```bash
# 查看容器启动日志，确认错误模式
docker logs <container-id> 2>&1 | grep -A3 -B3 "pam_chauthtok\|Authentication token"

# 进入容器检查用户状态
docker run --rm -it --entrypoint bash <image> -c "
  getent passwd <user>
  getent shadow <user>
  ls -la /etc/shadow /etc/.pwd.lock
"
```

### 步骤2：快速诊断脚本
在容器内运行以下诊断：
```bash
#!/bin/bash
user=ai  # 替换为你的用户名

echo "=== 1. Check user exists ==="
id "$user" || echo "User does not exist!"

echo ""
echo "=== 2. Check shadow file state ==="
getent shadow "$user"
ls -la /etc/shadow /etc/passwd /etc/gshadow

echo ""
echo "=== 3. Check lock file ==="
ls -la /etc/.pwd.lock 2>&1
fuser /etc/.pwd.lock 2>&1 || echo "No processes holding lock"

echo ""
echo "=== 4. Test methods ==="
# Method A: chpasswd
echo "$user:testpass123" | chpasswd && echo "chpasswd: OK" || echo "chpasswd: FAILED"

# Method B: usermod -p with openssl
hash=$(/usr/bin/openssl passwd -6 "testpass123")
usermod -p "$hash" "$user" && echo "usermod -p: OK" || echo "usermod -p: FAILED"
```

### 步骤3：分级修复方案

#### 方案A：紧急热修复（不重建镜像）
如果不能立即重建镜像，在 docker run 时挂载修复后的 entrypoint：
```bash
docker run -d \
  -v /path/to/fixed/entrypoint.sh:/usr/local/bin/entrypoint.sh:ro \
  -e NON_ROOT_USER=ai \
  your-image:tag
```

#### 方案B：永久修复（推荐）
使用我们已实现的 `set_user_password()` 函数：
```bash
set_user_password() {
    local target_user="$1"
    local target_pass="$2"
    local hashed
    if [ -x /usr/bin/openssl ]; then
        hashed=$(/usr/bin/openssl passwd -6 "${target_pass}")
    else
        # Fallback to chpasswd if openssl not available
        echo "${target_user}:${target_pass}" | chpasswd
        return $?
    fi
    usermod -p "${hashed}" "${target_user}"
}

# 使用方式：
set_user_password "${user}" "${USER_PASSWORD}"
set_user_password root "${ROOT_PASSWORD}"
```

#### 方案C：临时Workaround（不推荐）
在 usermod 重命名和 chpasswd 之间加延迟：
```bash
usermod -l "${user}" "${default_user}"
groupmod -n "${user}" "${default_user}" 2>/dev/null || true
usermod -d "/home/${user}" -m "${user}"
sleep 1  # Wait for nscd/cache to settle
echo "${user}:${pass}" | chpasswd  # Still may fail intermittently
```

---

## 4. 为什么 chown /opt/conda 与用户切换无关？

### 问题回答
**chown /opt/conda 操作完全不影响运行时用户切换功能**，原因如下：

| 关注点 | 解释 |
|--------|------|
| **chown 操作对象** | `/opt/conda` 目录下的文件所有者设置为 `root:root`，权限 `a+rX`（所有用户可读+遍历目录） |
| **执行时机** | 在 **Docker build 阶段**（镜像构建时）执行，不是在容器启动时 |
| **执行用户** | Docker build 时以 root 身份执行 |
| **作用** | 确保任何用户（包括 devuser/ai/动态创建的用户）都能**读取并执行** conda 环境中的 Python 和包，不会出现 Permission denied |
| **与用户切换的关系** | ❌ 没有关系——它只解决"用户能否访问conda"的权限问题，不解决"用户如何被创建/重命名"的身份管理问题 |

### 类比理解
- **用户切换（usermod/set_user_password）**：像"给员工办入职/改名"——解决的是身份认证问题
- **chown /opt/conda**：像"给所有员工发办公楼门禁卡"——解决的是资源访问权限问题
- 两者是独立的正交关注点：入职流程不需要重新刷门禁，刷门禁也不需要重新办入职

### 修复用户切换时为什么不需要碰 chown？
1. ✅ `/opt/conda` 权限已经在镜像构建时正确设置为 `root:root + a+rX`
2. ✅ 动态创建的任何用户（无论叫 devuser 还是 ai）都属于"所有用户"范畴，天然有读+执行权限
3. ✅ pip install 包虽然可能以 root 身份运行，但 `chmod a+rX` 已确保所有用户可读
4. ❌ 如果把 `/opt/conda` chown 给某个具体用户（如 devuser），**反而会破坏**多用户支持——切换为 ai 用户后反而没权限了

---

## 5. 可复用模式萃取（E阶段）

### 模式名称：Shadow Direct Hash Password Setting（容器内密码设置可靠模式）

**触发场景**：
- Docker 容器 entrypoint 脚本中需要设置用户密码
- 涉及用户创建/重命名后立即设置密码
- Ubuntu/Debian 基础镜像中使用 shadow-utils
- 需要支持运行时动态用户名（NON_ROOT_USER）

**核心步骤**：
1. ✅ 优先使用 `/usr/bin/openssl passwd -6` 生成 SHA512 哈希
2. ✅ 使用 `usermod -p <hash> <user>` 直接写入 shadow 文件
3. ✅ 保留 chpasswd 作为 fallback（openssl 不可用时）
4. ❌ 不要依赖 PAM 栈进行非交互式密码设置
5. ❌ 不要在重命名用户后立即调用 chpasswd（即使加 sleep 也不可靠）

**反模式**：
- ❌ `echo user:pass | chpasswd` —— 在用户重命名场景下偶发 PAM 错误
- ❌ `echo user:pass | chpasswd -c SHA512` —— 仍然经过 PAM，同样可能失败
- ❌ 依赖 `sleep` 等待 PAM 缓存刷新 —— 时序问题不可靠

**验证清单**：
- [ ] 默认用户 devuser 密码正常设置
- [ ] NON_ROOT_USER 动态用户密码正常设置
- [ ] GRANT_SUDO=yes 时 sudo NOPASSWD 正常工作
- [ ] su - <user> 可使用密码登录
- [ ] 无 pam_chauthtok/Authentication token manipulation error

---

## 6. 预防措施

1. **entrypoint 脚本中统一使用 set_user_password()** 函数，不直接调用 chpasswd
2. **每次修改 entrypoint 用户管理逻辑后**，必须测试以下场景：
   - 默认用户（不设置 NON_ROOT_USER）
   - 动态重命名用户（NON_ROOT_USER=xxx）
   - USER_PASSWORD 显式设置
   - 随机密码生成（不设置 USER_PASSWORD）
   - ROOT_PASSWORD + ALLOW_ROOT_SSH=yes
3. **Dockerfile 中验证 openssl 存在**：base 镜像构建时确保 `/usr/bin/openssl` 可用
4. **添加集成测试**：在 variants/test-*.sh 中加入密码设置验证用例

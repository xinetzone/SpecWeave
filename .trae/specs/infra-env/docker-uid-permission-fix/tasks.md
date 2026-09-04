# Docker 跨 UID 权限问题修复 - 任务分解

## 任务依赖关系

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6
                              ↓
                           Task 7 (Review)
```

---

## Task 1: 重构 entrypoint.sh 权限初始化模块

**优先级**: high  
**对应 AC**: AC1, AC2, AC3, AC4, AC5  
**修改文件**: `apps/docker-images/devcontainer-base/entrypoint.sh`

### 描述

重构现有用户设置和权限处理逻辑，新增运行时动态 UID/GID 映射功能：

1. 在 `setup_passwords()` 函数之前新增 `adjust_user_uid_gid()` 函数：
   - 读取 `LOCAL_USER_ID`、`LOCAL_GROUP_ID` 环境变量
   - 自动检测逻辑：如果环境变量未设置，检测 `/workspace` 目录属主 UID（非 root 且非 1000 时使用）
   - 目标 UID/GID 确定逻辑：env var > 自动检测 > 默认 1000
   - 如果目标 UID 与当前 devuser UID 不同：
     - 终止使用 devuser UID 的进程（如已启动）
     - 执行 `usermod -u <TARGET_UID> devuser`
     - 执行 `groupmod -g <TARGET_GID> devuser`
     - 调整容器内部文件（/home/devuser、/run/user、/tmp 等 devuser 拥有的文件，排除 /workspace 和挂载点）
   - 输出 FIXUID_DEBUG 详细日志（当 FIXUID_DEBUG=1）

2. 重构 `setup_workspace()` 函数：
   - 移除硬编码 WORKSPACE_CHOWN_MODE 默认值 "yes"，改为 "auto"
   - 整合现有 `_do_chown_dir()` 和 `_is_docker_named_volume()` 逻辑
   - 新增只读卷检测逻辑
   - 当 chown 被跳过时，清晰打印解决方案提示框（保留现有 `_print_permission_help()`）

3. 调整执行顺序：
   - diagnose_system（检查当前 UID 状态）
   - adjust_user_uid_gid（在 setup_passwords 之前调整 UID/GID）
   - setup_passwords（使用调整后的用户）
   - setup_workspace（使用正确的 UID 处理目录）

### Test Requirements

- **rule**: `bash -n entrypoint.sh` 语法检查通过
- **rule**: 不传任何环境变量时，devuser UID=1000，与现有行为一致
- **rule**: 传入 `LOCAL_USER_ID=501 LOCAL_GROUP_ID=20` 时，`id -u devuser` 输出 501，`id -g devuser` 输出 20
- **rule**: `/etc`、`/usr` 等系统目录永远不会被 chown
- **rubric**: FIXUID_DEBUG=1 时输出足够的诊断信息（UID 检测、决策过程、目录类型判断）
  - 0=无调试输出；1=部分信息；2=完整诊断（阈值≥2）

---

## Task 2: 更新 Dockerfile 添加环境变量声明和构建期准备

**优先级**: high  
**对应 AC**: AC2, AC5  
**修改文件**: `apps/docker-images/devcontainer-base/Dockerfile`

### 描述

1. 在 Stage 2.5 用户创建阶段，调整 devuser 创建逻辑，确保文件属主正确：
   - 构建期仍保持 UID=1000（运行时调整）
   - 确保 /home/devuser 下所有配置文件（.bashrc、.config、.jupyter、.ssh）在构建期属主正确

2. 在 ENV 层添加新环境变量默认值（元数据，不产生层）：
   ```
   LOCAL_USER_ID=
   LOCAL_GROUP_ID=
   WORKSPACE_CHOWN_MODE=auto
   CHOWN_EXTRA=
   FIXUID_DEBUG=0
   ```

3. 移除 Stage 2.6 中重复的 `chown -R devuser:devuser /workspace`（Line 650），因为：
   - 构建期 chown /workspace 没有意义（运行时会重新处理）
   - 如果 /workspace 是 volume，构建期 chown 会被覆盖

4. 确保 /etc/sudoers.d 配置正确，devuser 调整 UID 后 sudo 仍然有效

### Test Requirements

- **rule**: Dockerfile 语法检查通过（可正常 docker build）
- **rule**: 镜像构建成功，无错误
- **rule**: 构建后 /home/devuser 下所有文件属主为 devuser:devuser
- **rule**: 构建后镜像中 devuser UID=1000（构建期默认值）

---

## Task 3: 保留并增强权限辅助脚本（可选，如需拆分复杂逻辑）

**优先级**: medium  
**对应 AC**: AC1, AC4  
**修改文件**: `apps/docker-images/devcontainer-base/variants/shared/lib/permissions.sh`（如需要）

### 描述

检查现有 `permissions.sh` 中的函数是否需要更新以配合新的 UID 调整逻辑：

1. 如果逻辑较简单，直接放在 entrypoint.sh 中，不额外新增文件
2. 如果需要在变体构建中也使用 UID 调整能力，在 permissions.sh 中添加：
   - `ensure_user_uid_matches()` 构建期 UID 调整辅助函数
   - 保持现有 `ensure_conda_permissions()` 等函数不变

### Test Requirements

- **rule**: 如果修改 permissions.sh，bash 语法检查通过
- **rule**: 变体构建仍能正常 source 该文件

---

## Task 4: 本地构建验证 - 基础镜像

**优先级**: high  
**对应 AC**: AC1, AC2, AC5  
**依赖**: Task 1, Task 2

### 描述

在本地 WSL Docker 环境中构建并验证修复：

1. 构建基础镜像：
   ```bash
   cd apps/docker-images/devcontainer-base
   docker build -t devcontainer-base:uid-fix-test .
   ```

2. 测试场景 1 - 默认行为（无 env var）：
   ```bash
   docker run --rm --privileged devcontainer-base:uid-fix-test id
   # 验证 uid=1000(devuser)
   ```

3. 测试场景 2 - 指定 UID（模拟 macOS UID=501）：
   ```bash
   docker run --rm -e LOCAL_USER_ID=501 -e LOCAL_GROUP_ID=20 \
     -v /tmp/test-ws:/workspace --privileged devcontainer-base:uid-fix-test \
     su - devuser -c "id; touch /workspace/test.txt; ls -la /workspace/test.txt"
   # 验证 uid=501，文件创建成功
   ```

4. 测试场景 3 - DooD 模式（挂载 docker socket）：
   ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     -e LOCAL_USER_ID=$(id -u) devcontainer-base:uid-fix-test \
     su - devuser -c "docker ps"
   # 验证 docker 命令可执行
   ```

### Test Requirements

- **rule**: 镜像构建成功，无错误
- **rule**: 默认场景 devuser UID=1000
- **rule**: LOCAL_USER_ID 场景下 UID 正确调整，bind mount 目录可写
- **rule**: DooD 模式下 docker 命令可访问
- **rubric**: 启动时间 < 3 秒（不计算大目录 chown 时间）
  - 0=>5s；1=3-5s；2=<3s（阈值≥2）

---

## Task 5: 变体兼容性验证

**优先级**: high  
**对应 AC**: AC6  
**依赖**: Task 4

### 描述

验证一个代表性变体（如 conda-llvm 或 onnx-dev）构建正常：

1. 构建 conda-llvm 变体：
   ```bash
   cd apps/docker-images/devcontainer-base/variants
   bash build.sh --variant conda-llvm
   ```

2. 验证变体中 UID 调整功能正常工作

### Test Requirements

- **rule**: conda-llvm 变体构建成功
- **rule**: 变体容器中 LOCAL_USER_ID 功能正常
- **rubric**: 变体构建无新增警告，行为符合预期
  - 0=构建失败；1=有警告但可用；2=完全正常（阈值≥2）

---

## Task 6: 更新文档注释（可选）

**优先级**: low  
**对应 AC**: 所有  
**依赖**: Task 4

### 描述

更新 Dockerfile 头部注释和 entrypoint.sh 中的使用说明，添加：
- 新增环境变量文档
- 典型使用示例
- 常见问题排查（Permission denied 解决方案）

### Test Requirements

- **rule**: 注释准确反映实际功能
- **rule**: 无拼写错误

---

## Task 7: 独立审查（Review）

**优先级**: high  
**对应 AC**: 所有  
**依赖**: Task 1-6 完成

### 描述

执行独立代码审查：
1. 检查所有修改是否符合 spec.md 需求
2. 验证安全保护机制是否完整
3. 检查是否有遗漏的边缘情况
4. 验证向后兼容性
5. 测试一个之前的运行命令是否仍然正常工作

### Test Requirements

- **rule**: 每个 AC 都有对应的验证证据
- **rule**: 无安全漏洞引入
- **rule**: 向后兼容性保持
- **rubric**: 代码质量符合项目现有风格
  - 0=风格混乱；1=基本符合；2=风格一致、逻辑清晰（阈值≥2）

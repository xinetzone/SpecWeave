---
id: variant-framework-enhancement-tasks
title: "Variant Framework 增强任务分解"
---

# 任务分解

## 阶段一：新增模块实现（4个新模块）

### Task 1: 创建 user-management.sh（用户管理模块）
- [ ] 1.1 创建文件头注释（职责、依赖、环境变量、API列表）
- [ ] 1.2 实现内部辅助函数：_get_next_available_uid、_get_next_available_gid
- [ ] 1.3 实现 variant_create_user：创建用户，处理UID/GID冲突，加入docker/sudo组
- [ ] 1.4 实现 variant_rename_user：重命名用户、组、主目录
- [ ] 1.5 实现 variant_configure_sudo：写入/etc/sudoers.d/，设置0440权限
- [ ] 1.6 实现 variant_set_user_password：chpasswd设置密码，添加安全警告注释
- [ ] 1.7 实现 variant_lock_user_password：passwd -l锁定密码
- [ ] 1.8 实现 variant_get_target_user_info/group：输出最终用户信息
- [ ] 1.9 实现 variant_configure_target_user：一键配置主函数
- [ ] 1.10 bash -n 语法检查

### Task 2: 创建 shell-profile.sh（Shell环境配置模块）
- [ ] 2.1 创建文件头注释
- [ ] 2.2 定义幂等性标记常量（MARKER_START/MARKER_END）
- [ ] 2.3 实现 _idempotent_append：内部辅助函数，标记包裹追加（先删旧内容再追加）
- [ ] 2.4 实现 variant_configure_umask：写入4个位置（/etc/profile、bash.bashrc、user.bashrc、root.bashrc）
- [ ] 2.5 实现 variant_append_user_bashrc：用户bashrc幂等追加
- [ ] 2.6 实现 variant_append_root_bashrc：root bashrc幂等追加
- [ ] 2.7 实现 variant_persist_path：/etc/environment PATH幂等持久化
- [ ] 2.8 实现 variant_configure_ssh_env：配置~/.ssh/environment文件，设置600权限
- [ ] 2.9 实现 variant_configure_shell_profile：一键配置
- [ ] 2.10 bash -n 语法检查

### Task 3: 创建 jupyter-kernel.sh（Jupyter内核注册模块）
- [ ] 3.1 创建文件头注释
- [ ] 3.2 定义默认Jupyter路径列表
- [ ] 3.3 实现 _detect_jupyter_paths：检测存在的Jupyter数据路径
- [ ] 3.4 实现 _write_kernel_json：生成kernel.json内容（argv+env）
- [ ] 3.5 实现 variant_register_jupyter_kernel：遍历路径注册，设置权限
- [ ] 3.6 实现 verify_jupyter_kernel：验证内核文件存在
- [ ] 3.7 bash -n 语法检查

### Task 4: 创建 docs.sh（文档部署模块）
- [ ] 4.1 创建文件头注释
- [ ] 4.2 实现 variant_deploy_docs：COPY后调用，复制文件到/opt/docs，设置a+rX权限
- [ ] 4.3 bash -n 语法检查

## 阶段二：现有模块增强（2个增强 + 2个兼容修复）

### Task 5: 增强 install-helpers.sh
- [ ] 5.1 实现 variant_pip_build_mode：设置PIP_USER=0，输出日志
- [ ] 5.2 实现 variant_pip_runtime_mode：设置PIP_USER=1，输出日志
- [ ] 5.3 bash -n 语法检查

### Task 6: 增强 verify.sh
- [ ] 6.1 实现 verify_ssh_config：调用sshd -t验证配置语法
- [ ] 6.2 实现 verify_user_access <username>：通用用户验证（替代硬编码devuser）
- [ ] 6.3 保留 verify_devuser_access 作为 wrapper 调用 verify_user_access devuser
- [ ] 6.4 实现 verify_jupyter_kernel：内核文件存在性检查
- [ ] 6.5 bash -n 语法检查

### Task 7: 更新 permissions.sh（兼容自定义用户）
- [ ] 7.1 新增通用函数 ensure_user_bashrc <username>
- [ ] 7.2 保留 ensure_devuser_bashrc 作为 wrapper
- [ ] 7.3 更新 ensure_all_permissions 使用 DEVTARGET_USER 变量
- [ ] 7.4 bash -n 语法检查

### Task 8: 更新 mirror.sh（兼容自定义用户）
- [ ] 8.1 更新 _write_pip_conf 目标用户逻辑，使用 DEVTARGET_USER 变量（默认devuser）
- [ ] 8.2 保持对devuser的向后兼容
- [ ] 8.3 bash -n 语法检查

## 阶段三：框架集成与模板更新

### Task 9: 更新 variant-framework.sh
- [ ] 9.1 框架版本号从1.0.0升级到1.1.0
- [ ] 9.2 更新 _VARIANT_MODULES 数组，加入4个新模块（按正确顺序）
- [ ] 9.3 更新模块计数输出
- [ ] 9.4 bash -n 语法检查

### Task 10: 更新 _template/Dockerfile
- [ ] 10.1 在合适位置添加注释展示用户自定义可选用法（ARG + RUN variant_configure_target_user）
- [ ] 10.2 在合适位置添加注释展示Jupyter内核注册可选用法
- [ ] 10.3 在合适位置添加注释展示Shell环境配置可选用法
- [ ] 10.4 不修改现有模板的核心5阶段结构

## 阶段四：文档与验证

### Task 11: 创建 shared/README.md 共享库文档
- [ ] 11.1 框架概述与版本信息
- [ ] 11.2 模块列表表格（14个模块的职责）
- [ ] 11.3 每个模块的API函数说明（参数、返回值、示例）
- [ ] 11.4 环境变量配置表（DEVTARGET_USER等）
- [ ] 11.5 使用示例片段（自定义用户场景、自定义内核场景）
- [ ] 11.6 安全注意事项（密码设置警告）
- [ ] 11.7 向后兼容说明（旧函数wrapper列表）

### Task 12: 全面验证
- [ ] 12.1 所有新脚本和修改过的脚本通过 bash -n 语法检查
- [ ] 12.2 检查所有wrapper函数存在且正确转发
- [ ] 12.3 验证默认值：source框架后DEVTARGET_USER默认是devuser
- [ ] 12.4 验证不调用新函数时，现有行为完全不变
- [ ] 12.5 模拟检查：ai-dev变体使用的函数（verify_devuser_access、ensure_devuser_bashrc）仍然可用
- [ ] 12.6 检查幂等性：shell-profile追加函数的标记正确包裹

## 执行顺序依赖

```
Task 1-4（新模块）→ Task 5-8（增强现有模块）→ Task 9（框架集成）→ Task 10-11（模板+文档）→ Task 12（验证）
```

Task 1-4 之间无依赖，可并行实现。
Task 5-8 依赖 Task 1（user-management模块定义了DEVTARGET_USER约定）。

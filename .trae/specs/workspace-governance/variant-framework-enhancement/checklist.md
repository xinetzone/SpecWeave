---
id: variant-framework-enhancement-checklist
title: "Variant Framework 增强验收检查清单"
---

# 验收检查清单

## 一、文件存在性检查

- [ ] `shared/lib/user-management.sh` 已创建
- [ ] `shared/lib/shell-profile.sh` 已创建
- [ ] `shared/lib/jupyter-kernel.sh` 已创建
- [ ] `shared/lib/docs.sh` 已创建
- [ ] `shared/lib/install-helpers.sh` 已更新（新增2个函数）
- [ ] `shared/lib/verify.sh` 已更新（新增3个函数）
- [ ] `shared/lib/permissions.sh` 已更新（wrapper兼容）
- [ ] `shared/lib/mirror.sh` 已更新（DEVTARGET_USER支持）
- [ ] `shared/lib/variant-framework.sh` 已更新（模块列表、版本号）
- [ ] `_template/Dockerfile` 已更新（注释展示新功能）
- [ ] `shared/README.md` 已创建

## 二、语法检查

- [ ] `bash -n shared/lib/user-management.sh` 通过
- [ ] `bash -n shared/lib/shell-profile.sh` 通过
- [ ] `bash -n shared/lib/jupyter-kernel.sh` 通过
- [ ] `bash -n shared/lib/docs.sh` 通过
- [ ] `bash -n shared/lib/install-helpers.sh` 通过
- [ ] `bash -n shared/lib/verify.sh` 通过
- [ ] `bash -n shared/lib/permissions.sh` 通过
- [ ] `bash -n shared/lib/mirror.sh` 通过
- [ ] `bash -n shared/lib/variant-framework.sh` 通过
- [ ] 所有原有未修改模块（logging/timer/ft-guards/cleanup/build-info）语法仍然正常

## 三、API 函数存在性检查

### user-management.sh
- [ ] `variant_configure_target_user` 存在
- [ ] `variant_create_user` 存在
- [ ] `variant_rename_user` 存在
- [ ] `variant_configure_sudo` 存在
- [ ] `variant_set_user_password` 存在（带安全警告注释）
- [ ] `variant_lock_user_password` 存在
- [ ] `variant_get_target_user_info` 存在
- [ ] `variant_get_target_user_group` 存在

### shell-profile.sh
- [ ] `variant_configure_umask` 存在
- [ ] `variant_append_user_bashrc` 存在
- [ ] `variant_append_root_bashrc` 存在
- [ ] `variant_persist_path` 存在
- [ ] `variant_configure_ssh_env` 存在
- [ ] `variant_configure_shell_profile` 存在
- [ ] 幂等性标记定义存在

### jupyter-kernel.sh
- [ ] `variant_register_jupyter_kernel` 存在
- [ ] `verify_jupyter_kernel` 存在

### docs.sh
- [ ] `variant_deploy_docs` 存在

### install-helpers.sh 新增
- [ ] `variant_pip_build_mode` 存在
- [ ] `variant_pip_runtime_mode` 存在
- [ ] 原有函数（pip_install_group、conda_install_group、apt_install_group、variant_activate_*）保持不变

### verify.sh 新增与兼容
- [ ] `verify_ssh_config` 存在
- [ ] `verify_user_access` 存在（通用版本，接受username参数）
- [ ] `verify_jupyter_kernel` 存在
- [ ] `verify_devuser_access` 仍然存在（wrapper，调用verify_user_access devuser）
- [ ] 原有函数（verify_validation_header、verify_base_services、verify_conda_main_env、verify_bash_syntax、verify_all_basic）保持不变

### permissions.sh 兼容
- [ ] `ensure_user_bashrc` 存在（通用版本）
- [ ] `ensure_devuser_bashrc` 仍然存在（wrapper）
- [ ] `ensure_all_permissions` 使用DEVTARGET_USER变量

## 四、向后兼容验证

- [ ] 默认值检查：`source variant-framework.sh` 后，`echo $DEVTARGET_USER` 输出 `devuser`
- [ ] 默认值检查：`echo $DEVTARGET_UID` 输出 `1000`
- [ ] 默认值检查：`echo $DEVTARGET_GID` 输出 `1000`
- [ ] 现有wrapper函数行为不变：`verify_devuser_access` 仍然检查devuser
- [ ] 现有wrapper函数行为不变：`ensure_devuser_bashrc` 仍然操作/home/devuser/.bashrc
- [ ] 不自动调用任何新函数：source框架后不执行用户创建/umask修改/内核注册等操作
- [ ] _template/Dockerfile默认构建行为不变（注释的示例代码不影响构建）

## 五、安全检查

- [ ] `variant_set_user_password` 函数注释包含明确安全警告（密码进入镜像层历史）
- [ ] README.md中密码安全警告可见
- [ ] 提供了`variant_lock_user_password`作为更安全的替代
- [ ] sudoers文件权限设置为0440
- [ ] SSH environment文件权限设置为600
- [ ] 内核json文件权限设置为644

## 六、代码质量检查

- [ ] 所有函数有注释说明用途、参数
- [ ] 使用 `variant_log_info/variant_log_ok/variant_log_error` 进行日志输出（不直接echo关键信息）
- [ ] 框线头格式与现有代码一致（┌─┐ 格式）
- [ ] 错误处理：关键操作有返回码检查
- [ ] 幂等性：shell-profile追加函数使用标记包裹
- [ ] 防御性编程：目录不存在时自动创建，文件不存在时优雅处理
- [ ] 不修改全局shell选项（set +e后恢复）

## 七、框架集成检查

- [ ] variant-framework.sh版本号为1.1.0
- [ ] 模块加载顺序正确：logging → timer → user-management → mirror → shell-profile → install-helpers → jupyter-kernel → docs → ft-guards → cleanup → build-info → verify → permissions
- [ ] 模块数量：_VARIANT_MODULE_COUNT 为13（原10 + 新4 - 0删除？实际14个模块：原10个+新4个=14？核对）
- [ ] source variant-framework.sh输出正确版本和模块数量（VARIANT_DEBUG=1时）
- [ ] 所有模块文件存在且可source

## 八、文档检查

- [ ] shared/README.md 包含模块列表
- [ ] shared/README.md 包含每个模块的API说明
- [ ] shared/README.md 包含使用示例
- [ ] shared/README.md 包含环境变量表
- [ ] shared/README.md 包含向后兼容说明
- [ ] shared/README.md 包含安全注意事项

## 九、模板更新检查

- [ ] _template/Dockerfile 包含用户自定义的注释示例
- [ ] _template/Dockerfile 包含Jupyter内核注册的注释示例
- [ ] _template/Dockerfile 现有5阶段结构未被破坏
- [ ] _template/Dockerfile 注释示例不会被执行（被#注释）

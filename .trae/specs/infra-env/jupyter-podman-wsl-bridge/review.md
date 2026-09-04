# jupyter-podman-rootless WSL 桥接转换 - 验证检查清单

## 问题解答验证
- [x] CP-1: 明确回答"不能直接使用 wsl -d"，答案在显眼位置
- [x] CP-2: 解释 OCI 分层镜像 vs flat rootfs 的区别，通俗易懂
- [x] CP-3: 说明直接导入的后果（.wh.* 文件、权限问题、启动失败）
- [x] CP-4: 明确指出 seven-concepts-cmd 是 AI Skill 不是镜像文件
- [x] CP-5: 给出正确的解决方案方向（使用 docker-wsl-bridge-cmd 转换）

## 手动转换指南验证
- [x] CP-6: PowerShell 脚本路径正确（镜像 tar.gz 路径、安装目录等）
- [x] CP-7: 使用 rootful podman（sudo podman），避免 rootless UID 映射问题
- [x] CP-8: Windows → WSL 路径转换正确（D:\ → /mnt/d/，反斜杠→正斜杠）
- [x] CP-9: 包含 wsl.conf 配置（default=devuser, systemd=false）
- [x] CP-10: 包含 conda 全局激活配置（/etc/profile.d/conda.sh）
- [x] CP-11: 包含 wsl --terminate 步骤使配置生效
- [x] CP-12: 包含完整的 Smoke Test 验证步骤
- [x] CP-13: 脚本中包含错误处理提示（镜像名<none>的处理等）

## CLI 增强验证（已实现）
- [x] CP-14: wsl-export 和 wsl-verify 命令在 bin/jpman 的 help 中可见
- [x] CP-15: wsl-export 有幂等检查（同名发行版已存在时提示 unregister）
- [x] CP-16: wsl.conf 配置 default=devuser（非 root）
- [x] CP-17: wsl-verify 检查 `whoami` 输出 devuser
- [x] CP-18: wsl-verify 检查 Python 版本显示 Python 3.14
- [x] CP-19: wsl-verify 检查 conda --version
- [x] CP-20: wsl-verify 检查 jupyter lab --version
- [x] CP-21: wsl-verify 检查 /mnt/c 和 /mnt/d 挂载（best-effort）
- [x] CP-22: wsl-verify 检查文件系统可写（touch/rm in /tmp）
- [x] CP-23: wsl-verify 命令存在且能正确报告各项状态（14项检查，彩色输出）
- [x] CP-24: 现有命令（start/stop/save/load/rebuild/keepalive/install 等）功能不受影响
- [x] CP-25: bash -n 语法检查通过
- [x] CP-26: 脚本命名为 jpman（不与 Python jupyter CLI 冲突）
- [x] CP-27: .wsl-cache/ 已加入 .gitignore
- [x] CP-28: Windows wrapper 更新为 jpman.cmd
- [x] CP-29: cmd_install 安装 symlink 到 ~/.local/bin/jpman
- [x] CP-30: 端到端实际运行测试 ✅ 2026-08-27 通过
  - pwsh 原生 wsl-export: 5步流程全部完成（load→export→import→config→restart）
  - pwsh 原生 wsl-verify: 15项 Smoke Test 全部 PASS（0 failed）
  - 验证环境: WSL 2.9.3.0 / Kernel 6.18.35.2 / Podman 5.7.0 / Python 3.14.7 cp314t / JupyterLab 4.6.3
  - 修复的 bug: wslpath 反斜杠吞字、PowerShell EAP/exit code、here-string 子表达式、数组标量化、conda env（main非base）、LoginShell bash非sh、regex::Escape 参数绑定

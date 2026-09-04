# devcontainer-win11 - Acceptance Checklist

## 功能完整性

- [ ] AC-1: 应用目录结构创建完成
- [ ] AC-2: Dockerfile 可成功构建
- [ ] AC-3: SSH 服务可用
- [ ] AC-4: JupyterLab 服务可用
- [ ] AC-5: Python/Miniforge free-threading 环境可用（Python 3.14 cp314t + conda，Py_GIL_DISABLED==1）
- [ ] AC-6: Docker CLI (DooD) 可用
- [ ] AC-7: 中文环境和时区配置正确
- [ ] AC-8: 非管理员用户权限正确（devuser）
- [ ] AC-9: 健康检查正常工作
- [ ] AC-10: 构建日志包含 [TIMER] 和 [VALIDATION CHECKPOINT]
- [ ] AC-11: AGENTS.md 和规范文件完整
- [ ] AC-12: Dockerfile 代码质量 ≥ 4/5
- [ ] AC-13: 开发者体验一致性 ≥ 4/5
- [ ] AC-14: Free-threading 运行时验证（sys._is_gil_enabled()==False，Py_GIL_DISABLED=1）
- [ ] AC-15: pip 源码编译 free-threading 扩展能力（C 编译器可用）

## 任务完成状态

- [ ] Task 1: 创建应用目录结构和 AGENTS.md 入口
- [ ] Task 2: 编写 Dockerfile（Stage 1-3：基础镜像 + 系统配置 + SSH）
- [ ] Task 3: 编写 Dockerfile（Stage 4-5：Miniforge3 + Python free-threading + Jupyter + 编译工具链）
- [ ] Task 4: 编写 Dockerfile（Stage 6-7：用户配置 + 元数据 + 验证）
- [ ] Task 5: 编写 entrypoint.ps1 启动脚本
- [ ] Task 6: 编写配置文件
- [ ] Task 7: 编写构建脚本和启动脚本
- [ ] Task 8: 编写 .agents/rules/ 规范文件
- [ ] Task 9: 构建验证和测试
- [ ] Task 10: 更新 apps/AGENTS.md 和 README 文档
- [ ] Task 11: 更新 apps/docker-images 分组 README

## 非功能要求验证

- [ ] NFR-1: 镜像压缩后体积 ≤ 6GB
- [ ] NFR-2: Dockerfile 遵循分层缓存原则
- [ ] NFR-3: 构建脚本支持国内镜像源参数
- [ ] NFR-4: 所有 PowerShell 脚本设置严格模式和错误处理
- [ ] NFR-5: 所有文件使用 UTF-8 编码
- [ ] NFR-6: 健康检查配置与 Linux 版一致（30s/10s/60s）
- [ ] NFR-7: 遵循 SpecWeave 开发规范

## 范围确认（Non-Goals 检查）

- [ ] 未实现 Docker-in-Docker (DinD)
- [ ] 未包含 Podman
- [ ] ✅ 使用 Python 3.14 free-threading (cp314t) 作为默认 Python（通过 conda-forge python-freethreading 元包）
- [ ] 未实现双 Python 环境（GIL + free-threading 切换），v1.0 直接默认 free-threading
- [ ] 使用 PowerShell 原生服务管理（非 supervisord）
- [ ] 未使用 tini init
- [ ] 未包含 GPU 直通/CUDA
- [ ] v1.0 不包含 variants/ 变体系统
- [ ] 已设置 Py_GIL_DISABLED=1 系统环境变量，支持 pip 源码编译 C 扩展

# Tasks

- [x] Task 1: 环境与镜像确认：确认 Docker 可用、`xmnn-whl-builder:latest` 镜像存在、端口 8891 空闲
- [x] Task 2: 清理旧容器：删除 Exited 的 `xmnn-whl-builder-jupyter` 容器
- [x] Task 3: 启动 Jupyter 服务：以 chaos bind mount + 8891 端口 + Jupyter 命令启动容器
- [x] Task 4: 健康验证：容器状态 Up、端口可访问、`/api/kernelspecs` 可见 xmnn-conda、`/workspace` 挂载正确

# Task Dependencies
- [Task 3] depends on [Task 1] 和 [Task 2]
- [Task 4] depends on [Task 3]

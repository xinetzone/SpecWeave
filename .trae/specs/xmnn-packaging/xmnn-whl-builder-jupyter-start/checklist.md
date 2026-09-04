# Checklist

- [x] 容器 `xmnn-whl-builder-jupyter` 运行状态为 Up
- [x] `/workspace` 正确 bind mount 到 chaos 目录（容器内可见 ai/models 等）
- [x] 宿主 `127.0.0.1:8891` 可访问 Jupyter（HTTP 200/302）
- [x] `/api/kernelspecs` 可见 `xmnn-conda` kernel
- [x] WSL2 会话保持存活，容器不被回收

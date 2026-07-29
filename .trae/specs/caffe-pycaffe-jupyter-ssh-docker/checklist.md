---
version: "1.0"
---

# PyCaffe Jupyter SSH Docker - Verification Checklist

- [x] Checkpoint 1: 新目录 `pycaffe-jupyter-ssh/` 已创建，包含完整子目录结构（config/supervisor/conf.d/, scripts/）
- [x] Checkpoint 2: config/sshd_config 文件存在，ED25519 密钥优先、PermitRootLogin no、密码认证启用等安全配置正确
- [x] Checkpoint 3: config/supervisord.conf 文件存在，nodaemon 模式、include conf.d 配置正确
- [x] Checkpoint 4: config/jupyter_notebook_config.py 文件存在，监听 0.0.0.0:8888、root_dir=/workspace、用户路径适配为 /home/builder
- [x] Checkpoint 5: config/supervisor/conf.d/sshd.conf 文件存在，sshd 进程配置正确（autorestart、priority=100）
- [x] Checkpoint 6: config/supervisor/conf.d/jupyter.conf 文件存在，jupyter 进程以 builder 用户运行、目录 /workspace、环境变量正确（无 venv 路径）
- [x] Checkpoint 7: entrypoint.sh 文件存在且 bash 语法正确（`bash -n` 检查通过，WSL 验证）
- [x] Checkpoint 8: entrypoint.sh 使用 builder 作为默认 NON_ROOT_USER，HOME=/home/builder，系统 Python 路径正确
- [x] Checkpoint 9: entrypoint.sh 包含所有核心功能：密码设置、SSH host key 生成、sshd 配置、公钥注入、Jupyter 动态配置、命令模式支持、supervisord 启动
- [x] Checkpoint 10: scripts/healthcheck.sh 文件存在且 bash 语法正确，同时检测 sshd 进程/端口和 jupyter 进程/HTTP 响应
- [x] Checkpoint 11: Dockerfile 存在，多阶段构建结构完整（base-system → base-builder → pycaffe-builder → runtime with SSH/Jupyter）
- [x] Checkpoint 12: Dockerfile 中 COPY 路径相对于 vendor/ 构建上下文正确，能访问 caffe-slim、tvm-ffi 和自身 config/scripts/entrypoint
- [x] Checkpoint 13: Dockerfile 安装了必要的运行时包：openssh-server, supervisor, tini, pwgen, locales, curl, procps
- [x] Checkpoint 14: Dockerfile 安装了 Jupyter Python 包（notebook, jupyterlab, ipykernel, nbconvert, jupyter_server）到系统 Python（使用 --break-system-packages）
- [x] Checkpoint 15: Dockerfile 配置了中文环境：zh_CN.UTF-8 locale 生成、Asia/Shanghai 时区设置
- [x] Checkpoint 16: Dockerfile 中 builder 用户配置正确（UID 1000, HOME=/home/builder, .jupyter 和 .ssh 目录权限正确）
- [x] Checkpoint 17: Dockerfile 中 ENTRYPOINT 使用 tini，CMD 为空，EXPOSE 22 8888，WORKDIR /workspace，VOLUME ["/workspace"]
- [x] Checkpoint 18: Dockerfile 包含构建时验证步骤（sshd -t, supervisord --version, jupyter --version, pycaffe import）
- [x] Checkpoint 19: Dockerfile HEALTHCHECK 配置正确，调用 healthcheck.sh
- [x] Checkpoint 20: Dockerfile 复制了 pycaffe 的验证脚本（verify-pycaffe.sh, verify-parity.sh）并设置可执行权限
- [x] Checkpoint 21: README.md 文件存在，包含项目简介、特性列表、目录结构、构建命令、运行示例、SSH/Jupyter 访问方式、环境变量表、服务管理、验证步骤
- [x] Checkpoint 22: README 中构建命令正确（cd vendor && docker build -f caffe/docker/standalone/pycaffe-jupyter-ssh/Dockerfile .）
- [x] Checkpoint 23: README 中运行示例包含端口映射（22:2222, 8888:8888）和必要的环境变量（USER_PASSWORD, JUPYTER_TOKEN）
- [ ] Checkpoint 24: 构建的镜像中 pycaffe 可成功导入并输出版本号（需 Docker 环境验证）
- [ ] Checkpoint 25: 容器启动后 sshd 服务在 22 端口正常监听，可使用密码登录（需 Docker 环境验证）
- [ ] Checkpoint 26: 容器启动后 Jupyter 在 8888 端口正常响应 HTTP 请求（需 Docker 环境验证）
- [ ] Checkpoint 27: supervisorctl status 显示 sshd 和 jupyter 均为 RUNNING 状态（需 Docker 环境验证）
- [ ] Checkpoint 28: 容器内 healthcheck.sh 执行返回 STATUS: HEALTHY（需 Docker 环境验证）
- [ ] Checkpoint 29: 使用 USER_PASSWORD 和 JUPYTER_TOKEN 环境变量可正常认证（需 Docker 环境验证）
- [ ] Checkpoint 30: 中文环境配置正确（LANG=zh_CN.UTF-8, TZ=Asia/Shanghai）（需 Docker 环境验证）
- [ ] Checkpoint 31: 调试模式（docker run ... bash）正确进入 shell 而非启动 supervisord（需 Docker 环境验证）
- [ ] Checkpoint 32: Jupyter Notebook 中可成功 import pycaffe, numpy, scipy, matplotlib（需 Docker 环境验证）
- [x] Checkpoint 33: 未修改现有 pycaffe/ 目录或 apps/jupyter-ssh-base/ 目录中的任何文件
- [x] Checkpoint 34: 所有新增文件路径位于 projects/xuanspace/vendor/caffe/docker/standalone/pycaffe-jupyter-ssh/ 下

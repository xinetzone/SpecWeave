# 验证清单

- [x] CP-1: docker-compose.yml 中 dev 服务 environment 段包含 `PIP_USER=1`
- [x] CP-2: container-bootstrap.sh 中 pip install 命令使用 `PIP_USER=0` 前缀
- [x] CP-3: 容器重启后 `PIP_USER=1` 环境变量在 devuser 会话中生效
- [x] CP-4: devuser 执行 `pip install --dry-run <pkg>` 路径指向 `/home/devuser/.local/`
- [x] CP-5: root 执行 `PIP_USER=0 pip install --dry-run <pkg>` 路径指向 `/opt/conda/`
- [x] CP-6: devuser 执行 `sudo pip install --dry-run <pkg>` 路径指向 `/opt/conda/`
- [x] CP-7: bootstrap 已安装的包（pandas/cv2/toml 等）可在 /opt/conda 中找到且 devuser 可 import
- [x] CP-8: TVM/VTA Python 导入正常（tvm 0.19.0 + vta）
- [x] CP-9: caffe_demo 模型编译成功
- [x] CP-10: Dockerfile 未被修改（构建阶段不受影响）

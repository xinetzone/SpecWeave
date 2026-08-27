---
id: "jupyter-faq"
title: "常见问题"
source: "README.md#常见问题"
---
# 常见问题

## 构建问题

### Q: 构建时下载 Miniforge 很慢？

使用国内镜像源构建：
```bash
invoke build --conda-mirror tuna --apt-mirror tuna --pip-mirror tuna
```

支持的镜像源：
- `official`：官方源（默认）
- `tuna`：清华大学镜像源（推荐国内用户）
- `aliyun`：阿里云镜像源

### Q: 构建时conda solve很慢？

这是正常现象，conda依赖解析（特别是libmamba首次solve）需要时间。建议：
- 使用`--conda-mirror tuna`使用国内源加速下载
- 构建完成后镜像已缓存，后续构建会很快
- 避免频繁`--no-cache`，充分利用层缓存

### Q: 如何构建标准Python版本（非free-threading）？

```bash
podman build -t jupyter-podman-rootless:cp314 \
  --build-arg PYTHON_BUILD=cp314 \
  --build-arg APT_MIRROR=tuna \
  .
```
注意：可能需要修改Containerfile中的conda包匹配规则。

## 运行问题

### Q: Podman 报错 "fuse: device not found"？

运行容器时必须添加 `--device /dev/fuse` 参数：
```bash
podman run -d \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  -p 2222:22 -p 8888:8888 \
  jupyter-podman-rootless
```

invoke的`run`命令已自动添加此参数，无需手动添加。

### Q: WSL2 下挂载路径不对？

invoke的`utils.to_posix_path()`会自动将Windows路径转换为WSL2路径：
- `D:\project` → `/mnt/d/project`
- `C:\Users\xxx` → `/mnt/c/Users/xxx`

直接使用podman命令时需手动转换路径。

### Q: 容器启动后无法通过SSH连接？

排查步骤：
1. 检查容器是否在运行：`podman ps`
2. 检查端口映射：`podman port jupyter-podman`
3. 查看启动日志获取密码：`podman logs jupyter-podman | grep -A2 -B2 "SSH:"`
4. 确认使用正确的端口（默认2222）：`ssh -p 2222 devuser@localhost`
5. 检查防火墙设置

### Q: 忘记密码/token怎么办？

1. 密码和token在启动时会打印到日志，查看日志：
   ```bash
   podman logs jupyter-podman | grep -E "(SSH:|Jupyter|password|token)"
   ```
2. 如果日志已被清，可重启容器重新生成密码：
   ```bash
   invoke stop
   invoke run
   ```
3. 或在启动时设置固定密码：
   ```bash
   invoke run --user-password yourpassword --jupyter-token yourtoken
   ```

## 权限问题

### Q: 如何在容器中使用 sudo？

启动时添加 `--grant-sudo` 参数：
```bash
invoke run --grant-sudo
```

进入容器后即可无密码使用sudo：
```bash
sudo apt update
sudo apt install some-package
```

### Q: 如何设置 SSH 公钥登录？

```bash
invoke run --ssh-public-key "$(cat ~/.ssh/id_ed25519.pub)"
```

启动后即可使用SSH密钥登录，无需输入密码：
```bash
ssh -p 2222 devuser@localhost
```

### Q: 如何允许root SSH登录？

不推荐，但如果需要：
```bash
invoke run --grant-sudo -e ALLOW_ROOT_SSH=yes
```
root密码会随机生成（查看日志获取）或通过`ROOT_PASSWORD`设置。

## Podman/DinP问题

### Q: 容器内的 Podman 无法拉取镜像？

确保运行容器时添加了以下参数（invoke run已自动添加）：
1. `--device /dev/fuse`
2. `--security-opt label=disable`
3. `--cgroupns=host`

验证：
```bash
# 进入容器
invoke shell

# 检查Podman
podman info
podman run --rm hello-world
```

### Q: rootless Podman需要特权模式吗？

不需要。只需要`--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host`三个参数即可，不需要`--privileged`。

## 透传/开发模式问题

### Q: 如何使用开发透传模式（SSH agent/GUI）？

使用`compose.dev.yaml`覆盖文件：
```bash
podman-compose -f compose.yaml -f compose.dev.yaml up -d
```

透传功能包括：SSH agent、git配置、SSH密钥、X11 GUI、pip缓存。

### Q: compose.dev.yaml 中的透传安全吗？

所有透传均为 opt-in（默认不启用）。安全设计：
- SSH keys和gitconfig以只读方式挂载
- /run/host逃生口默认关闭
- 不挂载GPG密钥、credential store等高敏感资源

### Q: X11 GUI应用无法显示？

1. 确保主机运行X server（Linux桌面环境、Windows上的VcXsrv、Mac上的XQuartz）
2. 确保使用compose.dev.yaml启动：
   ```bash
   podman-compose -f compose.yaml -f compose.dev.yaml up -d
   ```
3. 测试xclock：
   ```bash
   podman-compose exec jupyter xclock
   ```
4. Windows上可能需要设置DISPLAY环境变量并配置VcXsrv访问权限。

## ML模型问题

### Q: 如何启动本地模型仓库？

```bash
podman-compose --profile registry up -d
```

验证：
```bash
curl http://localhost:5000/v2/_catalog
```

然后使用`localhost:5000`作为OMLMD/OLOT的registry地址。

### Q: model.push/pack 报错 omlmd/olot 未安装？

omlmd和olot已预装在容器镜像内。错误原因通常是：
1. 容器未运行（需要先`invoke run`）
2. 尝试在宿主机直接执行ML命令（宿主机未安装）

宿主机安装：
```bash
pip install omlmd 'olot[oras-py]'
# 或
pip install -e ".[model]"
```

### Q: 推送到本地registry报错HTTPS？

本地registry使用HTTP（非HTTPS），需要配置：
- 容器内已默认配置`REGISTRY_PLAIN_HTTP=true`
- 如果使用podman直接推送，可能需要配置registries.conf允许insecure：
  ```bash
  echo '[[registry]]
  location = "localhost:5000"
  insecure = true' | sudo tee /etc/containers/registries.conf.d/localhost.conf
  ```

## Python/Free-Threading问题

### Q: 某些Python库导入错误或崩溃？

这可能是free-threading（cp314t）兼容性问题：
1. 先确认是否是free-threading导致：
   ```bash
   python -c "import sys; print(sys.version)"
   # 应显示 "free-threaded"
   ```
2. 尝试构建标准GIL版本Python（cp314）
3. 或等待上游库适配free-threading

### Q: Jupyter某些扩展不工作？

部分Jupyter扩展可能未适配free-threading或Python 3.14：
1. 检查扩展是否支持Python 3.14
2. 检查扩展是否支持free-threading
3. 如必须使用，建议切换到cp314构建

## Toolbx问题

### Q: toolbox create 报错？

确保：
1. 镜像已构建：`invoke build`
2. 使用正确的镜像名：`jupyter-podman-rootless:latest`
3. Toolbx版本支持自定义镜像（Toolbx ≥0.0.99）

```bash
toolbox create -i localhost/jupyter-podman-rootless:latest -c jupyter-dev
```

### Q: toolbox enter 后找不到conda/python？

Toolbx可能未正确初始化PATH。手动source conda：
```bash
source /opt/conda/etc/profile.d/conda.sh
conda activate base
```

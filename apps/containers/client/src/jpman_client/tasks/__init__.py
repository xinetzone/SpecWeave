"""jupyter-podman-client invoke 任务入口。

根命名空间（7 个镜像消费端命令）：
  invoke load       从本地 tar 加载镜像
  invoke images     列出本地镜像
  invoke save       导出镜像到缓存目录（备份）
  invoke run        启动容器
  invoke stop       停止并删除容器
  invoke status     查看容器状态
  invoke clean      清理资源

container.* 别名命名空间：
  invoke container.load / container.images / container.save / container.run ...

env.* 自举环境命名空间（3 个命令）：
  invoke env.build-layer   基于 Containerfile.client 构建叠加镜像
  invoke env.run-cmd       在自举容器内执行单条命令
  invoke env.shell         启动交互式 bash shell（可直接 inv 命令）

quant.* 工作负载栈命名空间（6 个命令，opt-in，podman-compose 子进程）：
  invoke quant.build / up / down / ps / logs / smoke
  驱动 overlays/onnx-quantized 量化叠加栈；Windows 原生门禁，详见 quant.py
"""
from invoke import Collection

from . import env_in_container, manage, quant

ns = Collection()

# ---- 根命名空间（镜像消费端 7 命令） ----
ns.add_task(manage.load)
ns.add_task(manage.images)
ns.add_task(manage.save)
ns.add_task(manage.run)
ns.add_task(manage.stop)
ns.add_task(manage.status)
ns.add_task(manage.clean)

# ---- container.* 别名命名空间 ----
container_ns = Collection("container")
container_ns.add_task(manage.load, "load")
container_ns.add_task(manage.images, "images")
container_ns.add_task(manage.save, "save")
container_ns.add_task(manage.run, "run")
container_ns.add_task(manage.stop, "stop")
container_ns.add_task(manage.status, "status")
container_ns.add_task(manage.clean, "clean")
ns.add_collection(container_ns)

# ---- env.* 自举环境命名空间 ----
env_ns = Collection("env")
env_ns.add_task(env_in_container.build_layer, "build-layer")
env_ns.add_task(env_in_container.run_cmd_, "run-cmd")
env_ns.add_task(env_in_container.shell, "shell")
ns.add_collection(env_ns)

# ---- quant.* ONNX 量化工作负载栈命名空间（podman-compose，opt-in） ----
quant_ns = Collection("quant")
quant_ns.add_task(quant.build, "build")
quant_ns.add_task(quant.up, "up")
quant_ns.add_task(quant.down, "down")
quant_ns.add_task(quant.ps, "ps")
quant_ns.add_task(quant.logs, "logs")
quant_ns.add_task(quant.smoke, "smoke")
ns.add_collection(quant_ns)

# configure 全局默认（与 ContainerConfig 对齐）
ns.configure(
    {
        "container": {
            "image_tag": "localhost/jupyter-podman-client:latest",
            "container_name": "jupyter-podman",
            "ssh_port": 2222,
            "jupyter_port": 8888,
            "workspace": "./workspace",
        },
        "env": {
            "client_image": "localhost/jupyter-podman-client:latest",
            "client_container": "jpman-client-env",
        },
        "quant": {
            "image_tag": "localhost/onnx-quantized:latest",
            "base_image": "localhost/jupyter-podman-rootless:latest",
            "container_name": "onnx-quantized",
            "ssh_port": 2222,
            "jupyter_port": 8888,
        },
    }
)


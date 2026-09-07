"""jupyter-podman-client invoke 任务入口。

根命名空间（6 个镜像消费端命令）：
  invoke load       从本地 tar 加载镜像
  invoke images     列出本地镜像
  invoke run        启动容器
  invoke stop       停止并删除容器
  invoke status     查看容器状态
  invoke clean      清理资源

container.* 别名命名空间：
  invoke container.load / container.images / container.run ...

env.* 自举环境命名空间（3 个命令）：
  invoke env.build-layer   基于 Containerfile.client 构建叠加镜像
  invoke env.run-cmd       在自举容器内执行单条命令
  invoke env.shell         启动交互式 bash shell（可直接 inv 命令）
"""
from invoke import Collection

from . import env_in_container, manage

ns = Collection()

# ---- 根命名空间（镜像消费端 6 命令） ----
ns.add_task(manage.load)
ns.add_task(manage.images)
ns.add_task(manage.run)
ns.add_task(manage.stop)
ns.add_task(manage.status)
ns.add_task(manage.clean)

# ---- container.* 别名命名空间 ----
container_ns = Collection("container")
container_ns.add_task(manage.load, "load")
container_ns.add_task(manage.images, "images")
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
    }
)


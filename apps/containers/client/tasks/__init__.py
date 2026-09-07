"""jupyter-podman-client invoke 任务入口。

根命名空间：
  invoke load       从本地 tar 加载镜像
  invoke images     列出本地镜像
  invoke run        启动容器
  invoke stop       停止并删除容器
  invoke status     查看容器状态
  invoke clean      清理资源

container.* 别名命名空间：
  invoke container.load / container.images / container.run ...
"""
from invoke import Collection

from . import manage

ns = Collection()

# 根命名空间直接注册（与用户习惯一致：invoke run / invoke stop）
ns.add_task(manage.load)
ns.add_task(manage.images)
ns.add_task(manage.run)
ns.add_task(manage.stop)
ns.add_task(manage.status)
ns.add_task(manage.clean)

# container.* 别名命名空间（便于脚本统一前缀调用）
container_ns = Collection("container")
container_ns.add_task(manage.load, "load")
container_ns.add_task(manage.images, "images")
container_ns.add_task(manage.run, "run")
container_ns.add_task(manage.stop, "stop")
container_ns.add_task(manage.status, "status")
container_ns.add_task(manage.clean, "clean")
ns.add_collection(container_ns)

# configure 全局默认（与 ContainerConfig 对齐）
ns.configure(
    {
        "container": {
            "image_tag": "localhost/jupyter-podman-rootless:latest",
            "container_name": "jupyter-podman",
            "ssh_port": 2222,
            "jupyter_port": 8888,
            "workspace": "./workspace",
        }
    }
)

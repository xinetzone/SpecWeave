"""Jupyter Podman Rootless 容器管理任务入口。

常用命令：
    invoke build      - 构建镜像
    invoke run        - 启动容器
    invoke stop       - 停止并删除容器
    invoke clean      - 清理资源
    invoke status     - 查看容器状态
    invoke shell      - 进入容器Shell
    invoke logs       - 查看容器日志
    invoke exec       - 在容器中执行命令
    invoke container.* - 容器管理子命令集合
    invoke model.push  - 推送ML模型到OCI registry（OMLMD）
    invoke model.pull  - 从OCI registry拉取ML模型
    invoke model.config - 查看模型元数据配置
"""
from invoke import Collection

from . import container, model

ns = Collection()

# 核心容器任务提升到根命名空间
ns.add_task(container.build, default=True)
ns.add_task(container.run)
ns.add_task(container.stop)
ns.add_task(container.clean)
ns.add_task(container.status)
ns.add_task(container.shell)
ns.add_task(container.logs)
ns.add_task(container.exec_task)

# 添加container子集合
ns.add_collection(Collection.from_module(container), name="container")

# 添加model子集合（OMLMD模型管理，不提升到根命名空间）
ns.add_collection(Collection.from_module(model), name="model")

# 默认配置
ns.configure(
    {
        "container": {
            "image_tag": "jupyter-podman-rootless:latest",
            "container_name": "jupyter-podman",
            "ssh_port": 2222,
            "jupyter_port": 8888,
            "workspace": "./workspace",
            "apt_mirror": "official",
            "conda_mirror": "official",
            "pip_mirror": "official",
        },
        "model": {
            "registry_url": "localhost:5000",
        },
    }
)

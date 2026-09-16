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

xmnn.* 开发/打包栈命名空间（8 个命令，opt-in，podman-compose 子进程）：
  invoke xmnn.build / up / down / ps / logs / smoke / build-tvm / wheel
  驱动 overlays/xmnn-dev 开发打包栈（运行时挂载 npu_tvm/npuusertools 源码，
  LLVM 22 + Nuitka 4.1.3 工具链）；Windows 原生门禁，详见 xmnn.py

xmnnrt.* wheel 消费运行时栈命名空间（7 个命令，opt-in）：
  invoke xmnnrt.build / up / down / ps / logs / smoke / pack
  驱动 overlays/xmnn-runtime 干净运行时镜像（安装预构建 whl，无源码挂载、
  无编译工具链；build/up 自动从 workspace/dist 暂存最新 whl）；pack 产出
  完全独立的客户离线交付包到 overlays/xmnn-runtime/release/；详见 xmnnrt.py
"""
from invoke import Collection

from . import env_in_container, manage, monetize, quant, xmnn, xmnnrt

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
# 六任务消费 overlay_core.make_stack_tasks 工厂产物
quant_ns = Collection("quant")
for _name, _task in quant.TASKS.items():
    quant_ns.add_task(_task, _name)
ns.add_collection(quant_ns)

# ---- xmnn.* XMNN 开发/打包栈命名空间（podman-compose，opt-in） ----
xmnn_ns = Collection("xmnn")
for _name, _task in xmnn.TASKS.items():
    xmnn_ns.add_task(_task, _name)
xmnn_ns.add_task(xmnn.build_tvm, "build-tvm")
xmnn_ns.add_task(xmnn.wheel, "wheel")
ns.add_collection(xmnn_ns)

# ---- monetize.* agent-monetize 开发/tvm-ffi 原生编译打包栈（podman-compose，opt-in） ----
monetize_ns = Collection("monetize")
for _name, _task in monetize.TASKS.items():
    monetize_ns.add_task(_task, _name)
monetize_ns.add_task(monetize.build_native, "build-native")
monetize_ns.add_task(monetize.wheel, "wheel")
ns.add_collection(monetize_ns)

# ---- xmnnrt.* XMNN wheel 消费运行时栈命名空间（podman-compose，opt-in） ----
# 六任务均为 xmnnrt 模块产物（build/up 为 whl 暂存薄封装，其余四任务走工厂）
xmnnrt_ns = Collection("xmnnrt")
for _name, _task in xmnnrt.TASKS.items():
    xmnnrt_ns.add_task(_task, _name)
ns.add_collection(xmnnrt_ns)

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
        # 注：quant/xmnn/monetize 三栈的镜像/端口/容器名等配置在 2026-09-15
        # 声明式重构后唯一事实源是各栈模块的 StackSpec（经任务闭包消费），
        # 不再经 invoke Collection.configure 注入；勿在此重新登记，以免形成
        # 无人消费却误导维护者的第二事实源。
    }
)


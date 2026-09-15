---
id: "jupyter-podman-client-sdk-usage"
title: "作为 SDK 使用"
source: "README.md#6-作为-sdk-使用python-import"
---
# 作为 SDK 使用（Python import）

```python
from pathlib import Path
from invoke import MockContext

from jpman_client.tasks.client_core import load_image, run_container, stop_container
from jpman_client.tasks.utils import ContainerConfig, default_build_cache_dir, find_latest_image_tar

ctx = MockContext()

# 1) 加载镜像
tar = find_latest_image_tar(default_build_cache_dir())
result = load_image(ctx, tar)
assert result.loaded, result.message

# 2) 启动容器
cfg = ContainerConfig(
    image="localhost/jupyter-podman-rootless:latest",
    workspace="/mnt/d/spaces/SpecWeave",
    ssh_port=2222,
    jupyter_port=8888,
)
run_container(ctx, cfg)

# ... 使用完毕 ...
stop_container(ctx, cfg.name)
```
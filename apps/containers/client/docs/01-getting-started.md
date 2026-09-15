---
id: "jupyter-podman-client-getting-started"
title: "快速开始"
source: "README.md#2-安装"
---
# 快速开始

## 安装

> 需要 Python ≥ 3.14（与构建端 `py314` 环境对齐）。

```bash
cd apps/containers
pip install -e shared     # 先装两端共享包 jpman-common（连接层/平台工具，client 依赖它）
cd client
pip install -e .
# 验证
invoke --list
```

## 步骤 0：构建端先 save 出镜像缓存（首次/改镜像后）

```bash
cd ../jupyter-podman-rootless
bash bin/jpman rebuild-all    # 或 invoke build
bash bin/jpman save           # 产出 .image-cache/*.tar.gz
```

## 步骤 1：消费端加载镜像

```bash
cd ../client
# 方式 A：自动从构建端 .image-cache 选最新 tar.gz（推荐）
invoke load

# 方式 B：显式指定路径
invoke load --path /mnt/d/backup/jupyter-podman-rootless-xxxx.tar.gz
```

## 步骤 2：启动容器

```bash
# 使用默认配置（端口 2222/8888，工作区 ./workspace）
invoke run

# 指定工作区路径（Windows D 盘会自动转 /mnt/d）
invoke run --workspace D:/spaces/SpecWeave

# 显式传密码/token，不自动生成
invoke run --user-password mypass --jupyter-token mytoken32charsxxxxxxxx
```

启动成功后会打印 SSH/Jupyter URL 与挂载信息。

> **🛟 排障：JupyterLab 看不到 `.temp` / `.env` / `.gitignore` 等隐藏项**
>
> 症状：项目目录里的 `.temp`、`.env`、`.image-cache` 等以 `.` 开头的项在 JupyterLab 文件树里不显示。
> 根因：JupyterLab 前端默认**隐藏以 `.` 开头的文件/目录**——与服务端无关（服务端
> `ContentsManager/FileContentsManager.allow_hidden=True` 已内置）；挂载与容器内文件均正常，仅展示层隐藏。
> 修复：JupyterLab 顶部菜单 **View → Show Hidden Files** 勾选后即显示
> （`.temp` 为空目录时勾选后可见但为空，写入内容并刷新后即可看到文件）。

## 步骤 3：状态/停止/清理

```bash
invoke status        # 查看状态
invoke stop          # 停止+删除容器（保留镜像与工作区）
invoke clean --image # 连镜像一起删
invoke images        # 列出本地所有镜像
```

## 镜像备份与恢复（`invoke save` / `invoke load`）

```bash
# 备份（导出当前镜像到 .image-cache/，产物含 manifest + SHA256 + gzip 完整性校验）
invoke save                              # 默认保存 .env 的 IMAGE_TAG（client 叠加层）
invoke save --tag localhost/jupyter-podman-rootless:latest   # 指定镜像
# 保存 rootless 基底亦可走构建端: cd ../jupyter-podman-rootless && bash bin/jpman save

# 恢复
invoke load                              # 自动取 .image-cache/ 最新 tar
invoke load --path <具体 tar 路径>        # 指定文件恢复
```

- **产物命名**：`<镜像名>-<short_id>-<YYYYMMDD-HHMMSS>.tar.gz`（无 gzip 时降级为 `.tar` 未压缩，Windows 原生环境常见）
- **完整性**：写 `manifest.txt` 段（`IMAGE_FILE/SIZE/SHA256/SAVED`），`invoke load` 读取前按 manifest 校验（与构建端 `jpman save/load` 格式互操作）
- **用途**：VM 崩溃 / WSL 重置后 2-5 分钟恢复（对比重建 20-40 分钟），见构建端 [docs/16-image-cache.md](../../jupyter-podman-rootless/docs/16-image-cache.md)
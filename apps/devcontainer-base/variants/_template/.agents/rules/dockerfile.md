# __VARIANT_NAME__ 变体 Dockerfile 规范

## 基础信息

- **变体名称**：`__VARIANT_NAME__`
- **变体描述**：`__VARIANT_DESCRIPTION__`
- **基础镜像**：`devcontainer-base:__BASE_VARIANT__${BASE_TAG}`
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`（必须使用 BuildKit 语法）
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）
- **构建信息文件**：`/etc/__VARIANT_BUILD_INFO_NAME__`

## 核心约束

### 1. 服务继承（禁止破坏）

以下指令由基础镜像设置，**不得在变体 Dockerfile 中重新定义或覆盖**：

- `ENTRYPOINT`（保持 `/usr/bin/tini -- /usr/local/bin/entrypoint.sh`）
- `CMD`（保持 `[]`）
- `USER`（构建过程用 root，最终用户由基础镜像决定）
- `WORKDIR`（保持 `/workspace`）
- `HEALTHCHECK`（保持基础镜像的健康检查）
- `EXPOSE`、`VOLUME`（保持基础镜像声明）

### 2. 系统服务保护

基础镜像的所有服务在变体中必须保持可用：

- **sshd**：SSH 服务（端口 22）
- **dockerd**：Docker DinD（端口 2375）
- **podman**：Podman rootless（按需）
- **jupyter**：Jupyter Notebook/Lab（端口 8888），使用 `/opt/venv` 中的 Python 和 jupyter 包
- **supervisord**：进程管理，配置不变

### 3. PATH 优先级

- 默认 PATH 中 `/opt/venv/bin` 应保持优先（除非变体明确设计需要改变）
- 系统服务（Jupyter、supervisord、SSH 等）始终使用 `/opt/venv` 中的 Python
- 如果修改 PATH，请在文档中明确说明原因和影响

### 4. 权限管理

- 确保 devuser (UID 1000) 能够正常访问安装的工具和文件
- 系统级安装的工具应设置适当的权限（a+rX）
- 恢复 devuser 对 home 目录文件的所有权

### 5. 清理要求

- 每个变体构建结束时必须清理缓存：
  - `apt-get clean`
  - `rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*`
  - conda/pip 缓存（如使用）
- 目标：减小镜像体积，避免不必要的层

## Dockerfile 结构规范

模板默认提供 3 个追加阶段，可根据实际需求增加：

### Stage 1/N：基础验证 + 计时器初始化

- 验证基础镜像关键组件存在（devuser、/opt/venv、python）
- 初始化追加层计时器文件：`/tmp/.variant-build-timer`（或变体特有的计时器文件）
- 记录构建开始时间
- 输出 `[TIMER]` 阶段耗时

### Stage 2/N：自定义安装步骤（__EXTRA_INSTALL_STEPS__）

- 在此区域添加变体特有的安装逻辑
- 支持的安装方式：
  - `apt-get install`（系统包，使用 `--no-install-recommends`）
  - `conda install`（如基于 conda 变体）
  - `pip install`（注意区分系统 venv 和 conda）
  - 下载解压二进制包
  - 编译安装
- 使用 BuildKit cache 挂载加速重复构建：
  - apt: `--mount=type=cache,target=/var/cache/apt,sharing=locked`
  - conda: `--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- 每个主要步骤输出 `[ACTION]`、`[INFO]`、`[OK]` 日志
- 阶段结束输出 `[TIMER]`

### Stage N/N：元数据 + 清理 + 最终验证

- 写入构建元数据到 `/etc/__VARIANT_BUILD_INFO_NAME__`：
  - `BUILD_DATE`：UTC 时间戳
  - `VARIANT`：变体名称
  - `VARIANT_DESCRIPTION`：变体描述
  - `BASE_IMAGE`：基础镜像
  - 镜像源配置（APT_MIRROR、CONDA_MIRROR、PIP_MIRROR）
  - 变体特有的版本信息
  - `SYSTEM_VENV=/opt/venv`
  - `SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord`
  - `BUILD_TIMER=enabled`
- 执行清理（见"清理要求"）
- **[VALIDATION CHECKPOINT]** 最终验证：
  1. `/opt/venv` 存在且有 python（系统 venv 保留）
  2. Jupyter 仍可通过 venv 使用
  3. docker、supervisord 仍存在（服务未被破坏）
  4. devuser 存在且可访问
  5. **变体特有验证**（__EXTRA_VALIDATION__）：验证安装的工具可用
- 输出 **BUILD TIMING SUMMARY** 表格
- 清理计时器文件
- 输出构建完成提示

## 日志/输出规范

- 文件开头：详细的注释块，包含构建/运行/验证命令示例、阶段分层说明
- 阶段开始：
  ```
  echo "########################################################################"
  echo "# [__VARIANT_NAME__ VARIANT STAGE N/N] Stage Description"
  echo "########################################################################"
  ```
- 动作标记：`[ACTION]`（正在执行）、`[INFO]`（信息）、`[OK]`（成功）、`[WARN]`（警告）、`[ERROR]`（错误）
- 计时器格式：`[TIMER] Stage N/N (description) took Xs | Variant cumulative: Ys`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[ERROR]` 后必须 `exit 1`

## 构建参数

通用构建参数（所有变体支持）：

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna/official（如使用 conda） |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official |

变体特有参数：请在 `__EXTRA_BUILD_ARGS__` 区域声明，并在 .env.example 中提供默认值和说明。

## 新增步骤注意事项

1. **层缓存优化**：将变化频率低的步骤放在前面，变化频率高的步骤放在后面
2. **错误处理**：使用 `set -e` 已通过 SHELL 声明启用，关键步骤添加明确的错误检查
3. **可读性**：每个阶段使用 `# ═══════════════════════════════════════════` 分隔线
4. **注释**：复杂逻辑添加注释说明设计意图
5. **可验证性**：每个安装步骤后立即验证安装结果
6. **参考现有变体**：参考 `variants/conda/` 和 `variants/conda-llvm/` 的实现模式

## Checklist（提交前确认）

- [ ] 语法声明正确：`# syntax=docker/dockerfile:1.7-labs`
- [ ] SHELL 指令显式声明
- [ ] 未覆盖 ENTRYPOINT/CMD/USER/WORKDIR 等基础镜像指令
- [ ] 所有阶段都有 `[TIMER]` 输出
- [ ] 最终有 `[VALIDATION CHECKPOINT]`
- [ ] 包含 BUILD TIMING SUMMARY 表格
- [ ] 构建元数据已写入 `/etc/__VARIANT_BUILD_INFO_NAME__`
- [ ] 执行了清理步骤
- [ ] 验证了核心服务（Jupyter、Docker、supervisord）未被破坏
- [ ] 验证了变体特有功能
- [ ] devuser 权限正确
- [ ] 注释完整，包含构建/运行/验证示例

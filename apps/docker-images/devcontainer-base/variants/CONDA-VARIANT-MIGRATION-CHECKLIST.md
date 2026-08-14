# conda 变体迁移检查清单

> **迁移目标**：移除冗余的 `variants/conda/` 目录，将镜像源配置内聚到基础镜像，简化构建链为 `base → conda-llvm → onnx-pytorch → onnx-quantized`。

---

## ✅ 代码修改完成确认

### 文件修改清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `variants/build.sh` | 1. 从 VARIANTS 数组移除 conda 条目<br>2. conda-llvm 依赖字段设为空（直接依赖基础镜像） | ✅ 已完成 |
| `Dockerfile`（基础镜像） | 1. Stage 2.4：系统级 `/opt/conda/.condarc` 写入（含镜像源+性能参数+`auto_activate_base: false`）<br>2. Stage 2.4：root 用户全局 `/root/.config/pip/pip.conf` 配置<br>3. Stage 2.4：conda base 环境 pip 镜像配置<br>4. Stage 2.4：conda main 环境 pip 镜像配置<br>5. Stage 2.5：创建 devuser 后配置 `/home/devuser/.config/pip/pip.conf`<br>6. Stage 2.5：修正 conda-init.sh 激活 `main` 环境（fallback 到 base）<br>7. Stage 2.5：修正 `/etc/environment` PATH 包含 `/opt/conda/envs/main/bin`<br>8. Stage 2.7：添加镜像源配置验证（.condarc + root/devuser pip.conf） | ✅ 已完成 |
| `variants/conda-llvm/Dockerfile` | 1. FROM 改为 `devcontainer-base:${BASE_TAG}`（移除 conda 中间层）<br>2. 头部注释更新<br>3. build-info 中 BASE_IMAGE 字段更新<br>4. PYTHON_ENV 从 `conda-base` 改为 `conda-main` | ✅ 已完成 |
| `variants/AGENTS.md` | 1. 可用变体列表移除 conda<br>2. 目录树移除 conda/ 条目<br>3. 上下文路由表移除 conda 变体路由<br>4. 核心规范入口移除 conda 变体规范<br>5. 共享脚本说明更新 | ✅ 已完成 |

---

## 🔍 构建前验证

### 1. 语法检查

| 检查项 | 验证命令 | 预期结果 |
|--------|---------|---------|
| 基础镜像 Dockerfile 语法 | `docker build --target base -f Dockerfile . --no-cache --pull 2>&1 \| head -100` | 无语法错误，能正常解析 |
| build.sh 语法 | `bash -n variants/build.sh` | 退出码 0，无输出 |
| conda-llvm Dockerfile 语法 | （依赖基础镜像构建成功后验证） | 无语法错误 |

### 2. 配置一致性检查

- [ ] 确认 `PYTHON_BUILD=cp314t` 时，Stage 2.4 的 free-threading 验证仍可通过
- [ ] 确认 Stage 2.5 创建 devuser 后，`/home/devuser/.config/pip/pip.conf` 权限正确（devuser:devuser 所有）
- [ ] 确认 `/opt/conda/.condarc` 中包含：
  - [ ] `channels: [conda-forge]`
  - [ ] `channel_priority: strict`
  - [ ] `auto_activate_base: false`
  - [ ] `solver: libmamba`
  - [ ] 镜像源配置（使用 tuna/aliyun 时）
- [ ] 确认 conda-init.sh 激活顺序正确：先尝试 `conda activate main`，失败则 fallback 到 base

---

## 🧪 构建测试

### 测试矩阵（必须全部通过）

| # | 测试场景 | 构建命令 | 预期结果 |
|---|---------|---------|---------|
| 1 | 基础镜像（官方源） | `docker build -t devcontainer-base:test --build-arg APT_MIRROR=official --build-arg CONDA_MIRROR=official --build-arg PIP_MIRROR=official .` | Stage 2.7 所有验证通过 |
| 2 | 基础镜像（清华源） | `docker build -t devcontainer-base:test-cn --build-arg APT_MIRROR=tuna --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=tuna .` | Stage 2.7 所有验证通过 |
| 3 | 基础镜像（阿里云源） | `docker build -t devcontainer-base:test-aliyun --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun .` | Stage 2.7 所有验证通过 |

### 基础镜像运行时验证（构建成功后）

```bash
# 启动容器
docker run -d --name test-base --privileged -e USER_PASSWORD=test devcontainer-base:test

# 1. root 用户验证
docker exec test-base bash -c "
    echo '=== conda 验证 ==='
    conda --version
    conda info --envs
    echo '=== Python 验证（应是 main 环境） ==='
    which python
    python --version
    python -c 'import sysconfig; print(\"SOABI:\", sysconfig.get_config_var(\"SOABI\"))'
    echo '=== 镜像源验证 ==='
    cat /opt/conda/.condarc
    echo '=== pip 配置验证（root） ==='
    pip config get global.index-url
    echo '=== /etc/environment PATH 验证 ==='
    grep PATH /etc/environment
"

# 2. devuser 用户验证
docker exec test-base su - devuser -c "
    echo '=== devuser conda 验证 ==='
    conda --version
    echo '=== devuser Python 验证 ==='
    which python
    python --version
    echo '=== devuser pip 配置验证 ==='
    pip config get global.index-url
    echo '=== devuser .bashrc 激活验证 ==='
    echo \"CONDA_DEFAULT_ENV=\$CONDA_DEFAULT_ENV\"
"

# 3. 服务验证
docker exec test-base bash -c "
    sshd -t && echo '[OK] sshd config valid'
    supervisord --version && echo '[OK] supervisord available'
    docker --version && echo '[OK] docker available'
    test ! -d /opt/venv && echo '[OK] /opt/venv does not exist'
"

# 清理
docker rm -f test-base
```

---

## 🔗 变体链构建测试

基础镜像验证通过后，继续构建上层变体：

| # | 测试场景 | 构建命令 | 预期结果 |
|---|---------|---------|---------|
| 4 | conda-llvm 变体 | `cd variants && bash build.sh --base-tag test --only conda-llvm --push false` | 构建成功，4个追加层验证通过 |
| 5 | onnx-pytorch 变体 | `cd variants && bash build.sh --base-tag test --only onnx-pytorch --push false` | 构建成功，继承 conda-llvm 验证通过 |
| 6 | onnx-quantized 变体 | `cd variants && bash build.sh --base-tag test --only onnx-quantized --push false` | 构建成功 |
| 7 | ai-dev 变体（如果存在） | `cd variants && bash build.sh --base-tag test --only ai-dev --push false` | 构建成功 |

### 全量构建测试

```bash
cd variants
bash build.sh --base-tag test-full --push false --verify-mode standard
```

预期结果：
- [ ] 构建拓扑顺序正确：conda-llvm → onnx-pytorch → onnx-quantized（无 conda 步骤）
- [ ] 所有变体的验证命令全部通过
- [ ] 总构建时间不显著增加（由于镜像源内置可能略有减少）

---

## 🚮 删除 conda 变体前最终确认

### 1. 无其他引用检查

- [ ] 搜索整个代码库，确认没有脚本/文档/CI 配置引用 `devcontainer-base:conda-` 标签
```bash
grep -r "devcontainer-base:conda" d:\spaces\SpecWeave --include="*.sh" --include="*.md" --include="*.yml" --include="*.yaml" --include="Dockerfile*"
```
- [ ] 确认 `.github/workflows/` 中没有 CI 工作流依赖 conda 变体
- [ ] 确认 `scripts/` 下没有脚本硬编码引用 conda 变体

### 2. 废弃文件确认（可删除）

以下文件/目录在验证全部通过后可以删除：
- [ ] `variants/conda/Dockerfile`
- [ ] `variants/conda/README.md`
- [ ] `variants/conda/.env.example`
- [ ] `variants/conda/.agents/`（整个目录）
- [ ] `variants/shared/scripts/conda-mirror-setup.sh`（功能已合并到基础镜像，仅保留 conda-perf-setup.sh）

### 3. 文档更新确认

- [ ] `variants/README.md`（如果存在）已更新变体列表
- [ ] 父级 `README.md`（devcontainer-base 根目录）已更新构建说明
- [ ] 如有发布说明，记录 conda 变体合并到基础镜像的变更

---

## ⚠️ 回滚方案

如果构建过程中出现问题，可以快速回滚：

```bash
# 1. 恢复 build.sh
git checkout variants/build.sh

# 2. 恢复 conda-llvm/Dockerfile
git checkout variants/conda-llvm/Dockerfile

# 3. 恢复基础镜像 Dockerfile
git checkout Dockerfile

# 4. 恢复 variants/AGENTS.md
git checkout variants/AGENTS.md
```

---

## 📋 验收标准

迁移完成的标志：
1. ✅ 基础镜像在三种镜像源配置（official/tuna/aliyun）下均可构建成功
2. ✅ Stage 2.7 新增的镜像源验证全部通过
3. ✅ root 和 devuser 用户均可正常使用 conda 和 pip，镜像源配置正确
4. ✅ conda 默认激活 main 环境（Python 3.14 free-threading）
5. ✅ conda-llvm 变体直接从基础镜像构建成功，无需中间 conda 层
6. ✅ 全量变体链构建成功，所有原有验证通过
7. ✅ 代码库搜索无对 conda 变体的遗留引用
8. ✅ 删除 conda/ 目录后构建仍成功

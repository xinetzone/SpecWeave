---
id: "retrospective-caffe-ffi-conda-build-20260730-backlog"
title: "洞察行动项 Backlog：caffe-ffi Conda 包构建验证"
date: 2026-07-30
type: insight-action-backlog
status: active
source: "caffe-ffi Conda 包构建验证复盘"
ssot:
  retrospective_source: README.md
  insight_source: README.md#s3-洞察与模式萃取
---
# 洞察行动项 Backlog

> 本文件记录从 caffe-ffi Conda 包构建验证复盘中转化的可执行行动项。核心包含：**1项高优先级改进**（editable残留自动清理）+ 3项中优先级改进（meta.yaml注释、RPATH健壮性、模式沉淀）+ 1项低优先级改进（macOS跨平台支持）。

## 行动项总览

| ID | 行动项 | 优先级 | 类型 | 状态 | 预期收益 |
|----|--------|--------|------|------|---------|
| ACT-001 | build.sh 增加 `_editable_*.pth` 自动清理步骤 | 🔴高 | 质量门禁 | ✅ 已完成 | 消除editable残留干扰，确保验证环境干净 |
| ACT-002 | meta.yaml 增加 `missing_dso_whitelist` 详细注释 | 🟡中 | 文档 | ⏳ 待执行 | 其他开发者理解DSO白名单用途，降低维护成本 |
| ACT-003 | RPATH 改进：使用 `$PREFIX/lib` 绝对路径替代 `$ORIGIN/../../..` | 🟡中 | 健壮性 | ⏳ 待执行 | 不依赖conda-build自动重定位，降低跨环境风险 |
| ACT-004 | macOS conda 包支持（`@rpath`/`@loader_path`） | 🟢低 | 跨平台 | ⏳ 待执行 | macOS用户可直接使用conda包 |
| ACT-005 | 将洞察/模式萃取为正式模式文档存入 patterns/ | 🟡中 | 知识沉淀 | ⏳ 待执行 | 模式可复用，其他scikit-build-core项目受益 |

---

## 🔴 高优先级行动项

### ACT-001：build.sh 增加 `_editable_*.pth` 自动清理步骤 ✅ 已完成

- **优先级**：🔴 高
- **来源**：复盘 §S3 洞察3 — Editable Install 残留对 Conda 包验证的干扰
- **责任人**：caffe-ffi conda recipe 维护者
- **预期收益**：在有 editable install 残留的开发容器中，验证脚本也能正确加载 conda 包，避免误判
- **状态**：✅ **已完成**（2026-07-30）
- **验收标准（DoD）**：
  1. ✅ test-conda-build.sh 在构建前（Step 1b）和安装前（Step 7a）自动查找并删除 `_editable_*.pth` 文件及对应finder模块
  2. ✅ 清理函数 `clean_editable_residuals()` 同时清理：`_editable_skbc_*.pth/.py`、`__editable__.*.pth`、`__pycache__`缓存、pip的`direct_url.json`
  3. ✅ 验证步骤包含加载路径检查，确认从 site-packages 加载
  4. ✅ 在有 editable 残留的环境中运行脚本，验证能正确通过（首次运行清理3个残留文件，二次运行无残留）
- **涉及文件**：
  - [scripts/test-conda-build.sh](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh#L186-L201)（Step 7 安装步骤）
- **实施步骤**：
  1. 在 Step 7（Installing built package）中，`pip uninstall` 之后增加：
     ```bash
     # Clean up editable install residuals
     _ED_PTH=$(python -c "import site; print(site.getsitepackages()[0])" 2>/dev/null)
     if [ -n "$_ED_PTH" ]; then
         _CLEANED=$(find "$_ED_PTH" -name "_editable_*.pth" -delete -print 2>/dev/null | wc -l)
         echo "  Cleaned $_CLEANED editable .pth file(s)"
     fi
     ```
  2. 将 `conda install` 命令改为 `conda install -y --offline --use-local --force-reinstall`
  3. 在 Step 8 验证开头增加路径检查：
     ```bash
     _CAFFE_FILE=$(python -c "import caffe_ffi; print(caffe_ffi.__file__)" 2>/dev/null)
     echo "  Loading from: $_CAFFE_FILE"
     if echo "$_CAFFE_FILE" | grep -q "site-packages"; then
         pass "Loading from site-packages (conda package)"
     else
         warn "Not loading from site-packages (may be editable install residual)"
     fi
     ```

---

## 🟡 中优先级行动项

### ACT-002：meta.yaml 增加 `missing_dso_whitelist` 详细注释

- **优先级**：🟡 中
- **来源**：复盘 §S1 修改文件清单 — meta.yaml missing_dso_whitelist 缺乏说明
- **责任人**：caffe-ffi conda recipe 维护者
- **预期收益**：其他维护者能快速理解哪些库是 vendored/bundled，避免误删白名单导致构建失败
- **验收标准（DoD）**：
  1. `missing_dso_whitelist` 段每一行有 YAML 注释说明
  2. 注释说明白名单的原因（vendored、动态加载、conda-build误报等）
- **涉及文件**：
  - [conda.recipe/meta.yaml](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml#L14-L17)
- **实施步骤**：
  1. 在 `missing_dso_whitelist:` 上方添加块注释说明用途
  2. 为每个白名单条目添加行内注释

### ACT-003：RPATH 改进 — 使用 `$PREFIX/lib` 绝对路径替代相对路径

- **优先级**：🟡 中
- **来源**：复盘 §S2 瓶颈与约束 — conda-build 自动重定位依赖
- **责任人**：caffe-ffi 构建系统维护者
- **预期收益**：不依赖 conda-build 的自动 RPATH 重定位行为，在不同 conda 版本/环境中更健壮
- **验收标准（DoD）**：
  1. build.sh 中 NEW_RPATH 使用 `$ORIGIN:$ORIGIN/lib:${PREFIX}/lib`（当前已包含 PREFIX/lib，但验证是否被 conda-build 覆盖）
  2. 构建后验证 RPATH 中包含 PREFIX/lib 的绝对路径
  3. 在全新 conda 环境中安装验证 ldd 全部解析
- **涉及文件**：
  - [conda.recipe/build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L198-L211)
- **实施步骤**：
  1. 检查 conda-build 是否会覆盖 build.sh 中 patchelf 设置的 RPATH
  2. 若被覆盖，在 build.sh 末尾添加 conda-build 后的 RPATH 修复步骤（通过 post-link 脚本或调整 build.sh 执行时机）
  3. 验证修复后 RPATH 在安装环境中正确

### ACT-005：将洞察/模式萃取为正式模式文档存入 patterns/

- **优先级**：🟡 中
- **来源**：复盘 §S3 模式1和模式2
- **责任人**：方法论维护者
- **预期收益**：其他使用 conda-build + scikit-build-core 的项目可直接参考模式，避免重复踩坑
- **验收标准（DoD）**：
  1. 创建模式文档 `.agents/docs/retrospective/patterns/methodology-patterns/python-packaging/conda-build-scikit-build-core.md`
  2. 模式包含：触发场景、meta.yaml模板、build.sh模板、RPATH设置、反模式清单
  3. 创建模式文档 `.agents/docs/retrospective/patterns/methodology-patterns/python-packaging/conda-clean-environment-verification.md`
  4. 模式包含：editable残留清理、pth文件检查、路径验证、ldd验证步骤
  5. 更新 patterns/ 索引
- **涉及文件**：新模式文档 + 模式索引
- **实施步骤**：
  1. 参考现有模式文档格式（如 wheel 自包含打包模式）
  2. 提炼 meta.yaml 三段式依赖模板和 build.sh 关键配置模板
  3. 编写反模式清单（从本次踩坑记录中提取）
  4. 标注成熟度 L2
  5. 更新模式索引文件

---

## 🟢 低优先级行动项

### ACT-004：macOS conda 包支持

- **优先级**：🟢 低
- **来源**：复盘 §S2 瓶颈与约束
- **责任人**：caffe-ffi 跨平台维护者
- **预期收益**：macOS 用户可通过 conda 直接安装 caffe-ffi
- **验收标准（DoD）**：
  1. conda-build 支持 macOS（osx-64 / osx-arm64）
  2. RPATH 使用 `@rpath`/`@loader_path` 替代 `$ORIGIN`
  3. patchelf 在 macOS 上使用 `install_name_tool` 替代
  4. 在 macOS 环境中构建并通过 ldd 等价验证（`otool -L`）
- **实施步骤**：
  1. 在 meta.yaml 中增加 macOS 平台支持（移除 skip 限制或添加 osx 支持）
  2. build.sh 中检测平台，Linux 用 patchelf/$ORIGIN，macOS 用 install_name_tool/@rpath
  3. 增加 `bld.bat`（Windows）或 `build.sh` 中增加 macOS 分支
  4. 在 macOS CI 或本地环境中验证

---

## 行动项依赖关系

```
ACT-001（editable残留清理）── 独立可执行，无需前置依赖
    │
    └── 为 ACT-003 的RPATH验证提供干净环境基础

ACT-002（meta.yaml注释）── 独立可执行，文档改进无代码依赖

ACT-003（RPATH健壮性）── 建议在 ACT-001 完成后验证（需要干净环境）

ACT-004（macOS支持）── 依赖 ACT-003 的RPATH改进（需要先稳定Linux RPATH）

ACT-005（模式沉淀）── 建议在 ACT-001/ACT-002/ACT-003 完成后沉淀
    （包含最终版本的最佳实践，而非中间状态）
```

---

## 完成追踪

| ID | 状态 | 完成日期 | 验证结果 |
|----|------|---------|---------|
| ACT-001 | ✅ 已完成 | 2026-07-30 | Docker容器中验证通过：首次运行清理3个editable残留文件（_editable_skbc_caffe_ffi.pth + finder模块 + direct_url.json），二次运行环境已干净无残留 |
| ACT-002 | ⏳ 待执行 | - | - |
| ACT-003 | ⏳ 待执行 | - | - |
| ACT-004 | ⏳ 待执行 | - | - |
| ACT-005 | ⏳ 待执行 | - | - |

---

## 快速执行参考

```bash
# ACT-001: 验证editable清理效果
cd /path/to/caffe-ffi-jupyter
# 模拟editable残留后运行脚本
docker exec caffe-ffi-jupyter bash -c "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&
  pip install -e /SpecWeave/projects/xuanspace/libs/caffe-ffi &&
  bash /SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh
"

# ACT-002: 查看当前 meta.yaml
cat projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml

# ACT-003: 验证RPATH在安装后的实际值
docker exec caffe-ffi-jupyter bash -c "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&
  CAFFE_SO=\$(python -c 'import caffe_ffi, glob, os; print(glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi*.so\"))[0]') &&
  echo 'RPATH:' && patchelf --print-rpath \$CAFFE_SO &&
  echo 'ldd check:' && ldd \$CAFFE_SO | grep 'not found' && echo FAIL || echo PASS
"
```

**行动项总结**：5项行动项中，ACT-001（editable残留自动清理）为🔴高优先级，直接影响conda包验证的可靠性。ACT-002/003/005为🟡中优先级，分别改进文档、健壮性和知识沉淀。ACT-004为🟢低优先级跨平台扩展。建议优先执行ACT-001，其余按依赖关系逐步推进。

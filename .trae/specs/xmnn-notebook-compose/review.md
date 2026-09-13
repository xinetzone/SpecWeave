# xmnn-whl-builder → .temp/notebook podman-compose 迁移 - Independent Review

- [x] CP-R1: compose 三文件 config 静态解析五断言（AC-1，TR-2.1/3.1/4.1/6.1）
  - **Type**: `rule`
  - **Covers**: AC-1
  - **Evidence**: R1 独立执行三条 config 退出码均 0：默认 1 服务/8888/三必需/1 bind；sources 合并 3 bind（targets notebooks/npu_tvm/npuusertools，按 target 去重）；build 合并 context=/mnt/d/spaces/SpecWeave/external/chaos、dockerfile=ai/xmnn-whl-builder/Dockerfile、PIP_MIRROR=aliyun。

- [x] CP-R2: Notebook 栈独立 E2E 可达（AC-2，TR-7.1）
  - **Type**: `rule`
  - **Covers**: AC-2
  - **Evidence**: up 退出 0，容器 Up + `0.0.0.0:8888->8888`（22 未发布）；无凭据 curl /lab=200、/api=200（version 2.20.0）、/api/contents=200、/api/contents/smoke.ipynb=200；kernelspec 含 xmnn-whl-builder；cp314 python `import tvm,vta,xmnn` 退出 0（xmnn 1.2.1.dev0）；smoke.ipynb 9p 可见；PID1 argv 与声明一致；Privileged=false、/dev/fuse 字符设备可见。

- [x] CP-R3: smoke.ipynb 在 xmnn-whl-builder 内核 nbconvert 通过（AC-3，TR-7.2）
  - **Type**: `rule`
  - **Covers**: AC-3
  - **Evidence**: nbconvert 退出 0；输出含 `a + b = [2. 3. 4. 5.]` 与 `[OK] tvm.build LLVM vector add passed: [2.0, 3.0, 4.0, 5.0]`（tvm 0.19.0）；error 单元=0（grep ename=0 + JSON 解析）；宿主源文件 outputs 仍为 0。

- [x] CP-R4: sources 覆盖挂载两源码树标志文件（AC-4，TR-7.3）
  - **Type**: `rule`
  - **Covers**: AC-4
  - **Evidence**: 双文件 up 后 ls /workspace/npu_tvm/version.py（7720B）与 /workspace/npuusertools/AGENTS.md（7019B）退出 0；mount 表证实三条 9p bind 并存（list 追加/去重语义）。

- [x] CP-R5: build-compose.sh 静态可用性（AC-5，TR-4.2/4.3）
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Evidence**: bash -n=0；--help=0（REPO_ROOT 6 级 cd 成功）；grep 确认 export BUILDAH_FORMAT=docker 与 trap EXIT/INT/TERM/HUP；审查者用 /tmp 样例与真实 .dockerignore 副本独立验证三条 sed 表达式及 cp→patch→restore 全周期 diff 一致；未触发真实 build。

- [x] CP-R6: 零侵入与 down 零残留（AC-6，TR-7.4/8.1）
  - **Type**: `rule`
  - **Covers**: AC-6
  - **Evidence**: 终态项目容器=0、xmnn 网络=0、xmnn pod=0、8888 释放；check-ignore 命中 client/.gitignore:35 `.temp/`；`git status --porcelain -- apps/containers/client` 零输出；.dockerignore mtime=2026-08-28 无备份残留；external/chaos/ai 仅两处先存 M（mtime 2026-08-12）与 logs/（2026-09-08），时间戳证实非本次引入。

- [x] CP-U1: OKF podman-compose 知识包模式保真度（AC-7，TR-2.3）
  - **Type**: `rubric`
  - **Covers**: AC-7
  - **Scale**: 1-5
  - **Anchors**: 1 = 出现知识包明确反对写法（旧式顶层 x-podman 字典/特权/短语法自动建目录/列表覆盖误用）；3 = 可运行但 ≥2 处无依据偏离；5 = 非平凡写法均可指认 concepts 章节
  - **Pass Threshold**: >= 4
  - **Evidence**: **4/5 pass**。标准字段/端口/bind/插值/深合并/注释引用逐条回查 concepts/02/03/06/08 均真实成立；两处 machine 修复（network_mode: bridge、healthcheck.disable）经最小反例与 podman run 对照独立证实为硬必需且为 Compose 标准字段。扣 1 分：`cgroupns: host` 在 podman-compose 1.6.0 无翻译器（运行时 cgroup ns inode 对照实证为空操作）——已按 advisory-1 修正注释为「声明性字段」，字段保留以对齐 client C11。

- [x] CP-U2: 产物原子性与极简度（AC-8，TR-8.2）
  - **Type**: `rubric`
  - **Covers**: AC-8
  - **Scale**: 1-5
  - **Anchors**: 1 = 多职责混杂或冗余文件；3 = 1-2 个可删文件/段落；5 = 6 文件最少必要集且单一职责
  - **Pass Threshold**: >= 4
  - **Evidence**: **5/5 pass**。恰 6 文件、零 *.md/.env/备份；compose×3 与 wrapper/smoke 职责单一；compose 引用变量集合与 .env.example 8 行完全相等，无悬空/遗漏。advisory-2（usage sed 越界打印代码行）已修复为 `sed -n '2,18p'`，回归 SYNTAX-OK/help 边界正确/config 退出 0。

## Review History

### Review R1（fresh-context 独立审查，2026-09-13）
- **Result**: `pass`
- **Evidence**: CP-R1～R6 全 pass；CP-U1=4、CP-U2=5 过阈值；实现者三项环境声明（bridge 硬必需 / healthcheck.disable 硬必需 / 空 token=免认证）均被独立取证属实。
- **Findings 处置**：
  - advisory-1（cgroupns 1.6.0 空操作注释高估）→ 已采纳：compose.yaml 注释改为声明性说明并保留字段（回归 config OK）。
  - advisory-2（usage() sed 2,22p 越界）→ 已采纳：改 2,18p（回归 help 末行为注释闭合行、bash -n 通过）。
  - advisory-3（先存空 pod `pod_notebook`，属既有 notebook 样本项目、46h+ 0 容器）→ 不在本任务范围，保留不动，终态报告中提示用户择机 `podman pod rm pod_notebook`。
  - 无 actionable 发现，不产生 remediation 队列。

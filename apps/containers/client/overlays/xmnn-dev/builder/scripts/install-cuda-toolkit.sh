#!/usr/bin/env bash
# xmnn-dev CUDA 编译器工具链安装层（Containerfile.xmnn-dev Layer 2.6）
#
# 由 TORCH_FLAVOR 驱动（与 Layer 2.5 同一构建期维度）：
#   ""  / cpu 不装 —— 默认与 CPU 形态零 CUDA 编译器，镜像与改造前逐字等价
#   cu130      cu130 形态同时获得 CUDA 编译器工具链（nvcc）
#
# 为什么并入 cu130 形态，而不是新增独立构建开关（2026-09-20 裁决）：
#   ① 用户对 cu130 的心智模型是「CUDA 13 开发环境」；只有运行时没有编译器的
#      cu130 是半形态（本次事故即由此而来）；
#   ② 独立开关会引入第三个「同 tag 不同内容」的形态维度，而复用 C20 归档
#      身份需改动 save/load 命名契约——收益不抵复杂度；
#   ③ 默认形态（""/cpu）不受影响，C18「默认全关 = 默认隔离」条款不变。
#
# 三包版本必须**同轨**（2026-09-20 实测）：nvcc 含 ptxas/nvlink/cudafe++，
# nvvm 含 cicc + libdevice，cuda-crt 含 crt 头。混版（nvcc 13.0.88 + 解析器
# 顺带升级的 nvvm 13.4.92）→ cicc 产出 PTX `.version 9.4`、ptxas 只认 9.0
# → `ptxas fatal: Unsupported .version 9.4`，故三者必须同一 pin。
#
# 为什么 pin 13.4.92 而不是与 torch 运行时同轨的 13.0.x（2026-09-20 实测）：
#   基座为 Ubuntu 26.04 / glibc 2.43，CUDA 13.0 的 crt/math_functions.h 与
#   glibc mathcalls.h 的 `rsqrt` noexcept 规格冲突（前端报 "exception
#   specification is incompatible"，-std=c++14/17/20 三档均复现）；13.4.92
#   实测编译通过。故「编译器线高于 torch 运行时线」是**基座约束**而非选型
#   偏好；torch 的 CUDA 运行时仍由 cu130 wheel 自带，不受影响。
#
# 布局（/usr/local/cuda 农场，2026-09-20 实测三连）：
#   pip 包把 nvcc 装到 site-packages/nvidia/cu13/{bin,nvvm}，该布局**没有
#   lib64**（nvcc 默认 -L 找 lib64）也**没有 libcudart.so 短名** → 直接链接
#   必失败；且 nvcc **以 argv[0] 所在目录定位自身根**（bin/..//include）：
#     ① 裸软链 /usr/local/bin/nvcc → 真身：假通过（_HERE_ 落在 /usr/local/bin，
#        找不到 crt/include，报 `cuda_runtime.h: No such file`）；
#     ② 农场 /usr/local/cuda/{bin,include,lib64,nvvm} → pip 实体 + 短名软链；
#     ③ /usr/local/bin/nvcc 是**包装器**，exec 农场全路径（argv[0] 合规）。
#   CUDA_HOME=/usr/local/cuda 由 Containerfile 末尾 ENV 提供（torch 扩展编译
#   等生态工具的约定路径；无它则 `which nvcc` 推出 /usr/local 而解析错）。
#
# 幂等性：脚本可重跑（软链 -sfn、短名按存在性补建、包装器直接覆写）；
#   **禁止**在运行期 pip 升级单个 CUDA 组件——重装/升级 nvidia-* 包会丢短名
#   软链，须回有网侧重打镜像（与离线契约 C12 §10 同源纪律）。
set -euo pipefail

PY=/opt/conda/bin/python
MARKER=/opt/xmnn-cuda-nvcc-version
CUDA_HOME_DIR=/usr/local/cuda
FLAVOR="${TORCH_FLAVOR:-}"

# —— flavor → nvcc 版本映射（唯一事实源；未来新增 CUDA 形态在此加一行） ——
case "${FLAVOR}" in
  "")
    echo "[xmnn] cuda-nvcc: skipped（TORCH_FLAVOR 为空 —— 默认镜像无 torch 亦无 CUDA 编译器）"
    exit 0
    ;;
  cpu)
    echo "[xmnn] cuda-nvcc: skipped（cpu 形态不带 CUDA 编译器）"
    exit 0
    ;;
  cu130)
    NVCC_VERSION=13.4.92
    ;;
  *)
    echo "[xmnn] ERROR: TORCH_FLAVOR 必须为空|cpu|cu130，实际为 '${FLAVOR}'" >&2
    exit 1
    ;;
esac

# —— pip 索引：PIP_MIRROR 三档映射，与 Layer 3 的 pip config 同键同源（C15） ——
case "${PIP_MIRROR:-official}" in
  aliyun) PIP_INDEX=https://mirrors.aliyun.com/pypi/simple/ ;;
  tuna)   PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple ;;
  *)      PIP_INDEX=https://pypi.org/simple ;;
esac

SITE=$("${PY}" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
CU13="${SITE}/nvidia/cu13"

echo "[xmnn] cuda-nvcc: 安装 ${NVCC_VERSION} 三件套（nvcc + cuda-crt + nvvm，同轨 pin）"
"${PY}" -m pip install --no-cache-dir --index-url "${PIP_INDEX}" \
  "nvidia-cuda-nvcc==${NVCC_VERSION}" \
  "nvidia-cuda-crt==${NVCC_VERSION}" \
  "nvidia-nvvm==${NVCC_VERSION}"
rm -rf /root/.cache/pip

# —— /usr/local/cuda 农场：pip 布局 → 约定 CUDA_HOME 布局 ——
mkdir -p "${CUDA_HOME_DIR}"
ln -sfn "${CU13}/bin"     "${CUDA_HOME_DIR}/bin"
ln -sfn "${CU13}/include" "${CUDA_HOME_DIR}/include"
ln -sfn "${CU13}/lib"     "${CUDA_HOME_DIR}/lib64"
ln -sfn "${CU13}/nvvm"    "${CUDA_HOME_DIR}/nvvm"

# 短名软链：nvcc 默认只把 lib64 加进链接搜索路径，而 pip 布局无 `libcudart.so`
# 短名（实测 `cannot find -lcudart`）。按真实 toolkit 的 lib64 约定，为 cu13/lib
# 内所有 `lib*.so.<ver>` 补 `lib*.so` 短名（已存在则不覆盖）。
for f in "${CU13}"/lib/lib*.so.*; do
  [ -e "${f}" ] || continue
  base=${f##*/}
  short=${base%%.so.*}.so
  [ -e "${CU13}/lib/${short}" ] || ln -s "${base}" "${CU13}/lib/${short}"
done

# —— /usr/local/bin/nvcc 包装器（唯一入口） ——
# 直接软链真身会因 argv[0] 根定位错误而找不到头文件（实测假通过），必须 exec
# 全路径；包装器同时是「nvcc 该怎么被调用」的唯一纪律载体。
cat > /usr/local/bin/nvcc <<'WRAP'
#!/bin/sh
# nvcc 以 argv[0] 目录定位自身根（crt/include/nvvm），故必须 exec 农场全路径。
exec /usr/local/cuda/bin/nvcc "$@"
WRAP
chmod 0755 /usr/local/bin/nvcc

# —— 动态链接器登记：编译产物「开箱即跑」 ——
# 真实 CUDA toolkit 安装器同款做法（/etc/ld.so.conf.d/*.conf + ldconfig）。
# 无此步时 nvcc 编出的二进制**在运行期**才报 `libcudart.so.13: cannot open
# shared object file`（链接期有 nvcc 默认 -L，运行期 ld.so 不认识 /usr/local/cuda/lib64）
# ——2026-09-20 真机实测；唯一替代是让用户设 LD_LIBRARY_PATH，而本栈纪律
# 明令禁止用 env 覆盖库路径（C19：会冲掉 TVM 库路径），故必须在镜像层解决。
printf '%s\n' "${CUDA_HOME_DIR}/lib64" > /etc/ld.so.conf.d/10-xmnn-cuda.conf
ldconfig
ldconfig -p | grep -m1 libcudart || true

printf '%s' "${NVCC_VERSION}" > "${MARKER}"
echo "[xmnn] cuda-nvcc: ${NVCC_VERSION} 就绪（命令: /usr/local/bin/nvcc，CUDA_HOME: ${CUDA_HOME_DIR}）"
/usr/local/bin/nvcc --version | tail -2
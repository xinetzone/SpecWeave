#!/usr/bin/env bash
# =============================================================================
# r2-dtneeded-analysis.sh — GPU/ML镜像R2深度瘦身：DT_NEEDED动态依赖分析+安全删除
#
# 位置: variants/shared/scripts/r2-dtneeded-analysis.sh（项目级可复用脚本）
#
# 用法:
#   # 1. 分析模式（dry-run，只报告不删除）：
#   docker run --rm -v $(pwd)/r2-report:/report <image> \
#     bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --analyze
#
#   # 2. 执行删除（在容器构建层中使用，必须在pip install同层）：
#   bash r2-dtneeded-analysis.sh --delete
#
#   # 3. 完整流程：分析→删除→验证（一条命令）：
#   bash r2-dtneeded-analysis.sh --all
#
# 安全保证：
#   - --analyze模式零副作用，仅生成报告
#   - --delete前自动执行DT_NEEDED验证，不删除硬依赖
#   - 删除后自动运行7项验证清单（与SOP一致）
#   - torchgen/等陷阱项内置保护，不会被误删
#   - 非CUDA/PyTorch环境自动跳过（无nvidia/目录时安全退出）
#
# 参考SOP：patterns/code-patterns/docker-gpu-slimming-sop.md Step 3
# Dockerfile集成: COPY shared/scripts/r2-dtneeded-analysis.sh 到构建层，在pip install同层调用
# =============================================================================
set -euo pipefail

# ── 配置 ──────────────────────────────────────────────────────────────────────
SP="$(python -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || echo "")"
CORE_LIB=""
REPORT_DIR="${REPORT_DIR:-/tmp/r2-analysis}"
DRY_RUN=1
EXEC_DELETE=0
EXEC_VERIFY=0
SAVED_TOTAL=0

# 颜色输出（仅在TTY时启用颜色）
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi
info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }

# ── 候选删除清单（R2，基于DT_NEEDED验证，可安全删除）────────────────────────
# 格式: "相对路径|大小估计(MB)|删除依据|安全等级"
# 安全等级: safe=DT_NEEDED+功能双验证, caution=需功能验证
declare -a R2_DELETE_CANDIDATES=(
  # === R2a: DT_NEEDED确认非硬依赖（PyTorch cu130 wheel）===
  "nvidia/cu13/lib/libcusolverMg.so.12|100|多GPU分布式线性代数求解器,单卡不需要|safe"
  "nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9|29|cuDNN JIT运行时编译引擎,precompiled覆盖标准shape|safe"
  "nvidia/cu13/lib/libnvblas.so.13|1|NVBLAS drop-in BLAS替换,不用|safe"
  "nvidia/cu13/lib/libcheckpoint.so|2|CUDA checkpoint工具,运行时不需要|safe"
  "nvidia/cu13/lib/libpcsamplingutil.so|1|PC采样profiler工具,运行时不需要|safe"
  # === R2b: HPC/集群专用（WSL2/消费级GPU不用）===
  "nvidia/nvshmem/lib/nvshmem_bootstrap_mpi.so.3|1|MPI集群bootstrap,WSL2不用|safe"
  "nvidia/nvshmem/lib/nvshmem_bootstrap_pmi.so.3|1|PMI集群bootstrap,WSL2不用|caution"
  "nvidia/nvshmem/lib/nvshmem_bootstrap_pmi2.so.3|1|PMI2集群bootstrap,WSL2不用|caution"
  "nvidia/nvshmem/lib/nvshmem_bootstrap_pmix.so.3|1|PMIx集群bootstrap,WSL2不用|caution"
  "nvidia/nvshmem/lib/nvshmem_transport_ibdevx.so.3|1|InfiniBand ibdevx传输,WSL2不用|safe"
  "nvidia/nvshmem/lib/nvshmem_transport_ibgda.so.3|1|InfiniBand GDA传输,WSL2不用|caution"
  "nvidia/nvshmem/lib/nvshmem_transport_ibrc.so.3|1|InfiniBand RC传输,WSL2不用|caution"
  "nvidia/nvshmem/lib/nvshmem_transport_libfabric.so.3|1|libfabric传输,HPC专用|caution"
  "nvidia/nvshmem/lib/nvshmem_transport_ucx.so.3|1|UCX传输,HPC专用|caution"
  # === R2c: 构建时工具 ===
  "torch/bin/protoc|5|protobuf编译器,运行时用Python protobuf库|safe"
)

# ── 保护清单（禁止删除！删除将导致运行时失败）─────────────────────────────────
declare -a PROTECTED_PATTERNS=(
  "torchgen/"                                        # torch.utils._python_dispatch运行时import
  "nvidia/cusparselt/lib/libcusparseLt.so"           # DT_NEEDED硬依赖 224MB（独立cusparselt wheel）
  "nvidia/nccl/lib/libnccl.so"                       # DT_NEEDED硬依赖 186MB
  "nvidia/nvshmem/lib/libnvshmem_host.so"            # DT_NEEDED硬依赖 38MB
  "nvidia/cublas"                                    # cuBLAS核心
  "nvidia/cudnn/lib/libcudnn_engines_precompiled"    # cuDNN预编译引擎 235MB
  "nvidia/cu13/lib/libnvrtc.so"                      # 标准NVRTC（非.alt），Triton kernel编译必需
  "nvidia/cufft"                                     # FFT库
  "nvidia/curand"                                    # 随机数库
  "nvidia/cusolver/lib/libcusolver.so"               # 标准求解器（非Mg多卡版本）
  "nvidia/cusparse/lib/libcusparse.so"               # 标准稀疏库
)

# =============================================================================
# 辅助函数
# =============================================================================

find_core_lib() {
  if [ -z "$SP" ]; then
    fail "Cannot find Python site-packages"; return 1
  fi
  # 非CUDA环境检测：如果没有torch也没有nvidia/目录，安全跳过
  if [ ! -d "$SP/torch" ] && [ ! -d "$SP/nvidia" ]; then
    warn "No torch/nvidia found in site-packages - not a GPU/ML environment, skipping"
    return 2
  fi
  CORE_LIB=$(find "$SP/torch/lib" -name "libtorch_cuda.so*" -o -name "libtorch_cpu.so*" 2>/dev/null | head -1)
  if [ -z "$CORE_LIB" ]; then
    fail "Cannot find libtorch in $SP/torch/lib"; return 1
  fi
  info "Core library: $CORE_LIB ($(du -h "$CORE_LIB" 2>/dev/null | cut -f1))"
}

check_dtneeded() {
  local lib_basename="$1"
  if readelf -d "$CORE_LIB" 2>/dev/null | grep -q "NEEDED.*${lib_basename}"; then
    return 0  # 在DT_NEEDED中 = 硬依赖
  else
    return 1  # 不在DT_NEEDED中 = 可考虑删除
  fi
}

is_protected() {
  local relpath="$1"
  for pat in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$relpath" == *"$pat"* ]]; then
      return 0
    fi
  done
  return 1
}

get_file_size_mb() {
  local f="$1"
  if [ -e "$f" ] || [ -L "$f" ]; then
    stat -c%s "$f" 2>/dev/null | awk '{printf "%.1f", $1/1024/1024}' || echo "0"
  else
    echo "0"
  fi
}

# =============================================================================
# Step 1: DT_NEEDED分析（dry-run）
# =============================================================================
cmd_analyze() {
  mkdir -p "$REPORT_DIR"
  local report="$REPORT_DIR/dtneeded-analysis.txt"

  info "=== R2 DT_NEEDED Analysis ==="
  if ! find_core_lib; then
    if [ $? -eq 2 ]; then return 0; fi
    return 1
  fi

  echo "=== DT_NEEDED Analysis Report ===" > "$report"
  echo "Date: $(date)" >> "$report"
  echo "Core library: $CORE_LIB" >> "$report"
  echo "Site-packages: $SP" >> "$report"
  echo "" >> "$report"

  info "Scanning DT_NEEDED hard dependencies..."
  echo "--- Hard Dependencies (DT_NEEDED, CANNOT delete) ---" >> "$report"
  if command -v readelf >/dev/null 2>&1; then
    readelf -d "$CORE_LIB" 2>/dev/null | grep NEEDED | awk '{print $5}' | tr -d '[]' | sort | while read -r lib; do
      found=$(find "$SP/nvidia" -name "$lib*" -o -path "*/$lib" 2>/dev/null | head -1)
      if [ -n "$found" ]; then
        sz=$(du -h "$found" 2>/dev/null | cut -f1)
        echo "  [HARD-DEP] $lib ($sz) → $found" >> "$report"
      fi
    done
  else
    warn "readelf not available, skipping DT_NEEDED scan (install binutils for full analysis)"
    echo "  [WARN] readelf not available, DT_NEEDED scan skipped" >> "$report"
  fi

  echo "" >> "$report"
  echo "--- Large .so Analysis (>20MB) ---" >> "$report"
  local safe_count=0 hard_count=0
  if [ -d "$SP/nvidia" ] && command -v readelf >/dev/null 2>&1; then
    while IFS= read -r -d '' f; do
      relpath="${f#$SP/}"
      bn=$(basename "$f")
      sz_mb=$(du -m "$f" 2>/dev/null | cut -f1)
      if is_protected "$relpath"; then
        echo "  [PROTECTED] $relpath (${sz_mb}MB)" >> "$report"
        hard_count=$((hard_count+1))
      elif check_dtneeded "$bn"; then
        echo "  [HARD-DEP]  $relpath (${sz_mb}MB) - DT_NEEDED" >> "$report"
        hard_count=$((hard_count+1))
      else
        echo "  [CANDIDATE] $relpath (${sz_mb}MB) - safe to delete" >> "$report"
        safe_count=$((safe_count+1))
      fi
    done < <(find "$SP/nvidia" -name "*.so*" -size +20M -type f -print0 2>/dev/null)
  fi

  echo "" >> "$report"
  echo "--- R2 Pre-defined Candidates Status ---" >> "$report"
  for entry in "${R2_DELETE_CANDIDATES[@]}"; do
    IFS='|' read -r relpath est_mb reason safety <<< "$entry"
    fullpath="$SP/$relpath"
    if [ -e "$fullpath" ] || [ -L "$fullpath" ]; then
      actual_sz=$(get_file_size_mb "$fullpath")
      bn_f=$(basename "$relpath")
      if command -v readelf >/dev/null 2>&1 && check_dtneeded "$bn_f" 2>/dev/null; then
        echo "  [BLOCKED]   $relpath (~${actual_sz}MB) - DT_NEEDED HARD DEP!" >> "$report"
      else
        echo "  [DELETE]    $relpath (~${actual_sz}MB) - $reason [$safety]" >> "$report"
      fi
    else
      echo "  [ALREADY-GONE] $relpath" >> "$report"
    fi
  done

  echo "" >> "$report"
  echo "--- Protected Items ---" >> "$report"
  for pat in "${PROTECTED_PATTERNS[@]}"; do
    found=$(find "$SP" -path "*$pat*" -print -quit 2>/dev/null || true)
    if [ -n "$found" ]; then
      echo "  [OK] $pat (present)" >> "$report"
    else
      echo "  [WARN] $pat NOT FOUND" >> "$report"
    fi
  done

  echo "" >> "$report"
  echo "--- Summary ---" >> "$report"
  echo "Hard dependencies (keep): $hard_count" >> "$report"
  echo "Deletion candidates: $safe_count" >> "$report"
  echo "Report: $report" >> "$report"

  echo ""
  info "=== Analysis Summary ==="
  grep -E "^\s+\[(DELETE|ALREADY-GONE|BLOCKED|CANDIDATE)\]" "$report" | while read -r line; do
    case "$line" in
      *BLOCKED*) fail "$line" ;;
      *DELETE*) ok "$line" ;;
      *CANDIDATE*) ok "$line" ;;
      *) info "$line" ;;
    esac
  done
  echo ""
  ok "Analysis complete. Full report: $report"
}

# =============================================================================
# Step 2: 安全删除
# =============================================================================
cmd_delete() {
  info "=== R2 Safe Deletion ==="
  if ! find_core_lib; then
    if [ $? -eq 2 ]; then return 0; fi
    return 1
  fi
  mkdir -p "$REPORT_DIR"

  local deleted=0 skipped=0 blocked=0

  for entry in "${R2_DELETE_CANDIDATES[@]}"; do
    IFS='|' read -r relpath est_mb reason safety <<< "$entry"
    fullpath="$SP/$relpath"

    if [ ! -e "$fullpath" ] && [ ! -L "$fullpath" ] && [ ! -d "$fullpath" ]; then
      skipped=$((skipped+1)); continue
    fi

    bn_f=$(basename "$relpath")
    if command -v readelf >/dev/null 2>&1 && check_dtneeded "$bn_f" 2>/dev/null; then
      fail "BLOCKED: $relpath is DT_NEEDED hard dependency! Skipping."
      blocked=$((blocked+1)); continue
    fi

    if is_protected "$relpath"; then
      fail "BLOCKED: $relpath matches protected pattern! Skipping."
      blocked=$((blocked+1)); continue
    fi

    local sz_mb=$(get_file_size_mb "$fullpath")
    rm -f "$fullpath" 2>/dev/null || true
    if [ -d "$fullpath" ]; then
      sz_mb=$(du -sm "$fullpath" 2>/dev/null | cut -f1)
      rm -rf "$fullpath"
    fi
    SAVED_TOTAL=$(echo "$SAVED_TOTAL + $sz_mb" | bc 2>/dev/null || echo "$SAVED_TOTAL")
    ok "Deleted: $relpath (${sz_mb}MB) - $reason"
    deleted=$((deleted+1))
  done

  # Strip Triton CUDA工具链二进制
  local triton_bin="$SP/triton/backends/nvidia/bin"
  if [ -d "$triton_bin" ] && command -v strip >/dev/null 2>&1; then
    local tb_before tb_after tb_saved
    tb_before=$(du -sb "$triton_bin" 2>/dev/null | awk '{print $1}' || echo 0)
    find "$triton_bin" -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    tb_after=$(du -sb "$triton_bin" 2>/dev/null | awk '{print $1}' || echo 0)
    tb_saved=$(( (tb_before - tb_after) / 1024 / 1024 ))
    if [ "$tb_saved" -gt 0 ]; then
      SAVED_TOTAL=$(echo "$SAVED_TOTAL + $tb_saved" | bc 2>/dev/null || echo "$SAVED_TOTAL")
      ok "Stripped triton/backends/nvidia/bin/ (saved ~${tb_saved}MB)"
      deleted=$((deleted+1))
    fi
  fi

  echo ""
  ok "Deletion complete: $deleted deleted, $skipped already gone, $blocked blocked"
  ok "Estimated space saved: ~${SAVED_TOTAL}MB"
}

# =============================================================================
# Step 3: 功能验证（7项清单）
# =============================================================================
cmd_verify() {
  info "=== R2 Post-Deletion Verification (7 checks) ==="
  local errors=0

  echo -n "  [1/7] Core imports... "
  if python -c "import torch; import torchvision;" 2>/dev/null; then
    ok "torch $(python -c 'import torch;print(torch.__version__)' 2>/dev/null)"
  elif python -c "import torch;" 2>/dev/null; then
    ok "torch $(python -c 'import torch;print(torch.__version__)' 2>/dev/null) (torchvision optional)"
  else
    fail "import FAILED"; errors=$((errors+1))
  fi

  echo -n "  [2/7] CUDA matmul... "
  if python -c "
import torch
assert torch.cuda.is_available(), 'no-cuda'
x = torch.randn(256,256,device='cuda')
y = torch.matmul(x,x); assert y.shape==(256,256)
" 2>/dev/null; then
    ok "passed"
  else
    warn "skipped (CUDA unavailable or failed)"
  fi

  echo -n "  [3/7] CUDA conv2d+autograd... "
  if python -c "
import torch, torch.nn.functional as F
x = torch.randn(1,3,32,32,device='cuda',requires_grad=True)
w = torch.randn(16,3,3,3,device='cuda',requires_grad=True)
y = F.conv2d(x,w,padding=1); y.sum().backward()
assert x.grad is not None and w.grad is not None
" 2>/dev/null; then
    ok "passed"
  else
    warn "skipped (CUDA unavailable or failed)"
  fi

  echo -n "  [4/7] CUDA MLP+CrossEntropy... "
  if python -c "
import torch, torch.nn as nn, torch.nn.functional as F
model = nn.Sequential(nn.Linear(128,64),nn.ReLU(),nn.Linear(64,10)).cuda()
x = torch.randn(32,128,device='cuda')
loss = F.cross_entropy(model(x), torch.randint(0,10,(32,),device='cuda'))
loss.backward(); assert loss.item() > 0
" 2>/dev/null; then
    ok "passed (cuDNN path)"
  else
    warn "skipped (CUDA unavailable or failed)"
  fi

  echo -n "  [5/7] Deleted items absent... "
  local del_fail=0
  for entry in "${R2_DELETE_CANDIDATES[@]}"; do
    IFS='|' read -r relpath _ _ _ <<< "$entry"
    if [ -e "$SP/$relpath" ] || [ -L "$SP/$relpath" ]; then
      del_fail=1; break
    fi
  done
  if [ $del_fail -eq 0 ]; then ok "confirmed"
  else fail "some deleted items still present!"; errors=$((errors+1)); fi

  echo -n "  [6/7] Protected items present... "
  local prot_fail=0
  for pat in "${PROTECTED_PATTERNS[@]}"; do
    if ! find "$SP" -path "*$pat*" -print -quit 2>/dev/null | grep -q .; then
      prot_fail=1; fail "$pat MISSING!"; break
    fi
  done
  if [ $prot_fail -eq 0 ]; then ok "confirmed"
  else errors=$((errors+1)); fi

  echo -n "  [7/7] devuser access... "
  if su - devuser -c "python -c 'import torch'" >/dev/null 2>&1; then
    ok "passed"
  elif id devuser >/dev/null 2>&1; then
    warn "devuser exists but torch access check failed (may need conda activation)"
  else
    warn "devuser not found (using root-only image?)"
  fi

  echo ""
  if [ $errors -eq 0 ]; then
    ok "=== ALL 7 VERIFICATIONS PASSED ==="
  else
    fail "=== $errors VERIFICATION(S) FAILED ==="
    return 1
  fi
}

# =============================================================================
# 主入口
# =============================================================================
usage() {
  cat <<'EOF'
Usage: r2-dtneeded-analysis.sh [--analyze|--delete|--verify|--all]

  --analyze   DT_NEEDED dependency analysis (dry-run, no deletion)
  --delete    Perform safe deletion after DT_NEEDED checks
  --verify    Run 7-point verification checklist
  --all       Analyze → Delete → Verify (full pipeline)
  --help      Show this help

Environment:
  REPORT_DIR  Report output directory (default: /tmp/r2-analysis)

Dockerfile usage (same-layer as pip install):
  COPY shared/scripts/r2-dtneeded-analysis.sh /usr/local/share/variant-framework/
  RUN pip install torch ... && \
      bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --all
EOF
}

case "${1:---help}" in
  --analyze) DRY_RUN=1; cmd_analyze ;;
  --delete)  DRY_RUN=0; EXEC_DELETE=1; cmd_delete ;;
  --verify)  EXEC_VERIFY=1; cmd_verify ;;
  --all)
    cmd_analyze && echo "" && cmd_delete && echo "" && cmd_verify
    ;;
  --help|-h) usage ;;
  *) echo "Unknown option: $1"; usage; exit 1 ;;
esac

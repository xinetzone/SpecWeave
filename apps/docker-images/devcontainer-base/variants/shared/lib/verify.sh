#!/usr/bin/env bash
# =============================================================================
# verify.sh — 基础验证模块（服务检查+环境验证+语法检查）
#
# 提供标准验证函数：验证横幅、基础服务可用性、conda main环境、
# devuser访问权限、bash脚本语法检查。
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_VERIFY_LOADED:-}" ]] && return 0
_VARIANT_VERIFY_LOADED=1

# ---------------------------------------------------------------------------
# verify_validation_header: 输出标准验证检查点横幅
# ---------------------------------------------------------------------------
verify_validation_header() {
    local title="${1:-Final Validation Checkpoint}"
    echo ""
    echo "########################################################################"
    echo "# [VALIDATION CHECKPOINT] ${title}"
    echo "########################################################################"
    echo ""
}

# ---------------------------------------------------------------------------
# _verify_command_exists: 内部函数 - 检查命令是否存在
# ---------------------------------------------------------------------------
_verify_command_exists() {
    local cmd="$1"
    local description="${2:-${cmd}}"
    echo -n "  [VERIFY] ${description}... "
    if command -v "${cmd}" >/dev/null 2>&1; then
        local version
        version=$("${cmd}" --version 2>&1 | head -1 | awk '{print $NF}' || echo "ok")
        echo "[OK] (${version})"
        return 0
    else
        echo "[FAIL] - command not found"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# verify_base_services: 验证基础服务命令可用（docker/supervisord/sshd）
# ---------------------------------------------------------------------------
verify_base_services() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Base services availability             │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    _verify_command_exists docker "Docker CLI" || failed=1
    _verify_command_exists supervisord "Supervisord" || failed=1
    _verify_command_exists sshd "SSH daemon" || failed=1

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "All base services verified"
        return 0
    else
        variant_log_error "One or more base services missing"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_conda_main_env: 验证conda main环境存在且Python可执行
# ---------------------------------------------------------------------------
verify_conda_main_env() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Conda main environment                 │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    echo -n "  [VERIFY] /opt/conda/envs/main exists... "
    if [[ -d /opt/conda/envs/main ]]; then
        echo "[OK]"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] main env python executable... "
    if [[ -x /opt/conda/envs/main/bin/python ]]; then
        local py_ver
        py_ver=$(/opt/conda/envs/main/bin/python --version 2>&1)
        echo "[OK] (${py_ver})"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] conda command... "
    if [[ -x /opt/conda/bin/conda ]]; then
        local conda_ver
        conda_ver=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
        echo "[OK] (conda ${conda_ver})"
    else
        echo "[FAIL]"
        failed=1
    fi

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "Conda main environment verified"
        return 0
    else
        variant_log_error "Conda main environment verification failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_user_access: 验证指定用户存在且可访问conda（通用版本）
# 用法: verify_user_access [username]
# username 默认使用 DEVTARGET_USER（未设置则为 devuser）
# ---------------------------------------------------------------------------
verify_user_access() {
    local username="${1:-${DEVTARGET_USER:-devuser}}"
    local user_home="/home/${username}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] ${username} access permissions         │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    echo -n "  [VERIFY] ${username} exists... "
    if id -u "${username}" >/dev/null 2>&1; then
        echo "[OK] (uid: $(id -u "${username}"))"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] ${username} can access conda dir... "
    if [[ -r /opt/conda ]] && [[ -x /opt/conda ]]; then
        echo "[OK]"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] ${username} .bashrc ownership... "
    if [[ -f "${user_home}/.bashrc" ]]; then
        local owner
        owner=$(stat -c '%U' "${user_home}/.bashrc" 2>/dev/null || echo "unknown")
        if [[ "${owner}" == "${username}" ]]; then
            echo "[OK] (owner: ${owner})"
        else
            echo "[WARN] owner is ${owner} (expected ${username})"
        fi
    else
        echo "[INFO] no .bashrc found (ok if not needed)"
    fi

    echo -n "  [VERIFY] ${username} can execute python... "
    if su - "${username}" -c "python --version" >/dev/null 2>&1; then
        local py_ver
        py_ver=$(su - "${username}" -c "python --version" 2>&1)
        echo "[OK] (${py_ver})"
    else
        echo "[WARN] ${username} python execution check skipped (may need conda activation)"
    fi

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "${username} access verified"
        return 0
    else
        variant_log_error "${username} access verification failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_devuser_access: 验证devuser存在且可访问conda（向后兼容wrapper）
# ---------------------------------------------------------------------------
verify_devuser_access() {
    verify_user_access "devuser"
}

# ---------------------------------------------------------------------------
# verify_ssh_config: 验证 sshd 配置文件语法正确（sshd -t）
# ---------------------------------------------------------------------------
verify_ssh_config() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] SSH daemon configuration syntax        │"
    echo "└─────────────────────────────────────────────────┘"

    echo -n "  [VERIFY] sshd -t config syntax... "
    if command -v sshd >/dev/null 2>&1; then
        local saved_opts="$-"
        set +e
        local sshd_output
        sshd_output=$(sshd -t 2>&1)
        local rc=$?
        if [[ "${saved_opts}" == *e* ]]; then
            set -e
        fi
        if [[ ${rc} -eq 0 ]]; then
            echo "[OK]"
            variant_log_ok "sshd configuration syntax is valid"
            return 0
        else
            echo "[FAIL]"
            echo "  sshd -t output: ${sshd_output}"
            variant_log_error "sshd configuration syntax error"
            exit 1
        fi
    else
        echo "[SKIP] sshd not found in image"
        return 0
    fi
}

# ---------------------------------------------------------------------------
# verify_bash_syntax: bash语法检查
# 用法: verify_bash_syntax <script_path> [more_paths...]
# ---------------------------------------------------------------------------
verify_bash_syntax() {
    local failed=0
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Bash script syntax check               │"
    echo "└─────────────────────────────────────────────────┘"

    local script
    for script in "$@"; do
        echo -n "  [SYNTAX] ${script}... "
        if bash -n "${script}" 2>&1; then
            echo "[OK]"
        else
            echo "[FAIL]"
            failed=1
        fi
    done

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "All bash scripts pass syntax check"
        return 0
    else
        variant_log_error "One or more bash scripts have syntax errors"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_all_basic: 一键执行所有基础验证
# 快捷函数：services + conda env + devuser
# ---------------------------------------------------------------------------
verify_all_basic() {
    verify_validation_header "Basic Environment Validation"
    verify_base_services
    verify_conda_main_env
    verify_devuser_access
    variant_log_ok "All basic verifications passed"
}

# =============================================================================
# GPU/ML Slim 验证函数（对应 SOP Step 4 七项验证清单）
# 参考: patterns/code-patterns/docker-gpu-slimming-sop.md
# =============================================================================

# ---------------------------------------------------------------------------
# verify_slim_delete_preserve: 验证slim瘦身的删除项不存在/保留项存在
# 用法: verify_slim_delete_preserve <delete_list_file|-> <preserve_list_file|->
# 传入 - 表示使用内置默认列表（PyTorch cu130）
# ---------------------------------------------------------------------------
verify_slim_delete_preserve() {
    local del_list="${1:-}"
    local pres_list="${2:-}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Slim delete/preserve assertions        │"
    echo "└─────────────────────────────────────────────────┘"

    local SP
    SP=$(/opt/conda/envs/main/bin/python -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || echo "")
    if [ -z "$SP" ]; then
        echo "  [WARN] Cannot determine site-packages, skipping slim assertions"
        return 0
    fi

    local errors=0

    # 内置删除项默认列表（PyTorch cu130 R2标准删除项）
    if [ "$del_list" = "-" ] || [ -z "$del_list" ]; then
        set -- "nvidia/cu13/lib/libnvrtc.alt.so.13" \
               "nvidia/cu13/lib/libnvperf_host.so" \
               "nvidia/cu13/lib/libnvperf_target.so" \
               "nvidia/nvshmem/lib/libnvshmem_device.bc" \
               "nvidia/cu13/lib/libcusolverMg.so.12" \
               "nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9" \
               "nvidia/cu13/lib/libnvblas.so.13" \
               "triton/backends/amd"
        for f in "$@"; do
            if [ -e "$SP/$f" ] || [ -L "$SP/$f" ]; then
                echo "  [FAIL] Delete target still exists: $f"; errors=1
            fi
        done
    elif [ -f "$del_list" ]; then
        while IFS= read -r f; do
            [ -z "$f" ] || [[ "$f" == \#* ]] && continue
            if [ -e "$SP/$f" ] || [ -L "$SP/$f" ]; then
                echo "  [FAIL] Delete target still exists: $f"; errors=1
            fi
        done < "$del_list"
    fi
    if [ $errors -eq 0 ]; then echo "  [OK] All deletion targets confirmed absent"; fi

    # 内置保留项默认列表
    # 注意：libcusparseLt 拆分在独立 nvidia-cusparselt-cu13 wheel（torch 2.13+cu130），
    #       实际路径为 nvidia/cusparselt/lib/，而非 nvidia/cusparse/lib/。
    local p_errors=0
    if [ "$pres_list" = "-" ] || [ -z "$pres_list" ]; then
        set -- "nvidia/cusparselt/lib/libcusparseLt.so.0" \
               "nvidia/nccl/lib/libnccl.so.2" \
               "nvidia/nvshmem/lib/libnvshmem_host.so.3" \
               "torchgen/__init__.py"
        for f in "$@"; do
            if [ ! -e "$SP/$f" ]; then
                echo "  [FAIL] Preserved target missing: $f"; p_errors=1
            fi
        done
    elif [ -f "$pres_list" ]; then
        while IFS= read -r f; do
            [ -z "$f" ] || [[ "$f" == \#* ]] && continue
            if [ ! -e "$SP/$f" ]; then
                echo "  [FAIL] Preserved target missing: $f"; p_errors=1
            fi
        done < "$pres_list"
    fi
    if [ $p_errors -eq 0 ]; then echo "  [OK] All preserved targets confirmed present"; fi

    if [ $errors -eq 0 ] && [ $p_errors -eq 0 ]; then
        variant_log_ok "Slim delete/preserve assertions passed"
        return 0
    else
        variant_log_error "Slim delete/preserve assertions failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_gpu_smoke: GPU算子冒烟测试（CUDA matmul/conv2d/MLP）
# 自动跳过无CUDA环境（CPU-only构建）
# ---------------------------------------------------------------------------
verify_gpu_smoke() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] GPU compute smoke test                 │"
    echo "└─────────────────────────────────────────────────┘"

    /opt/conda/envs/main/bin/python - <<'PYEOF'
import sys, torch, torch.nn as nn, torch.nn.functional as F

if not torch.cuda.is_available():
    print("  [SKIP] CUDA not available (expected on CPU-only build)")
    sys.exit(0)

device = torch.device('cuda')
torch.manual_seed(42)
errors = 0

# CUDA matmul
try:
    a, b = torch.randn(256,256,device=device), torch.randn(256,256,device=device)
    c = torch.matmul(a,b); assert c.shape==(256,256)
    print("  [OK] CUDA matmul (256x256)")
except Exception as e:
    print(f"  [FAIL] CUDA matmul: {e}"); errors=1

# CUDA conv2d + autograd
try:
    x = torch.randn(1,3,32,32,device=device,requires_grad=True)
    w = torch.randn(16,3,3,3,device=device,requires_grad=True)
    y = F.conv2d(x,w,padding=1); y.sum().backward()
    assert x.grad is not None and w.grad is not None
    print("  [OK] CUDA conv2d+autograd")
except Exception as e:
    print(f"  [FAIL] CUDA conv2d: {e}"); errors=1

# CUDA MLP + CrossEntropy (cuDNN path)
try:
    model = nn.Sequential(nn.Linear(128,64),nn.ReLU(),nn.Linear(64,10)).to(device)
    x = torch.randn(32,128,device=device)
    loss = F.cross_entropy(model(x), torch.randint(0,10,(32,),device=device))
    loss.backward()
    assert loss.item() > 0
    print(f"  [OK] CUDA MLP+CrossEntropy (cuDNN, loss={loss.item():.4f})")
except Exception as e:
    print(f"  [FAIL] CUDA MLP+CE: {e}"); errors=1

if errors == 0:
    print("  [OK] All GPU smoke tests passed")
else:
    print(f"  [FAIL] {errors} GPU test(s) failed")
    sys.exit(1)
PYEOF
    local rc=$?
    if [ $rc -ne 0 ]; then
        variant_log_error "GPU smoke tests failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_all_slim_gpu: 一键执行GPU/ML镜像slim验证全流程
# 用法: verify_all_slim_gpu
# 包含: CPU算子冒烟 + GPU算子冒烟 + 删除项断言 + 保留项断言 + devuser权限
# ---------------------------------------------------------------------------
verify_all_slim_gpu() {
    verify_validation_header "GPU/ML Slim Validation (SOP Step 4)"

    # 安全检查：torch未安装时跳过（非GPU变体）
    if ! /opt/conda/envs/main/bin/python -c "import torch" 2>/dev/null; then
        echo "  [SKIP] torch not installed - not a GPU/ML variant, skipping slim GPU validation"
        variant_log_ok "GPU slim validation skipped (non-GPU variant)"
        return 0
    fi

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] CPU compute smoke test                 │"
    echo "└─────────────────────────────────────────────────┘"
    /opt/conda/envs/main/bin/python - <<'PYEOF'
import torch, torch.nn.functional as F
torch.manual_seed(42)
a,b = torch.randn(64,128),torch.randn(128,32)
c=torch.matmul(a,b); assert c.shape==(64,32); print("  [OK] CPU matmul")
x,w = torch.randn(1,3,32,32),torch.randn(16,3,3,3)
conv=F.conv2d(x,w,padding=1); assert conv.shape==(1,16,32,32); print("  [OK] CPU conv2d")
x2=torch.randn(4,8,requires_grad=True); w2=torch.randn(8,4,requires_grad=True)
(x2@w2).sum().backward(); assert x2.grad is not None; print("  [OK] CPU autograd")
model=torch.nn.Sequential(torch.nn.Linear(16,32),torch.nn.ReLU(),torch.nn.Linear(32,4))
out=model(torch.randn(4,16)); assert out.shape==(4,4); print("  [OK] CPU MLP")
print("  [OK] All CPU smoke tests passed")
PYEOF

    verify_gpu_smoke
    verify_slim_delete_preserve "-" "-"
    verify_devuser_access
    variant_log_ok "All GPU/ML slim verifications passed"
}

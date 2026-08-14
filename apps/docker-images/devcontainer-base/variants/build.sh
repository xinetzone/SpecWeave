#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "${SCRIPT_DIR}/shared/lib/logging.sh"
LOG_SERVICE="devcontainer-variants-build"
LOG_JSON_OUTPUT="/tmp/devcontainer-variants-events.jsonl"

VARIANTS=(
    "conda-llvm|conda+LLVM/clang编译工具链||/opt/conda/bin/llvm-config --version|||/opt/conda/bin/clang --version|||/opt/conda/bin/clang++ --version|||/opt/conda/bin/cmake --version|||/opt/conda/bin/ninja --version"
    "onnx-dev|conda-llvm + 纯ONNX生态(onnx/onnxruntime/onnx-simplifier/onnxscript,无PyTorch;onnxoptimizer因free-threading不兼容而排除)|conda-llvm|/opt/conda/envs/main/bin/python -c \"import onnx,onnxruntime,onnxsim,onnxscript;print('onnx-dev ecosystem OK')\"|||/opt/conda/envs/main/bin/python -c \"import sys;assert sys._is_gil_enabled() is False;print('free-threading OK')\"|||/opt/conda/envs/main/bin/python -c \"import importlib.util as u;assert u.find_spec('torch') is None and u.find_spec('torchvision') is None and u.find_spec('onnxoptimizer') is None;print('torch/onnxoptimizer absent OK')\""
    "onnx-pytorch|conda-llvm + PyTorch CPU + ONNX 深度学习运行时|conda-llvm|/opt/conda/bin/python -c \"import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)\"|||/opt/conda/bin/python -c \"import torch;assert torch.cuda.is_available() is False\"|||/opt/conda/bin/python -c \"import sys;assert sys._is_gil_enabled() is True;print('GIL enabled OK')\"|||/opt/conda/bin/python -c \"import onnxsim,onnxoptimizer,onnxscript;print('onnx ecosystem OK')\""
    "onnx-quantized|onnx-dev + ONNX量化工具链(INT8/FP16动态/静态量化,纯ONNX无PyTorch,free-threading main环境;neural-compressor可选需自装torch)|onnx-dev|/opt/conda/envs/main/bin/python -c \"from onnxruntime.quantization import quantize_dynamic,quantize_static,QuantType,QuantFormat,CalibrationDataReader;print('quantization API OK')\"|||/opt/conda/envs/main/bin/python -c \"from onnxconverter_common import float16;print('float16 conversion OK')\"|||/opt/conda/envs/main/bin/python -c \"import onnxruntime.quantization.shape_inference;print('shape_inference OK')\"|||/opt/conda/envs/main/bin/python -c \"import importlib.util as u,sys;assert u.find_spec('torch') is None and u.find_spec('onnxoptimizer') is None;print('torch/onnxoptimizer absent OK')\""
    "ai-dev|onnx-quantized + 完整AI/ML/NLP全栈Python生态(50+包)+JupyterLab4.x+AI内核|onnx-quantized|/opt/conda/bin/python -c \"import transformers,datasets,fastapi,pandas;print('ai-dev core OK')\"|||/opt/conda/bin/python -c \"import matplotlib,seaborn,rich,typer;print('viz/cli OK')\"|||/opt/conda/bin/python -c \"import jieba,nltk,fitz,openpyxl;print('nlp/document OK')\"|||/opt/conda/bin/python -c \"import psycopg2,pymongo,elasticsearch,minio;print('database OK')\"|||/opt/conda/bin/python -c \"from onnxruntime.quantization import quantize_dynamic;print('quantization inherited OK')\"|||test -f /opt/conda/share/jupyter/kernels/ai-dev/kernel.json && echo 'kernel registered'"
)

declare -A VARIANT_DESC
declare -A VARIANT_DEPS
declare -A VARIANT_VALIDATE

LIST_MODE=false
BUILD_ALL=false
NO_CACHE=""
APT_MIRROR="official"
CONDA_MIRROR="official"
PIP_MIRROR="official"
TAG="latest"
declare -a SELECTED_VARIANTS=()
declare -a EXTRA_BUILD_ARGS=()

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build devcontainer-base variant Docker images.

Options:
  -l, --list                 List all available variants with descriptions and dependencies
  -v, --variant <name>       Build specified variant (can be specified multiple times)
  -a, --all                  Build all variants in dependency order
  --no-cache                 Disable Docker build cache
  --cn                       Use China mirrors (apt: aliyun, conda: tuna, pip: aliyun)
  --build-arg KEY=VALUE      Pass custom build argument to docker build (can be used multiple times)
  -t, --tag TAG              Image tag suffix (default: latest, produces devcontainer-base:<variant>-<TAG>)
  -h, --help                 Show this help message

Available variants:
EOF

    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name desc deps validate <<< "$entry"
        echo "  $name"
        echo "      $desc"
        if [ -n "$deps" ]; then
            echo "      依赖: $deps"
        fi
        echo ""
    done

    cat << EOF
Examples:
  $0 --list                                   # List all variants
  $0 --variant conda                          # Build conda variant only
  $0 --all --cn                               # Build all variants with China mirrors
  $0 -v conda-llvm --no-cache -t dev          # Build conda-llvm without cache, tag as dev
  $0 -a --build-arg EXTRA_TOOLS=yes           # Build all with extra build arg
EOF
}

validate_delimiter_convention() {
    local errors=0
    local entry_num=0

    echo ""
    log_step "[CONVENTION CHECK] Validating ||| delimiter convention in VARIANTS array"

    for entry in "${VARIANTS[@]}"; do
        entry_num=$((entry_num + 1))

        local normalized_entry="${entry//|||/§§§}"
        local field_count
        field_count=$(awk -F'|' '{print NF}' <<< "$normalized_entry")

        if [ "$field_count" -ne 4 ]; then
            log_error "Entry #${entry_num}: Invalid field count (expected 4, got ${field_count})"
            log_error "  → Check if '|||' was accidentally written as '|' (single pipe) in validate commands"
            log_error "  → Entry: $entry"
            errors=$((errors + 1))
            continue
        fi

        local normalized_for_parse="${entry//|||/§§§}"
        IFS='|' read -r name desc deps validate_placeholder <<< "$normalized_for_parse"
        local validate="${validate_placeholder//§§§/|||}"

        if [ -z "$name" ]; then
            log_error "Entry #${entry_num}: Variant name cannot be empty"
            errors=$((errors + 1))
        fi

        if [ -z "$validate" ]; then
            log_warn "Entry '${name}': No validation commands defined"
        else
            local cmd_count=0
            local _remaining="$validate"

            if [[ "$_remaining" == *";"* ]] && [[ "$_remaining" != *'"'* ]]; then
                log_warn "Entry '${name}': Semicolon detected outside quoted strings - verify this is not a command separator"
                log_warn "  → Use '|||' (triple pipe) to separate multiple validation commands"
                log_warn "  → Validate field: $validate"
            fi

            while [[ "$_remaining" == *"|||"* ]]; do
                local cmd_part="${_remaining%%|||*}"
                cmd_part=$(echo "$cmd_part" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [ -n "$cmd_part" ]; then
                    cmd_count=$((cmd_count + 1))
                else
                    log_error "Entry '${name}': Empty command segment between '|||' separators"
                    errors=$((errors + 1))
                fi
                _remaining="${_remaining#*|||}"
            done
            _remaining=$(echo "$_remaining" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            if [ -n "$_remaining" ]; then
                cmd_count=$((cmd_count + 1))
            fi

            if [ $cmd_count -eq 0 ]; then
                log_error "Entry '${name}': Validate field has no non-empty commands"
                errors=$((errors + 1))
            else
                log_info "Entry '${name}': ${cmd_count} validation command(s), convention OK"
            fi
        fi
    done

    echo ""
    if [ $errors -gt 0 ]; then
        log_error "[CONVENTION CHECK] FAILED with ${errors} error(s). Please fix VARIANTS array before building."
        return 1
    else
        log_ok "[CONVENTION CHECK] PASSED for all ${entry_num} variant(s)"
        return 0
    fi
}

parse_variants() {
    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name desc deps validate <<< "$entry"
        VARIANT_DESC["$name"]="$desc"
        VARIANT_DEPS["$name"]="$deps"
        VARIANT_VALIDATE["$name"]="$validate"
    done
}

list_variants() {
    log_step "Available variants"
    echo ""
    printf "%-20s %-35s %s\n" "VARIANT" "DESCRIPTION" "DEPENDENCIES"
    printf "%-20s %-35s %s\n" "-------" "-----------" "------------"
    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name desc deps validate <<< "$entry"
        if [ -z "$deps" ]; then
            deps="(none)"
        fi
        printf "%-20s %-35s %s\n" "$name" "$desc" "$deps"
    done
    echo ""
}

variant_exists() {
    local check_name="$1"
    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name _ _ _ <<< "$entry"
        if [ "$name" = "$check_name" ]; then
            return 0
        fi
    done
    return 1
}

topological_sort() {
    local -a requested=("$@")
    local -A in_degree
    local -A adj
    local -a sorted=()
    local -a queue=()
    local -A needed

    for v in "${requested[@]}"; do
        needed["$v"]=1
    done

    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name _ deps_str _ <<< "$entry"
        if [ -z "${needed[$name]}" ]; then
            continue
        fi
        in_degree["$name"]=0
        if [ -n "$deps_str" ]; then
            IFS=',' read -ra deps <<< "$deps_str"
            for dep in "${deps[@]}"; do
                needed["$dep"]=1
                # 依赖节点的 VARIANTS 条目可能已在本循环中被跳过（当时 needed 尚未
                # 标记该依赖），因此其 in_degree 可能未被初始化。此处补齐默认值 0，
                # 确保依赖节点能正确进入构建队列。
                if [ -z "${in_degree[$dep]:-}" ]; then
                    in_degree["$dep"]=0
                fi
                adj["$dep"]="${adj[$dep]:-} $name"
                in_degree["$name"]=$((in_degree["$name"] + 1))
            done
        fi
    done

    for name in "${!in_degree[@]}"; do
        if [ "${in_degree[$name]}" -eq 0 ]; then
            queue+=("$name")
        fi
    done

    while [ ${#queue[@]} -gt 0 ]; do
        local current="${queue[0]}"
        queue=("${queue[@]:1}")
        sorted+=("$current")
        if [ -n "${adj[$current]}" ]; then
            for neighbor in ${adj[$current]}; do
                in_degree["$neighbor"]=$((in_degree["$neighbor"] - 1))
                if [ "${in_degree[$neighbor]}" -eq 0 ]; then
                    queue+=("$neighbor")
                fi
            done
        fi
    done

    echo "${sorted[@]}"
}

check_dependency_image() {
    local variant="$1"
    local deps_str="${VARIANT_DEPS[$variant]}"

    if [ -z "$deps_str" ]; then
        local base_image="devcontainer-base:${TAG}"
        if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${base_image}$"; then
            log_error "基础镜像不存在: ${base_image}"
            log_error "请先构建基础镜像: bash scripts/build.sh --tag ${TAG}"
            return 1
        fi
        return 0
    fi

    IFS=',' read -ra deps <<< "$deps_str"
    for dep in "${deps[@]}"; do
        local dep_image="devcontainer-base:${dep}-${TAG}"
        if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${dep_image}$"; then
            log_error "依赖镜像不存在: ${dep_image}"
            log_error "请先构建依赖变体: bash variants/build.sh --variant ${dep} --tag ${TAG}"
            return 1
        fi
    done
    return 0
}

get_base_tag() {
    echo "${TAG}"
}

parse_timer_logs() {
    local log_file="$1"
    local variant="$2"
    
    echo ""
    log_step "[TIMER ANALYSIS] Parsing build stage timings from log: $log_file"
    
    local -a timer_lines
    mapfile -t timer_lines < <(grep '\[TIMER\]' "$log_file" 2>/dev/null || true)
    
    if [ ${#timer_lines[@]} -eq 0 ]; then
        log_warn "No [TIMER] markers found in build log"
        return 0
    fi
    
    echo ""
    printf "%-60s %s\n" "STAGE TIMING" "DURATION"
    printf "%-60s %s\n" "------------------------------------------------------------" "--------"
    
    local stage_num=0
    local total_variant_time=0
    
    for line in "${timer_lines[@]}"; do
        local stage_desc
        local duration
        
        if echo "$line" | grep -q "took"; then
            stage_desc=$(echo "$line" | sed 's/.*\[TIMER\] //' | sed 's/ took.*//')
            duration=$(echo "$line" | grep -oP 'took \K[0-9]+s' || echo "N/A")
            # 仅当 duration 是纯数字时长（如 42s）时才累加；否则（N/A）跳过，
            # 避免对非数字做算术运算触发 set -e 的算术求值错误（division by 0），
            # 该错误会导致 build_variant 异常返回、主循环中断而跳过后续变体构建。
            if [[ "$duration" =~ ^[0-9]+s$ ]]; then
                total_variant_time=$((total_variant_time + ${duration%s}))
            fi
            stage_num=$((stage_num + 1))
            printf "%-60s %s\n" "S${stage_num}: $stage_desc" "$duration"
        elif echo "$line" | grep -q "started at"; then
            stage_desc=$(echo "$line" | sed 's/.*\[TIMER\] //' | sed 's/ at.*//')
            printf "%-60s %s\n" "EVENT: $stage_desc" "---"
        elif echo "$line" | grep -q "Build duration"; then
            duration=$(echo "$line" | grep -oP 'Build duration: \K[0-9]+s' || echo "N/A")
            printf "%-60s %s\n" "TOTAL (build_variant wrapper):" "$duration"
        fi
    done
    
    if [ $stage_num -gt 0 ]; then
        printf "%-60s %s\n" "------------------------------------------------------------" "--------"
        printf "%-60s %ds\n" "SUM (stages with 'took' marker):" "$total_variant_time"
    fi
    
    echo ""
}

build_variant() {
    local variant="$1"
    local variant_dir="${SCRIPT_DIR}/${variant}"
    local image_name="devcontainer-base:${variant}-${TAG}"
    local base_tag
    base_tag="$(get_base_tag "$variant")"
    local log_timestamp
    log_timestamp=$(date +%Y%m%d-%H%M%S)
    local log_file="/tmp/variants-build-${variant}-${log_timestamp}.log"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    === BUILD START: ${variant} ==="
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    log_step "Building variant: ${variant}"
    log_info "Description:   ${VARIANT_DESC[$variant]}"
    log_info "Image:         ${image_name}"
    log_info "Base tag:      ${base_tag}"
    log_info "Context:       ${variant_dir}"
    log_info "Log file:      ${log_file}"
    log_info "APT mirror:    ${APT_MIRROR}"
    log_info "Conda mirror:  ${CONDA_MIRROR}"
    log_info "PIP mirror:    ${PIP_MIRROR}"
    if [ -n "$NO_CACHE" ]; then log_info "Cache:         disabled"; fi
    echo ""

    if [ ! -d "$variant_dir" ]; then
        log_error "Variant directory not found: ${variant_dir}"
        return 1
    fi

    if ! check_dependency_image "$variant"; then
        return 1
    fi

    local -a build_args=(
        --build-arg APT_MIRROR="${APT_MIRROR}"
        --build-arg CONDA_MIRROR="${CONDA_MIRROR}"
        --build-arg PIP_MIRROR="${PIP_MIRROR}"
        --build-arg BASE_TAG="${base_tag}"
        --build-arg BUILDKIT_INLINE_CACHE=1
    )

    for extra_arg in "${EXTRA_BUILD_ARGS[@]}"; do
        build_args+=(--build-arg "$extra_arg")
    done

    BUILD_START=$(date +%s)
    log_event "variant_build_start" "variant=$variant" "image=$image_name" "log_file=$log_file"

    echo ""
    log_info "Starting docker build with --progress=plain, output to: $log_file"
    echo ""

    set +e
    DOCKER_BUILDKIT=1 docker build \
        --progress=plain \
        --file "${variant_dir}/Dockerfile" \
        ${NO_CACHE} \
        "${build_args[@]}" \
        -t "${image_name}" \
        "${SCRIPT_DIR}" 2>&1 | tee "$log_file"
    local build_exit_code=${PIPESTATUS[0]}
    set -e

    BUILD_END=$(date +%s)
    BUILD_DURATION=$((BUILD_END - BUILD_START))
    log_metric "variant_build_duration_seconds" "$BUILD_DURATION" "seconds"

    # 将总耗时追加到日志文件，确保 parse_timer_logs 能解析到
    echo "[TIMER] Build duration: ${BUILD_DURATION}s" >> "$log_file"

    if [ $build_exit_code -ne 0 ]; then
        echo ""
        log_error "Build failed for ${image_name} (exit code: $build_exit_code)"
        log_error "See full log at: $log_file"
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║                    === BUILD END: ${variant} (FAILED) ==="
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
        return 1
    fi

    parse_timer_logs "$log_file" "$variant"

    echo ""
    log_ok "Build complete: ${image_name}"
    IMAGE_SIZE=$(docker images --format '{{.Size}}' "${image_name}" | head -1)
    log_info "[TIMER] Build duration: ${BUILD_DURATION}s"
    log_info "Image size: ${IMAGE_SIZE}"
    log_info "Build log saved to: $log_file"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    === BUILD END: ${variant} (SUCCESS) ==="
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    return 0
}

validate_variant() {
    local variant="$1"
    local image_name="devcontainer-base:${variant}-${TAG}"
    local validate_cmds="${VARIANT_VALIDATE[$variant]}"
    local validate_result=0
    local pass_count=0
    local fail_count=0
    local total_count=0
    local VALIDATE_TIMEOUT=60

    echo ""
    log_step "[VALIDATION] Validating variant: ${variant}"
    log_info "Image: ${image_name}"
    log_info "Timeout per command: ${VALIDATE_TIMEOUT}s"

    if [ -z "$validate_cmds" ]; then
        log_warn "No validation command defined for ${variant}, skipping"
        echo "VALIDATE_COUNTS=0/0 PASS"
        return 0
    fi

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│  Running individual validation checks            │"
    echo "└─────────────────────────────────────────────────┘"
    echo ""

    local cmds=()
    local _remaining="$validate_cmds"
    while [[ "$_remaining" == *"|||"* ]]; do
        cmds+=("${_remaining%%|||*}")
        _remaining="${_remaining#*|||}"
    done
    cmds+=("$_remaining")
    local cmd_num=0
    
    for cmd in "${cmds[@]}"; do
        cmd=$(echo "$cmd" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -z "$cmd" ]; then
            continue
        fi
        cmd_num=$((cmd_num + 1))
        total_count=$((total_count + 1))
        
        printf "  [CHECK %d/%d] %s ... " "$cmd_num" "${#cmds[@]}" "$cmd"
        
        set +e
        local cmd_output
        local cmd_exit
        if command -v timeout >/dev/null 2>&1; then
            cmd_output=$(timeout "$VALIDATE_TIMEOUT" docker run --rm "${image_name}" bash -c "$cmd" 2>&1)
            cmd_exit=$?
        else
            cmd_output=$(docker run --rm "${image_name}" bash -c "$cmd" 2>&1)
            cmd_exit=$?
        fi
        set -e
        
        if [ $cmd_exit -eq 0 ]; then
            echo -e "\033[0;32mPASS\033[0m"
            pass_count=$((pass_count + 1))
        else
            if [ $cmd_exit -eq 124 ]; then
                echo -e "\033[0;31mTIMEOUT\033[0m (after ${VALIDATE_TIMEOUT}s)"
            else
                echo -e "\033[0;31mFAIL\033[0m (exit code: $cmd_exit)"
            fi
            fail_count=$((fail_count + 1))
            validate_result=1
            echo "    Output: $cmd_output" | head -5
        fi
    done

    echo ""
    printf "  Verification result: %d/%d PASS\n" "$pass_count" "$total_count"
    
    if [ $fail_count -eq 0 ]; then
        echo ""
        log_ok "[VALIDATION] ${variant} validation passed: ${pass_count}/${total_count} checks"
    else
        echo ""
        log_error "[VALIDATION] ${variant} validation failed: ${fail_count}/${total_count} checks failed"
    fi

    echo "VALIDATE_COUNTS=${pass_count}/${total_count}"
    return $validate_result
}

eval "$(log_parse_args "$@")"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -l|--list)
            LIST_MODE=true
            shift
            ;;
        -v|--variant)
            if [ -z "$2" ]; then
                log_error "--variant requires a name argument"
                usage
                exit 1
            fi
            SELECTED_VARIANTS+=("$2")
            shift 2
            ;;
        -a|--all)
            BUILD_ALL=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --cn)
            APT_MIRROR="aliyun"
            CONDA_MIRROR="tuna"
            PIP_MIRROR="aliyun"
            shift
            ;;
        --build-arg)
            if [ -z "$2" ]; then
                log_error "--build-arg requires KEY=VALUE argument"
                usage
                exit 1
            fi
            EXTRA_BUILD_ARGS+=("$2")
            shift 2
            ;;
        -t|--tag)
            if [ -z "$2" ]; then
                log_error "--tag requires a TAG argument"
                usage
                exit 1
            fi
            TAG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

parse_variants

if ! validate_delimiter_convention; then
    exit 1
fi

if $LIST_MODE; then
    list_variants
    exit 0
fi

if ! $BUILD_ALL && [ ${#SELECTED_VARIANTS[@]} -eq 0 ]; then
    log_error "No variants specified. Use --list to see available variants, --variant to specify, or --all to build all."
    echo ""
    usage
    exit 1
fi

if $BUILD_ALL; then
    for entry in "${VARIANTS[@]}"; do
        IFS='|' read -r name _ _ _ <<< "$entry"
        SELECTED_VARIANTS+=("$name")
    done
fi

for v in "${SELECTED_VARIANTS[@]}"; do
    if ! variant_exists "$v"; then
        log_error "Unknown variant: $v"
        log_error "Use --list to see available variants"
        exit 1
    fi
done

BUILD_ORDER=($(topological_sort "${SELECTED_VARIANTS[@]}"))

log_step "Build plan"
log_info "Build order: ${BUILD_ORDER[*]}"
log_info "Tag suffix:  ${TAG}"
echo ""

TOTAL_START=$(date +%s)
BUILD_PASS=0
BUILD_FAIL=0
declare -a BUILD_RESULTS=()
declare -A BUILD_DURATIONS
declare -A BUILD_SIZES
declare -A VALIDATION_COUNTS

for variant in "${BUILD_ORDER[@]}"; do
    VARIANT_START=$(date +%s)
    if build_variant "$variant"; then
        VARIANT_END=$(date +%s)
        VARIANT_DURATION=$((VARIANT_END - VARIANT_START))
        image_name="devcontainer-base:${variant}-${TAG}"
        IMAGE_SIZE=$(docker images --format '{{.Size}}' "${image_name}" | head -1)
        BUILD_DURATIONS["$variant"]=$VARIANT_DURATION
        BUILD_SIZES["$variant"]="$IMAGE_SIZE"
        BUILD_PASS=$((BUILD_PASS + 1))
        BUILD_RESULTS+=("${variant}:PASS")
    else
        BUILD_FAIL=$((BUILD_FAIL + 1))
        BUILD_RESULTS+=("${variant}:FAIL")
        VALIDATION_COUNTS["$variant"]="SKIPPED"
        log_error "Failed to build variant: ${variant}"
        break
    fi
done

VALIDATION_PASS=0
VALIDATION_FAIL=0

if [ $BUILD_FAIL -eq 0 ]; then
    echo ""
    log_step "Running validation for all built variants"
    for variant in "${BUILD_ORDER[@]}"; do
        local_validate_output=$(mktemp)
        if validate_variant "$variant" | tee "$local_validate_output"; then
            VALIDATION_PASS=$((VALIDATION_PASS + 1))
        else
            VALIDATION_FAIL=$((VALIDATION_FAIL + 1))
        fi
        counts=$(grep '^VALIDATE_COUNTS=' "$local_validate_output" | tail -1 | cut -d= -f2)
        if [ -n "$counts" ]; then
            VALIDATION_COUNTS["$variant"]="$counts PASS"
        else
            VALIDATION_COUNTS["$variant"]="N/A"
        fi
        rm -f "$local_validate_output"
    done
fi

TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

echo ""
log_step "Build summary"
echo ""
printf "%-15s %-10s %-12s %-10s %s\n" "VARIANT" "STATUS" "SIZE" "DURATION" "VERIFICATION COUNTS"
printf "%-15s %-10s %-12s %-10s %s\n" "-------" "------" "----" "--------" "--------------------"

for variant in "${BUILD_ORDER[@]}"; do
    status="PASS"
    size="${BUILD_SIZES[$variant]:-N/A}"
    duration="${BUILD_DURATIONS[$variant]:-N/A}s"
    validation_counts="${VALIDATION_COUNTS[$variant]:-SKIPPED}"

    for result in "${BUILD_RESULTS[@]}"; do
        IFS=':' read -r rname rstatus <<< "$result"
        if [ "$rname" = "$variant" ]; then
            status="$rstatus"
            break
        fi
    done

    if [ "$status" != "PASS" ]; then
        validation_counts="SKIPPED"
    fi

    printf "%-15s %-10s %-12s %-10s %s\n" "$variant" "$status" "$size" "$duration" "$validation_counts"
done

echo ""
log_info "Total variants built: ${BUILD_PASS}"
log_info "Total duration: ${TOTAL_DURATION}s"
log_info "[TIMER] Total build time: ${TOTAL_DURATION}s"

log_event "build_complete" "total=${#BUILD_ORDER[@]}" "passed=$BUILD_PASS" "failed=$BUILD_FAIL" "duration=$TOTAL_DURATION"

if [ $BUILD_FAIL -gt 0 ] || [ $VALIDATION_FAIL -gt 0 ]; then
    log_summary "$BUILD_PASS" "$((BUILD_FAIL + VALIDATION_FAIL))" "${#BUILD_ORDER[@]}" "$TOTAL_DURATION" "fail"
    exit 1
else
    log_summary "$BUILD_PASS" "0" "${#BUILD_ORDER[@]}" "$TOTAL_DURATION" "success"
fi

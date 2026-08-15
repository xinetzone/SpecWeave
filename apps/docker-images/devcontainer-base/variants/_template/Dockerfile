# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - __VARIANT_NAME__ Variant
# Description: __VARIANT_DESCRIPTION__
#
# Placeholders (replace after copying):
#   __VARIANT_NAME__           variant name (e.g. conda-llvm)
#   __VARIANT_DESCRIPTION__    short description
#   __BASE_VARIANT__           parent prefix (empty=base, "conda-"=conda child)
#   __EXTRA_BUILD_ARGS__       extra ARG declarations
#   __EXTRA_SYSTEM_PACKAGES__  apt packages (space-separated, or empty)
#   __EXTRA_CONDA_GROUPS__     conda_install_group calls
#   __EXTRA_PIP_PACKAGES__     pip packages (space-separated, or empty)
#   __EXTRA_CONFIG_STEPS__     post-install chmod/chown/activation config
#   __EXTRA_VALIDATION__       variant-specific verification
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
__EXTRA_BUILD_ARGS__

FROM devcontainer-base:__BASE_VARIANT__${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
__EXTRA_BUILD_ARGS__

LABEL maintainer="SpecWeave"
LABEL description="__VARIANT_DESCRIPTION__"
LABEL variant="__VARIANT_NAME__"

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Copy shared framework (10 modules) + legacy conda-mirror-setup.sh
COPY variants/shared/lib/ /usr/local/share/variant-framework/
COPY variants/shared/scripts/conda-mirror-setup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/conda-mirror-setup.sh

# ── Stage 1/5: Framework init + base verification ──────────────────
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "__VARIANT_NAME__"
variant_timer_stage 1 "Framework init + base verification"
variant_log_info "python: $(python --version 2>&1)"
test -d /opt/venv && test -x /opt/venv/bin/python && variant_log_ok "/opt/venv verified"
id devuser >/dev/null 2>&1 && variant_log_ok "devuser exists"
S1

# ── Stage 2/5: Mirrors + system packages ───────────────────────────
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "Mirrors + system packages"
variant_configure_mirrors
apt-get update -qq
if [ -n "__EXTRA_SYSTEM_PACKAGES__" ]; then
    apt_install_group "System dependencies" __EXTRA_SYSTEM_PACKAGES__
fi
S2

# ── Stage 3/5: Core variant installation ───────────────────────────
RUN <<'S3'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Core variant installation"
# __EXTRA_CONDA_GROUPS__
# Example:
#   conda_install_group "G1: LLVM" "LLVM toolchain" "llvmdev=${LLVM_VERSION}"
if [ -n "__EXTRA_PIP_PACKAGES__" ]; then
    pip_install_group "Python tools" "Utilities" __EXTRA_PIP_PACKAGES__
fi
# Custom steps here
S3

# ── Stage 4/5: Post-install configuration ──────────────────────────
RUN <<'S4'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 4 "Post-install configuration"
ensure_all_permissions
# __EXTRA_CONFIG_STEPS__
S4

# ── Stage 5/5: Metadata + cleanup + verification + summary ─────────
RUN <<'S5'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 5 "Final metadata + cleanup + verification"
variant_write_build_info "__VARIANT_NAME__" "__BASE_VARIANT__${BASE_TAG}" \
    "VARIANT_DESCRIPTION=__VARIANT_DESCRIPTION__" \
    "APT_MIRROR=${APT_MIRROR}" "CONDA_MIRROR=${CONDA_MIRROR}" "PIP_MIRROR=${PIP_MIRROR}"
cleanup_all
verify_validation_header "Final Verification"
/opt/venv/bin/python --version
verify_base_services
verify_devuser_access
# __EXTRA_VALIDATION__
variant_timer_summary "__VARIANT_NAME__ Variant"
echo ""
echo "########################################################################"
echo "# __VARIANT_NAME__ BUILD COMPLETE"
echo "########################################################################"
S5

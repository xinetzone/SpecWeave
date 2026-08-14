# Changelog

All notable changes to the **caffe-ffi-jupyter** Docker development environment will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to calendar versioning (YYYY-MM-DD) for dated snapshots.

---

## [Unreleased]

### Added
- **Container health check** (`scripts/container-healthcheck.sh`): Comprehensive Docker HEALTHCHECK that verifies conda environment activation, `caffe_ffi` Python import, `_caffe_ffi.so` shared library resolution, protobuf ABI compatibility (serialize/parse roundtrip test), and Jupyter HTTP API responsiveness. Replaces the previous simple `curl` health check which only verified Jupyter was up but could not detect C++ extension failures.
- **HEALTHCHECK instruction** baked into the Dockerfile (`--interval=30s --timeout=10s --start-period=120s --retries=3`), so containers started without docker-compose also benefit from health monitoring.
- **curl** added to runtime apt dependencies to support the health check script.
- **External editable-install.sh** (`scripts/editable-install.sh`): Moved from inline Dockerfile heredoc to standalone script for better maintainability. Includes build reliability fixes:
  - Auto-skip rebuild if package already installed from source directory (fast container restarts, ~3s vs ~2min)
  - Stale CMake build cache detection: automatically cleans `build/` if cached paths reference non-existent directories
  - Build retry logic: if first `pip install -e` fails, cleans build dir and retries once
  - Pre-build environment fixes: auto-creates `libopenblas.so → libopenblas.so.0` symlink (cmake looks for `.so`, conda ships `.so.0`)
  - tvm-ffi build with `-DTVM_FFI_USE_LIBBACKTRACE=OFF` to avoid libbacktrace compilation failures
  - caffe-ffi build with `-DCAFFE_FFI_ENABLE_BACKTRACE=OFF` for consistent backtrace behavior
  - Detects `.so` dependency resolution on existing installs (only rebuilds if deps are broken)

### Changed
- docker-compose.yml health check now uses `container-healthcheck.sh` instead of raw `curl -f http://localhost:8888/api`.
- docker-compose.yml mounts `scripts/editable-install.sh` and `scripts/container-healthcheck.sh` as read-only volumes, enabling script updates without rebuilding the Docker image.

### Fixed
- **Healthcheck protobuf false negative**: The original protobuf ABI check used an empty `DescriptorPool()` which doesn't contain built-in descriptors, causing false "UNHEALTHY" reports. Fixed to use a serialize/parse roundtrip test that actually verifies C++ protobuf library linkage.
- **Container restart rebuild loop**: Every container restart triggered a full C++ recompile (~2-3 minutes) because the entrypoint didn't check if the editable install was already valid. Fixed with "already installed from source" detection, reducing restart time to ~3 seconds.
- **libopenblas.so missing error**: Conda ships `libopenblas.so.0` but cmake looks for `libopenblas.so` during caffe-ffi linking, causing `ninja: error: .../libopenblas.so: missing and no known rule to make it`. Fixed by auto-creating the symlink before build.
- **tvm-ffi libbacktrace build failure**: `project_libbacktrace-build-Release.cmake` CMake error during tvm-ffi compilation. Fixed by passing `-DTVM_FFI_USE_LIBBACKTRACE=OFF` to cmake.
- **Windows mount CRLF contamination**: CRLF line endings in mounted source files breaking Linux builds (fixed by existing `fix_crlf()` function, now also applied before build retry).

---

## 2026-08-03

### Added
- **C++ extension dependency diagnostic script** (`scripts/check-cpp-extension-deps.sh`): A comprehensive environment diagnostic tool that works across Docker, WSL, and native Linux environments. Features include:
  - Automatic conda environment detection and activation
  - `_caffe_ffi.so` location discovery (via Python import or build directory search)
  - `LD_LIBRARY_PATH` analysis with `--fix` auto-repair mode
  - `ldd` dependency resolution with guided remediation for missing libraries
  - Protobuf ABI version compatibility verification
  - Python import test with C++ extension availability check
  - `--smoke` mode running Forward+Backward on a test network
- Script installed to `/usr/local/bin/check-cpp-extension-deps.sh` in the container for on-demand diagnostics.

### Changed
- Dockerfile updated to COPY and install `check-cpp-extension-deps.sh` with CRLF normalization (consistent with other scripts).
- Updated `xuanspace` submodule to include new caffe-ffi testing infrastructure:
  - **Gradient regression CLI** (`grad_regression_cli.py`): CI-friendly command-line tool supporting prototxt loading, numpy reference backward comparison, numerical gradient cross-validation, JSON structured output, and standard exit codes (0=PASS/1=FAIL/2=ERROR).
  - **`assert_backward_matches_reference()`**: New utility function in `_grad_check_utils.py` that automatically compares C++ analytical gradients against numpy reference implementations, with optional numerical gradient end-to-end verification.
  - **11 tie-breaking and overlap accumulation tests**: New test classes `TestMaxPoolTieBreaking` and `TestPoolOverlapAccumulation` covering all-equal windows, partial ties, random tie inputs, overlap gradient accumulation, boundary `pool_size` correction, and gradient conservation.
  - **Nightly CI pipeline**: `.github/workflows/ci.yml` now includes a `nightly` job (cron: `0 2 * * *` UTC) running edge-case tests, multi-seed numerical gradient verification, and CLI smoke tests (AVE/MAX pool vs numpy reference), with JSON results uploaded as artifacts.
  - Fixed `_PROJECT_ROOT` path calculation bug (4-level parent → 2-level) that prevented reference module imports in the CLI tool.

### Knowledge Base
- **Pooling backward gradient routing technical report** archived to `docs/retrospective/reports/code-optimization/report-pooling-backward-gradient-routing-20260803/`: Contains mathematical definitions for MAX/AVE Pooling gradient routing, numpy reference implementations, L0-L3 three-layer verification methodology, test coverage matrix, tie-breaking and overlap accumulation pitfalls analysis, and diagnostic tool usage guide.
- **5 reusable best-practice patterns** added to knowledge base:
  1. `caffe-pooling-max-gradient-routing` — MAX Pooling Winner-Takes-All gradient routing
  2. `caffe-pooling-ave-gradient-routing` — AVE Pooling uniform gradient distribution
  3. `hand-computed-gradient-verification` — Hand-computed known-value L1 verification
  4. `caffe-layer-backward-validation-workflow` — Caffe layer backward validation standard workflow
  5. `numerical-gradient-diagnostic-logging` — Numerical gradient error diagnostic logging

---

## 2026-07-29 (Initial Stable Release)

### Added
- **Multi-stage Docker build**: `continuumio/miniconda3` as builder stage → `jupyter-ssh-base:1.1` as runtime stage
- **Conda environment**: `caffe-ffi` environment with Python 3.14, libprotobuf ≥7.0, numpy ≥2.3, scikit-build-core ≥0.10, Cython ≥3.2.8, pytest ≥8.0, ipykernel, apache-tvm-ffi
- **Editable install entrypoint** (`/usr/local/bin/editable-install.sh`): Auto-detects mounted source directories, fixes CRLF line endings for Windows/WSL mounts, performs `pip install --no-build-isolation -e .` with RPATH configuration, updates ldconfig, and verifies imports
- **Jupyter kernel**: Registered as `Python (caffe-ffi)` in system-level kernel directory
- **C++ build toolchain scripts**: test-cpp-tests.sh, test-asan.sh, test-blas-bench.sh, test-conda-build.sh
- **docker-compose.yml**: SSH (2222) + Jupyter (8888) port mapping, SpecWeave repo mount to `/SpecWeave`, named volume for `/workspace`, health check with curl
- **Chinese locale**: zh_CN.UTF-8 / Asia/Shanghai timezone inherited from jupyter-ssh-base

### Fixed
- `--no-build-isolation` flag preventing pip build isolation runtime link failures
- Three-layer runtime library path guarantee: `LD_LIBRARY_PATH` + `/etc/ld.so.conf.d/caffe-ffi.conf` (ldconfig) + build-time RPATH embedding
- Runtime-stage Jupyter kernel registration to system prefix for venv Jupyter discovery
- libprotobuf-dev version compatibility via apt runtime installation (Ubuntu 26.04 compatible)
- ldd shared library verification in build logs

### Infrastructure
- Base image: `jupyter-ssh-base:1.1` (must be pre-built)
- Build context: SpecWeave repository root (for accessing caffe-ffi/tvm-ffi source)
- Non-root user: `jupyteruser` (UID 1000)
- Mirror support: Aliyun/Tsinghua TUNA mirrors for apt, pip, and conda (configurable via build args)
- Network resilience: 5 retries / 120s timeout for wget, 5 retries for apt

---

## Environment Quick Reference

| Component | Version/Path |
|-----------|-------------|
| Conda env | `caffe-ffi` (`/opt/conda/envs/caffe-ffi/`) |
| Python | 3.14 |
| Jupyter token | `jupyter123` (set via `JUPYTER_TOKEN` env) |
| SSH password | `changeme` (set via `USER_PASSWORD` env) |
| SSH port | `2222` (host) → `22` (container) |
| Jupyter port | `8888` (host) → `8888` (container) |
| Source mount | `/SpecWeave` (host repo root) |
| Health check | `container-healthcheck.sh` (30s interval, 120s start period) |
| Diagnostic script | `/usr/local/bin/check-cpp-extension-deps.sh` (use `--fix --smoke` for auto-repair) |

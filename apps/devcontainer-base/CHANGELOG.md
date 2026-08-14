# Changelog

All notable changes to the devcontainer-base project will be documented in this file.

---

## [2.2-ft] - 2026-08-14

### 🎯 Release Summary

v2.2-ft is the first production-ready release with **Python 3.14.6 free-threading (cp314t)** as the default Python runtime. This release focuses on build pipeline optimization, reproducible environments, and providing a standardized C extension development template for the free-threading ecosystem.

**Release Tag**: `devcontainer-base:v2.2-fasttest`
**Base Image**: Ubuntu 26.04 LTS
**Python**: 3.14.6 (cpython-314t, `Py_GIL_DISABLED=1`)
**Status**: ✅ **P0+P1 All Tests Passed**

---

### 📊 Acceptance Test Results

#### Build Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Image size | 2.2–2.5 GB | **2.46 GB** | ✅ |
| Cold build time (no cache) | 5–8 min | **10.7 min** (642s) | ⚠️ * |
| Hot build time (cache hit) | 1–3 min | ⏳ BuildKit cache configured, pending CI validation | ⏳ |
| Python ABI | cpython-314t | **cpython-314t-x86_64-linux-gnu** | ✅ |
| Free-threading enabled | Py_GIL_DISABLED=1 | **1** | ✅ |

> *Cold build time is 10.7 min due to Stage 4 (conda dependency solve: 419s, 65% of total) being the primary bottleneck. BuildKit cache mounts are expected to reduce Stage 4 to sub-minute on subsequent builds. Stage 7 cleanup (126s) is a secondary optimization target for v2.3.

#### Cold Build Stage Breakdown

| Stage | Description | Duration | Cumulative |
|-------|-------------|----------|------------|
| 1/7 | System packages + locale setup | 48s | 48s |
| 2/7 | Docker CE (DinD) | 19s | 67s |
| 3/7 | Podman rootless | 28s | 95s |
| 4/7 | **Miniforge3 + libmamba + Python 3.14t + Jupyter** | **419s** | 514s |
| 5/7 | User config + daemon setup | 1s | 515s |
| 6/7 | Configuration + validation | 1s | 516s |
| 7/7 | Cleanup + final verification (fast) | 126s | **642s** |

#### C Extension Free-Threading Build Verification

Verified via `templates/cmake-cext/test-in-docker.sh` inside `devcontainer-base:v2.2-fasttest` container:

| Test Item | Expected | Actual | Status |
|-----------|----------|--------|--------|
| CMake configure | Success | **<1s** | ✅ |
| C compilation (GCC 15.2.0) | Success | **<1s** | ✅ |
| Self-test (basic checks) | 3/3 passed | **3/3 passed** | ✅ |
| `sum_of_squares(100)` | 338,350 | **338,350** | ✅ |
| `atomic_increment(42)` | 42 | **42** | ✅ |
| `atomic_get` after increment | 42 | **42** | ✅ |
| Multi-thread stress test | 800,000 ops correct | **800,000/800,000** | ✅ |
| Race condition | None | **None detected** | ✅ |
| Stress test wall time | <1s | **0.026s** | ✅ |
| Atomic throughput | N/A | **30.7M ops/sec** | ✅ |
| FT ABI verification | cpython-314t | **cpython-314t** | ✅ |
| GIL declaration | Py_MOD_GIL_NOT_USED | **Verified** | ✅ |
| Output .so file size | N/A | **21.4 KB** | ✅ |

**Stress Test Details**: 8 threads × 100,000 atomic increments each = 800,000 total operations. All operations completed correctly with zero lost updates, confirming that `stdatomic.h` atomic operations work correctly under Python 3.14t free-threading without the GIL.

#### Toolchain Versions

| Tool | Version |
|------|---------|
| Python | 3.14.6 (cp314t, free-threading) |
| GCC | 15.2.0 (Ubuntu 15.2.0-16ubuntu1) |
| CMake | 4.2.3 |
| Ninja | 1.13.2 |
| conda | 26.3.2 (libmamba solver) |
| Docker | 29.7.2 |

---

### ✨ New Features (P0 - Core)

| # | Feature | Description |
|---|---------|-------------|
| A1 | **BuildKit Cache Mounts** | 3 cache mounts (pip, conda pkgs, libmamba solver) for fast rebuilds; cache directories preserved during cleanup |
| A2 | **Parameterized Verification Scripts** | `verify-cext.sh` supports 7 CLI args (`--python`, `--expect-soabi`, `--json`, `--deep`, etc.); zero-argument default behavior preserved |
| A3 | **Reliable Benchmark Defaults** | `ft-benchmark.sh` quick mode: 500K primes / 3.0x threshold (eliminates false positives from 50K/2.0x) |
| A4 | **Deep Verify Mode** | `build.sh --deep-verify`: bypass image build, run container and conda install numpy/pandas for scientific computing validation |
| A5 | **Build Verify Modes** | Three-tier verification: `fast` (C extension load test, default), `standard` (full C extension suite), `off` (skip verification) |

### 🚀 Enhancements (P1 - Extended)

| # | Enhancement | Description |
|---|-------------|-------------|
| B1 | **micromamba Comparison Experiment** | `compare-micromamba.sh` + `Dockerfile.micromamba` for evaluating micromamba vs Miniforge3 (build time / image size / feature parity) |
| B2 | **conda-lock Support** | `conda-lock/environment.yml` with exact version pinning for cp314t toolchain; `generate-locks.sh` supports generate/verify/install/cmake actions |
| B3 | **FT C Extension Standard Template** | `templates/cmake-cext/` — production-ready CMake + C template with GIL declaration, atomic ops, GIL release, self-test, and stress test built in |

### 📚 Documentation

- **[PY314T-C-EXTENSION-GUIDE.md](docs/PY314T-C-EXTENSION-GUIDE.md)** — Team technical share: 7 key changes in Python 3.13t/3.14t C extensions, 7 pitfalls encountered during development, and a best-practice checklist
- **[V2.2-BUILD-PIPELINE-OPTIMIZATION.md](V2.2-BUILD-PIPELINE-OPTIMIZATION.md)** — Full methodology record (First Principles → Adversarial Review → Insight Implementation)
- **C Extension Compilation Rules** — Mandatory specifications for GIL declaration, thread safety, CMake configuration, dependency versions, and testing requirements (Section 9 of pipeline doc)

### 🐛 Bug Fixes

- Fixed `Py_CompileString` worker code missing `import ft_extension` causing `NameError` in worker threads
- Fixed `Py_BuildValue` format string mismatch (`{s:l,s:l,s:l,s:O}` had 4 specifiers for 5 key-value pairs, causing `correct` field to be missing from return dict
- Added conda `main` environment auto-activation in container test script (base env has non-FT Python 3.13)
- Fixed FT detection logic in test CMakeLists.txt (simplified to direct `Py_GIL_DISABLED == 1` check, removed fragile SOABI string parsing)

### 📋 Known Limitations

1. **Cold build time (10.7 min)** exceeds the 5–8 min target due to conda dependency resolution; BuildKit cache is expected to address this for rebuilds
2. Stage 7 aggressive binary stripping (126s) has diminishing returns; optimization candidate for v2.3
3. Hot build time validation pending CI pipeline testing

---

## [2.1-ft] - 2026-08-13

### Changes
- Initial free-threading Python support (cp314t)
- Four-layer verification pipeline (pre-check → build-in → smoke → benchmark)
- libmamba solver integration
- Basic C extension verification (6 core modules)
- ft-benchmark.sh prime number benchmark for GIL validation

---

## [2.0] - 2026-08-12

### Changes
- Baseline release with Ubuntu 26.04 LTS
- Docker-in-Docker support
- Podman rootless support
- JupyterLab integration
- Multi-stage slim build

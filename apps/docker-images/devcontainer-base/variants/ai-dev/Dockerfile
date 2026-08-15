# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - AI Dev (Full AI/ML/NLP Stack, Dual-Env Architecture)
# Base: devcontainer-base:torch-dev-${BASE_TAG} (free-threading PyTorch cp314t in main env)
# Architecture: DUAL-ENV - base(GIL):50+ packages(NLP/data/viz/web/db) | main(ft):PyTorch+ONNX
# PATH priority: /opt/conda/bin first (base env python default; main env accessible via full path)
# Jupyter: "Python 3 (AI Dev)" kernel registered in main env's jupyter, pointing to base python
# Build (CN): docker build -f variants/ai-dev/Dockerfile --build-arg PIP_MIRROR=aliyun -t devcontainer-base:ai-dev-latest .
# Verify (base): docker run --rm devcontainer-base:ai-dev-latest python -c "import transformers,datasets,fastapi,pandas;print('ai-dev OK')"
# Verify (main ft): docker run --rm devcontainer-base:ai-dev-latest /opt/conda/envs/main/bin/python -c "import torch,sys;print(torch.__version__);assert not sys._is_gil_enabled()"
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:torch-dev-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer ai-dev: full AI/ML/NLP ecosystem (50+ pkgs in base GIL env), free-threading PyTorch (main env), JupyterLab 4.x, dual-env architecture"
LABEL variant="ai-dev"
LABEL ecosystem="nlp,transformers,data-science,document-processing,web-api,database"
LABEL architecture="dual-env:base(GIL)+main(free-threading)"

ENV CONDA_DIR=/opt/conda \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_WAIT_POLICY=PASSIVE \
    KMP_DUPLICATE_LIB_OK=TRUE
ENV PATH=/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Framework already inherited from torch-dev base layer.

# ── Stage 1/3: Base verification (torch-dev inheritance + dual-env pre-check)
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "ai-dev"
variant_timer_stage 1 "Base verification (torch-dev inheritance + dual-env pre-check)"

# main env (free-threading) verification from torch-dev
/opt/conda/envs/main/bin/python -c "import torch, torchvision; print(f'  [OK] torch {torch.__version__} + torchvision {torchvision.__version__} in main env')"
/opt/conda/envs/main/bin/python -c "from onnxruntime.quantization import quantize_dynamic; print('  [OK] quantization API in main env')"
/opt/conda/envs/main/bin/python -c "import sys; assert sys._is_gil_enabled() is False; print('  [OK] main env GIL disabled (free-threading cp314t)')"

# base env (GIL) pre-check
python -c "import sys; assert sys._is_gil_enabled() is True; print('  [OK] base env GIL enabled (standard Python)')"
test -d /opt/conda && test -x /opt/conda/bin/python && echo "  [OK] /opt/conda base environment present"
echo "  [OK] torch-dev base verified (dual-env architecture confirmed)"
S1

# ── Stage 2/3: Install full AI/ML/NLP ecosystem (50+ packages in BASE env)
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "Install full AI/ML/NLP ecosystem (base env, 50+ packages)"
variant_activate_base_env  # activates base + sets PIP_USER=0 for build-time

pip install --no-cache-dir --upgrade pip setuptools wheel
echo "  pip: $(pip --version 2>&1 | awk '{print $2}')"

pip_install_group "G1: Build Tools" "scikit-build-core, nuitka, invoke, build" \
    scikit-build-core nuitka invoke build

pip_install_group "G2: Core Utilities" "decorator, attrs, cloudpickle, typing_extensions, pytest, psutil" \
    decorator attrs cloudpickle typing_extensions pytest psutil

pip_install_group "G3: Jupyter Ecosystem" "ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3" \
    ipython ipykernel "jupyterlab>=4.4" "notebook>=7.3"

pip_install_group "G4: Data Processing" "pyarrow, pandas, scikit-learn, natsort" \
    pyarrow pandas scikit-learn natsort

pip_install_group "G5: NLP/Transformers" "datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken, onnx2torch" \
    datasets transformers sentencepiece sentence-transformers evaluate tiktoken onnx2torch

pip_install_group "G6: Visualization/CLI" "matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich" \
    matplotlib seaborn wordcloud tabulate tqdm colorama rich

pip_install_group "G7: AI/ML Utilities" "einops, open_clip_torch, numba" \
    einops open_clip_torch numba

pip_install_group "G8: Audio Processing" "librosa (soundfile/audioread/resampy as deps)" \
    librosa

pip_install_group "G9: Chinese NLP" "jieba, nltk, pypinyin" \
    jieba nltk pypinyin

pip_install_group "G10: Document Processing" "PyMuPDF, EbookLib, beautifulsoup4, openpyxl" \
    PyMuPDF EbookLib beautifulsoup4 openpyxl

pip_install_group "G11: Web/API Stack" "pydantic, fastapi, uvicorn, httpx>=0.28" \
    pydantic fastapi uvicorn "httpx>=0.28"

pip_install_group "G12: Serialization/Config" "toml, typer, xmltodict, pyyaml" \
    toml typer xmltodict pyyaml

pip_install_group "G13: Database Clients" "psycopg2-binary, pymongo, elasticsearch, minio" \
    psycopg2-binary pymongo elasticsearch minio

pip_install_group "G14: Developer Tools" "icecream" \
    icecream

ensure_all_permissions
cleanup_binaries
cleanup_pycache
cleanup_conda_pip_cache
pip check 2>&1 | head -5 || true
echo ""
echo "  Installed package versions (base env):"
python -c "
import importlib
pkgs = [('transformers','transformers'),('datasets','datasets'),('sentence_transformers','sentence-transformers'),
        ('fastapi','fastapi'),('uvicorn','uvicorn'),('pydantic','pydantic'),('pandas','pandas'),
        ('pyarrow','pyarrow'),('sklearn','scikit-learn'),('matplotlib','matplotlib'),('jieba','jieba'),
        ('nltk','nltk'),('fitz','PyMuPDF'),('psycopg2','psycopg2-binary'),('pymongo','pymongo'),
        ('elasticsearch','elasticsearch'),('minio','minio'),('nuitka','nuitka'),('rich','rich'),
        ('httpx','httpx'),('numba','numba'),('librosa','librosa')]
for mod, name in pkgs:
    try:
        m = importlib.import_module(mod); print(f'    {name}: {getattr(m,\"__version__\",\"installed\")}')
    except ImportError: print(f'    {name}: NOT FOUND')
"
S2

# ── Stage 3/3: Jupyter kernel + build-info + dual-env validation ─
RUN <<'S3'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Jupyter kernel + build-info + dual-env validation"
variant_activate_base_env

# ── Register "Python 3 (AI Dev)" Jupyter kernel (points to base python, lives in main env jupyter)
echo "[ACTION] Registering 'Python 3 (AI Dev)' Jupyter kernel..."
mkdir -p /opt/conda/envs/main/share/jupyter/kernels/ai-dev
cat > /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json <<'KERNEL'
{
 "display_name": "Python 3 (AI Dev)",
 "language": "python",
 "argv": ["/opt/conda/bin/python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
 "env": {"PATH": "/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
         "OMP_NUM_THREADS": "4", "KMP_DUPLICATE_LIB_OK": "TRUE"}
}
KERNEL
AI_GROUP=$(id -g devuser)
chown -R devuser:${AI_GROUP} /opt/conda/envs/main/share/jupyter/kernels/ai-dev
chmod 644 /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json
echo "[OK] ai-dev kernel registered (main env jupyter, base python)"

variant_write_build_info "ai-dev" "torch-dev-${BASE_TAG}" \
    "VARIANT_DESCRIPTION=Full AI/ML/NLP Python ecosystem (dual-env: base GIL 50+pkgs + main ft PyTorch)" \
    "ARCHITECTURE=dual-env: base(GIL,/opt/conda) for NLP/data/web + main(free-threading,/opt/conda/envs/main) for PyTorch" \
    "PYTHON_BASE_VERSION=$(python --version 2>&1 | awk '{print $2}') (GIL-enabled)" \
    "PYTHON_MAIN_VERSION=$(/opt/conda/envs/main/bin/python --version 2>&1 | awk '{print $2}') (cp314t free-threading, GIL disabled)" \
    "PYTORCH_VERSION=$(/opt/conda/envs/main/bin/python -c 'import torch;print(torch.__version__)' 2>/dev/null)" \
    "TORCHVISION_VERSION=$(/opt/conda/envs/main/bin/python -c 'import torchvision;print(torchvision.__version__)' 2>/dev/null)" \
    "TRANSFORMERS_VERSION=$(python -c 'import transformers;print(transformers.__version__)' 2>/dev/null)" \
    "DATASETS_VERSION=$(python -c 'import datasets;print(datasets.__version__)' 2>/dev/null)" \
    "FASTAPI_VERSION=$(python -c 'import fastapi;print(fastapi.__version__)' 2>/dev/null)" \
    "PANDAS_VERSION=$(python -c 'import pandas;print(pandas.__version__)' 2>/dev/null)" \
    "JUPYTERLAB_VERSION=$(/opt/conda/envs/main/bin/jupyter lab --version 2>/dev/null | head -1)" \
    "JUPYTER_KERNEL=ai-dev (Python 3 AI Dev, /opt/conda/bin/python, registered in main jupyter)" \
    "PACKAGES_COUNT=50+ (G1-G14 in base env)" \
    "PACKAGES_GROUPS=G1:Build,G2:Utils,G3:Jupyter,G4:Data,G5:NLP,G6:Viz,G7:AI,G8:Audio,G9:CN-NLP,G10:Doc,G11:Web,G12:Config,G13:DB,G14:DevTools" \
    "PATH_PRIORITY=conda-base-bin-first" \
    "BASE_VARIANT=torch-dev(PyTorch+ONNX-quant+LLVM inherited)"

cleanup_all

verify_validation_header "Dual-Env AI Dev Validation (9 checks)"

# Check 1-8: base env package imports
python -c "import transformers, datasets, sentence_transformers, evaluate; print('  [1/9] NLP stack imports OK')"
python -c "import fastapi, uvicorn, pydantic, httpx; print('  [2/9] Web/API stack imports OK')"
python -c "import pandas, pyarrow, sklearn; print('  [3/9] Data stack imports OK')"
python -c "import matplotlib, seaborn, rich, typer; print('  [4/9] Viz/CLI stack imports OK')"
python -c "import jieba, nltk, pypinyin; print('  [5/9] Chinese NLP imports OK')"
python -c "import fitz, bs4, openpyxl; print('  [6/9] Document processing imports OK')"
python -c "import psycopg2, pymongo, elasticsearch, minio; print('  [7/9] Database clients imports OK')"
python -c "import nuitka, pytest, psutil, icecream; print('  [8/9] Build/dev tools imports OK')"

# Check 9: dual-env GIL architecture + main env inheritance
echo "  [9/9] Dual-env GIL architecture verification:"
/opt/conda/envs/main/bin/python -c "import torch, torchvision; print(f'    main env: torch {torch.__version__} + torchvision {torchvision.__version__}')"
/opt/conda/envs/main/bin/python -c "from onnxruntime.quantization import quantize_dynamic; print('    main env: quantization API OK')"
/opt/conda/envs/main/bin/python -c "import sys; assert sys._is_gil_enabled() is False; print('    main env: GIL disabled (free-threading cp314t)')"
python -c "import sys; assert sys._is_gil_enabled() is True; print('    base env: GIL enabled (standard Python)')"
echo "[OK] GIL architecture: base=GIL, main=free-threading"

verify_base_services

# JupyterLab version check
_JL_VER=$(/opt/conda/envs/main/bin/jupyter lab --version 2>/dev/null | head -1)
_JL_MAJOR=$(echo "$_JL_VER" | cut -d. -f1)
_JL_MINOR=$(echo "$_JL_VER" | cut -d. -f2)
if [ "$_JL_MAJOR" -gt 4 ] || { [ "$_JL_MAJOR" -eq 4 ] && [ "$_JL_MINOR" -ge 4 ]; }; then
    echo "  [OK] JupyterLab $_JL_VER meets >=4.4 requirement"
else
    echo "  [WARN] JupyterLab $_JL_VER may not meet >=4.4 requirement"
fi

# Kernel + devuser checks
test -f /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json && echo "  [OK] ai-dev kernel.json present"
echo -n "  [VERIFY] devuser base env packages access... "
su - devuser -c "python -c 'import transformers,pandas,fastapi;print(\"OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }
echo -n "  [VERIFY] devuser main env PyTorch access... "
su - devuser -c "/opt/conda/envs/main/bin/python -c 'import torch;print(\"OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

echo ""
variant_timer_summary "ai-dev Variant (add-on)"
echo "########################################################################"
echo "# AI-DEV BUILD COMPLETE - Dual-Env: base(GIL 50+pkgs) + main(ft PyTorch)"
echo "# Quick (base): import transformers, datasets, fastapi, pandas"
echo "# Quick (main ft): /opt/conda/envs/main/bin/python -c \"import torch;print(torch.__version__)\""
echo "# Jupyter: jupyter lab --allow-root (kernel: Python 3 (AI Dev))"
echo "########################################################################"
S3

# Runtime environment
ENV PIP_USER=1

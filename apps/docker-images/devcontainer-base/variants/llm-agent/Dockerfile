# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - LLM Agent (LangChain/LangGraph + LLM SDKs + Vector DB)
# Base: devcontainer-base:ai-dev-${BASE_TAG} (dual-env: base GIL 50+pkgs + main ft PyTorch)
# Toolchain: LangChain ecosystem + LLM SDKs (OpenAI/Anthropic/Google) + vector stores
# Install env: base (GIL) - LangChain/LangGraph ft-compatibility not yet guaranteed
# PATH priority: /opt/conda/bin first (inherited from ai-dev, base env default)
# Kernel: reuses ai-dev "Python 3 (AI Dev)" kernel (no new kernel registered)
# Build (CN): docker build -f variants/llm-agent/Dockerfile --build-arg PIP_MIRROR=aliyun -t devcontainer-base:llm-agent-latest .
# Verify: docker run --rm devcontainer-base:llm-agent-latest python -c "from langchain_core.messages import HumanMessage;from langgraph.graph import StateGraph;print('llm-agent OK')"
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:ai-dev-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer llm-agent: LangChain/LangGraph + LLM SDKs (OpenAI/Anthropic/Google) + vector DBs (FAISS/Chroma), dual-env, free-threading PyTorch available"
LABEL variant="llm-agent"
LABEL ecosystem="langchain,langgraph,llm,agents,rag,vector-db"

# CONDA_DIR/PATH/OMP envs inherited from ai-dev.
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Framework already inherited from ai-dev base layer.

# ── Stage 1/3: Base verification (ai-dev inheritance) ────────────
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "llm-agent"
variant_timer_stage 1 "Base verification (ai-dev inheritance)"

# base env (GIL) verification
python -c "import transformers, datasets, fastapi, pandas; print('  [OK] ai-dev base env packages (transformers/datasets/fastapi/pandas) present')"
python -c "import sys; assert sys._is_gil_enabled() is True; print('  [OK] base env GIL enabled (standard Python for Agent framework)')"

# main env (free-threading PyTorch) verification
/opt/conda/envs/main/bin/python -c "import torch, sys; print(f'  [OK] main env torch {torch.__version__}, GIL disabled: {not sys._is_gil_enabled()}')"

test -f /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json && echo "  [OK] ai-dev Jupyter kernel preserved"
echo "[OK] ai-dev base verified"
S1

# ── Stage 2/3: Install LLM Agent ecosystem (base env, GIL) ──────
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "Install LLM Agent ecosystem (base env, GIL)"
variant_activate_base_env

pip_install_group "G1: LangChain Core" "langchain + langchain-core + langchain-community" \
    langchain langchain-core langchain-community

pip_install_group "G2: LangGraph (Agent Orchestration)" "langgraph (stateful multi-actor agent framework)" \
    langgraph

pip_install_group "G3: LLM SDKs" "openai + anthropic + google-generativeai" \
    openai anthropic google-generativeai

pip_install_group "G4: Vector Stores (RAG)" "faiss-cpu + chromadb" \
    faiss-cpu chromadb

pip_install_group "G5: Agent/Web Tools" "duckduckgo-search + tenacity + pydantic-settings" \
    duckduckgo-search tenacity pydantic-settings

ensure_all_permissions
cleanup_pycache
cleanup_conda_pip_cache
pip check 2>&1 | head -10 || true
echo ""
echo "  Installed LLM Agent package versions:"
python -c "
import importlib
pkgs = [('langchain','langchain'),('langchain_core','langchain-core'),
        ('langchain_community','langchain-community'),('langgraph','langgraph'),
        ('openai','openai'),('anthropic','anthropic'),('google','google-generativeai'),
        ('faiss','faiss-cpu'),('chromadb','chromadb'),('duckduckgo_search','duckduckgo-search'),
        ('tenacity','tenacity'),('pydantic_settings','pydantic-settings')]
for mod, name in pkgs:
    try:
        m = importlib.import_module(mod); print(f'    {name}: {getattr(m,\"__version__\",\"installed\")}')
    except ImportError: print(f'    {name}: NOT FOUND')
"
S2

# ── Stage 3/3: Build-info + LLM Agent smoke tests ───────────────
RUN <<'S3'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Build-info + LLM Agent smoke tests"
variant_activate_base_env

variant_write_build_info "llm-agent" "ai-dev-${BASE_TAG}" \
    "VARIANT_DESCRIPTION=LLM Agent dev env (LangChain/LangGraph + OpenAI/Anthropic/Google SDKs + FAISS/Chroma, dual-env)" \
    "ARCHITECTURE=dual-env: base(GIL,/opt/conda) for LLM/Agent frameworks + main(ft,/opt/conda/envs/main) for PyTorch/ONNX" \
    "INSTALL_ENV=base (GIL) - LangChain ecosystem ft-compat not yet guaranteed" \
    "PACKAGES_GROUPS=G1:LangChain-Core,G2:LangGraph,G3:LLM-SDKs,G4:Vector-Stores,G5:Agent-Tools" \
    "PACKAGES_INSTALLED=langchain,langchain-core,langchain-community,langgraph,openai,anthropic,google-generativeai,faiss-cpu,chromadb,duckduckgo-search,tenacity,pydantic-settings" \
    "PACKAGES_INHERITED=ai-dev(G1-G14 NLP/data/web 50+pkgs) + torch-dev(PyTorch+ONNX) + onnx-quantized + onnx-dev + conda-llvm(LLVM)" \
    "JUPYTER_KERNEL=reuses ai-dev 'Python 3 (AI Dev)' kernel (no new kernel)" \
    "LLM_PROVIDERS=OpenAI,Anthropic,Google Generative AI" \
    "VECTOR_STORES=FAISS(local),Chroma(local)" \
    "AGENT_FRAMEWORKS=LangGraph(stateful agents),LangChain(chains/agents)"

cleanup_all

verify_validation_header "LLM Agent Verification"

python -c "from langchain_core.messages import HumanMessage, SystemMessage; print('  [OK] langchain-core messages import')"
python -c "from langchain_core.prompts import ChatPromptTemplate; print('  [OK] langchain-core prompts import')"
python -c "from langchain_community.document_loaders import TextLoader; print('  [OK] langchain-community document_loaders import')"
python -c "from langgraph.graph import StateGraph, END; print('  [OK] langgraph StateGraph/END import')"
python -c "import openai; print(f'  [OK] openai SDK {openai.__version__}')"
python -c "import anthropic; print(f'  [OK] anthropic SDK {anthropic.__version__}')"
python -c "import google.generativeai as genai; print('  [OK] google-generativeai import')"
python -c "import faiss; print(f'  [OK] faiss-cpu {faiss.__version__}')"
python -c "import chromadb; print(f'  [OK] chromadb {chromadb.__version__}')"
python -c "from duckduckgo_search import DDGS; print('  [OK] duckduckgo-search import')"

# Dual-env architecture verification
echo "  [Dual-env check]:"
python -c "import sys; assert sys._is_gil_enabled() is True; print('    base env: GIL enabled (Agent frameworks)')"
/opt/conda/envs/main/bin/python -c "import torch, sys; assert sys._is_gil_enabled() is False; print(f'    main env: torch {torch.__version__}, GIL disabled (PyTorch/ONNX)')"

verify_base_services

# devuser access check
echo -n "  [VERIFY] devuser LLM packages access... "
su - devuser -c "python -c 'from langchain_core.messages import HumanMessage;print(\"OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

# ── Smoke Test: Minimal LangGraph agent graph construction ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [SMOKE] LangGraph state graph construction     │"
echo "└─────────────────────────────────────────────────┘"
python - <<'LANGSMOKE'
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def think(state: AgentState) -> AgentState:
    return {"messages": [{"role": "assistant", "content": "thinking..."}]}

def respond(state: AgentState) -> AgentState:
    return {"messages": [{"role": "assistant", "content": "hello from llm-agent!"}]}

graph = StateGraph(AgentState)
graph.add_node("think", think)
graph.add_node("respond", respond)
graph.set_entry_point("think")
graph.add_edge("think", "respond")
graph.add_edge("respond", END)
app = graph.compile()
result = app.invoke({"messages": [{"role": "user", "content": "hi"}]})
assert len(result["messages"]) == 3, f"expected 3 messages, got {len(result['messages'])}"
assert result["messages"][-1]["content"] == "hello from llm-agent!"
print(f"[OK] LangGraph: constructed+invoked, {len(result['messages'])} messages, final='{result['messages'][-1]['content']}'")
print("[OK] LLM AGENT SMOKE PASSED (langchain+langgraph imports + graph construction + invocation)")
LANGSMOKE

echo ""
variant_timer_summary "llm-agent Variant (add-on)"
echo "########################################################################"
echo "# LLM-AGENT BUILD COMPLETE"
echo "# LangChain/LangGraph + OpenAI/Anthropic/Google + FAISS/Chroma"
echo "# Quick: from langgraph.graph import StateGraph; from langchain_core.messages import HumanMessage"
echo "# PyTorch (main ft): /opt/conda/envs/main/bin/python -c \"import torch;print(torch.__version__)\""
echo "########################################################################"
S3

# Runtime environment
ENV PIP_USER=1

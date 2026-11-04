# 个人信息管家 Agent —— 应用镜像（同源：前端站点 + API）
#
# 目标运行时 Python 3.14；以非 root 用户运行；无状态，可任意扩缩或重启。
#
# 「同源」是刻意的：前端静态站与 API 由**同一个**进程、同一端口提供。
# 分成两个部署会带来三个必然后果：跨域要配 CORS、平台云服务要求 Origin
# 精确匹配（静态站域名 ≠ API 域名即被拒）、HTTPS 页面请求 HTTP API 被浏览器拦。

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依赖层单独 COPY：改代码不会重装依赖
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip \
    && python -m pip install .

# 前端构建产物：Sphinx 站点。构建期需要 Sphinx 依赖，故先 COPY 构建依赖再构建，
# 最后把构建产物与运行时依赖分层，镜像里不留 Sphinx。
COPY requirements.txt ./
COPY doc ./doc
RUN python -m pip install -r requirements.txt \
    && python -m sphinx -b html -d _build/doctrees --keep-going -W doc _build/html \
    && python -m pip uninstall -y sphinx myst-parser sphinx-book-theme sphinx-copybutton \
       sphinx-design sphinxcontrib-mermaid jieba

# 非 root：容器内进程不该有写镜像的权利
RUN useradd --create-home --uid 10001 butler
USER butler

# 云端平台普遍以 8080 作为默认端口；--host 0.0.0.0 是容器内必需的
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/api/health').status==200 else 1)"

CMD ["info-butler", "serve", "--host", "0.0.0.0", "--port", "8080", "--static"]

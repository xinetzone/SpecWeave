# 个人信息管家 Agent —— 后端镜像
#
# 目标运行时 Python 3.14；以非 root 用户运行；无状态，可任意扩缩或重启。

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

# 非 root：容器内进程不该有写镜像的权利
RUN useradd --create-home --uid 10001 butler
USER butler

# 云端平台普遍以 8080 作为默认端口；--host 0.0.0.0 是容器内必需的
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/api/health').status==200 else 1)"

CMD ["info-butler", "serve", "--host", "0.0.0.0", "--port", "8080"]

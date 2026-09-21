# payload/Dockerfile —— XMNN 载荷（wheel）派生构建入口【客户机执行】
# ------------------------------------------------------------
# 定位：底座镜像 localhost/xmnn-runtime:base-<形态> 不含 XMNN 载荷（只有依赖、
# torch、ipykernel、内核脚本与守卫脚本）；客户拿到交付包后由 xmnnctl load 用本
# 文件把随包 wheel 装入底座，产出派生镜像 localhost/xmnn-runtime:<交付版本>——
# 该 tag 与 compose.yaml 的 ${XMNN_VERSION} 逐字一致，故 compose 无需改动。
#
# 构建上下文 = 本目录（payload/）：只送 wheel（约 177 MB），
# 绝不把同级 artifacts/ 的 1.1 GB 底座归档送进 build（避免无谓的上下文拷贝）。
# 由 xmnnctl 下发：--build-arg BASE_IMAGE=<底座 ref> --build-arg PAYLOAD_VERSION=<交付版本>；
# 产物 tag 由 xmnnctl 用 -t 指定，本文件不打 tag。
#
# 三条硬约束：
#   1) 完全离线：--no-index 禁网、--no-deps 跳过依赖解析（依赖已由底座预装）；
#   2) 不改 ENTRYPOINT/CMD/WORKDIR：派生只是"加一层载荷"，服务契约沿用底座
#      （tini -> entrypoint.sh -> supervisord）；
#   3) 失败即构建失败：载荷守卫（root + devuser 双身份，10 项）与依赖区间校验
#      （pip check）任一不过即中止——不产出 tag，客户机上不会出现半成品镜像。
#      ⚠️ pip check 的判据必须**限定在载荷相关冲突**上：底座的 conda 自身带有
#      与载荷无关的既有元数据冲突（真机实测 `conda 26.7.2 has requirement
#      ruamel-yaml<0.19,>=0.11.14, but you have ruamel-yaml 0.19.1`），若要求
#      pip check 整体 exit 0，派生构建会在任何客户机上 100% 失败。故此处先完整
#      打印全部冲突供人查阅，只有以 xmnn 开头的冲突行（＝载荷声明的依赖在底座
#      缺失或版本不符）才判定为交付失败。
# ------------------------------------------------------------

ARG BASE_IMAGE=localhost/xmnn-runtime:base-cpu
FROM ${BASE_IMAGE}

# FROM 之前声明的 ARG 不能用于 LABEL/RUN，须在 FROM 之后重新声明
ARG BASE_IMAGE
ARG PAYLOAD_VERSION

LABEL org.specweave.component="xmnn-runtime-payload" \
      org.specweave.layer="xmnn-wheel-payload" \
      org.specweave.payload-version="${PAYLOAD_VERSION}" \
      org.specweave.payload-abi="cp314-gil" \
      org.specweave.base-image="${BASE_IMAGE}"

# 载荷 wheel（只可能有一个：payload/.gitignore 忽略 *.whl，交付流水线每次 stage 一个）
COPY xmnn-*.whl /tmp/payload/

# 装载荷（base env = cp314 GIL，故显式 /opt/conda/bin/python）+ 双身份守卫 + pip check
RUN /bin/bash -lc 'set -euo pipefail ; \
    WHL="$(ls /tmp/payload/xmnn-*.whl | head -1)" ; \
    echo "[payload] installing wheel: $WHL" ; \
    /opt/conda/bin/python -m pip install --no-index --no-deps --no-cache-dir "$WHL" ; \
    /opt/conda/bin/python -m pip show xmnn | grep -E "^(Name|Version|Location)" ; \
    rm -rf /tmp/payload /root/.cache/pip ; \
    echo "[payload] runtime smoke (root)" ; \
    /opt/conda/bin/python /opt/xmnnrt-smoke/_runtime_smoke.py ; \
    echo "[payload] runtime smoke (devuser)" ; \
    su -s /bin/bash devuser -c "cd /opt/xmnnrt-smoke && /opt/conda/bin/python _runtime_smoke.py" ; \
    echo "[payload] dependency interval check (pip check)" ; \
    /opt/conda/bin/python -m pip check > /tmp/pipcheck.txt 2>&1 || true ; \
    cat /tmp/pipcheck.txt ; \
    if grep -Eq "^xmnn[[:space:]]" /tmp/pipcheck.txt ; then \
      echo "[payload] FAIL: 载荷声明的依赖未在底座满足（见上方 pip check 输出）" ; \
      exit 1 ; \
    fi ; \
    echo "[payload] no xmnn-related dependency conflict" ; \
    rm -f /tmp/pipcheck.txt ; \
    find /opt/xmnnrt-smoke -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null ; \
    find /opt/xmnnrt-smoke -type f -name "*.pyc" -delete 2>/dev/null ; \
    echo "########################################################################" ; \
    echo "# XMNN-RUNTIME PAYLOAD INSTALLED" ; \
    echo "# payload : $WHL" ; \
    echo "# version : ${PAYLOAD_VERSION}" ; \
    echo "# base    : ${BASE_IMAGE}" ; \
    echo "########################################################################"'
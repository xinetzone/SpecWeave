# Checklist

- [x] 三个内核名全局唯一且互不相同（`npu` / `xmnn-whl-builder` / `xmnn-runtime`）
- [x] 三个内核的 display_name 清晰标示所属环境，无歧义（NPU Dev / xmnn whl-builder / xmnn runtime）
- [x] whl-builder kernel.json 已重命名为 `xmnn-whl-builder`，display_name 与 env（CHAOS_ROOT + PYTHONPATH）正确
- [x] runtime kernel.json 已重命名为 `xmnn-runtime`，display_name 与 env（CHAOS_ROOT + PYTHONPATH）正确
- [x] ai/Dockerfile `npu` kernel.json 与 setup-npu-kernel.sh 内联模板的 env（CHAOS_ROOT + PYTHONPATH）一致
- [x] 三个 Dockerfile 内核注册块路径与校验 grep 均已同步新内核名，无旧名 `xmnn-conda` 残留
- [x] 容器内统一挂载点（`/workspace/chaos`）存在、可读、权限正确
- [x] 运行期内核可访问 external/chaos 下资源（npuusertools / npu_tvm / ai 含 xmnn-client / models），无路径或导入错误
- [x] 挂载验证脚本（`scripts/verify-chaos-mount.sh`）返回 PASS（9/9）
- [x] 变更已通过原子提交（单一职责）

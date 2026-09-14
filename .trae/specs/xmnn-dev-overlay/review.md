# xmnn-dev 开发与打包叠加层 - Independent Review

> Reviewer 契约：fresh context（不参与设计/实施）；只读审查 + 可在
> WSL2 `podman-machine-default` 内独立复核运行证据（镜像
> `localhost/xmnn-dev:latest` c5fc1967d7b4 与 wheel 产物仍在；栈已 down，
> 可按 spec 自行 up）。对照：
> [spec.md](spec.md) 14 AC、[tasks.md](tasks.md) 13 任务完成证据、
> AI 规则 `apps/containers/client/.agents/rules/xmnn-overlay.md`、
> 范式真源 `overlays/onnx-quantized/` 与 `tasks/quant.py`。
> 重点行使 V（对抗审查）：实施期三处细化是否成立、wheel 与已交付 Docker
> 谱系产物是否真等价、"对 ai 零依赖/源码零修改"声明是否可被反证推翻。

- [ ] CP-R1: 对 ai 零依赖与 builder 资产齐全（AC-1）
  - **Type**: `rule`
  - **Covers**: AC-1
  - **Evidence**: Pending

- [ ] CP-R2: compose 配置静态正确（AC-2）
  - **Type**: `rule`
  - **Covers**: AC-2
  - **Evidence**: Pending

- [ ] CP-R3: 镜像真实构建、双 ABI 与工具链/SONAME 事实（AC-3、AC-4）
  - **Type**: `rule`
  - **Covers**: AC-3, AC-4
  - **Evidence**: Pending

- [ ] CP-R4: 栈 E2E（端口/挂载/内核双可见）（AC-5）
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Evidence**: Pending

- [ ] CP-R5: 源码调试链路（import 来自挂载树 + tvm.build）（AC-6）
  - **Type**: `rule`
  - **Covers**: AC-6
  - **Evidence**: Pending

- [ ] CP-R6: Nuitka wheel 真实闭环与内容等价性（AC-7）
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Evidence**: Pending

- [ ] CP-R7: wheel 隔离验证 10 项与 base 零污染（AC-8）
  - **Type**: `rule`
  - **Covers**: AC-8
  - **Evidence**: Pending

- [ ] CP-R8: 外部源码零修改与 AST 还原（AC-9）
  - **Type**: `rule`
  - **Covers**: AC-9
  - **Evidence**: Pending

- [ ] CP-R9: 清理幂等与 ccache 卷语义（AC-10）
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Evidence**: Pending

- [ ] CP-R10: invoke xmnn.* 集成、门禁与键集合（AC-11）
  - **Type**: `rule`
  - **Covers**: AC-11
  - **Evidence**: Pending

- [ ] CP-R11: 零侵入与 quant 零回归（AC-12）
  - **Type**: `rule`
  - **Covers**: AC-12
  - **Evidence**: Pending

- [ ] CP-U1: 范式保真度（AC-13）
  - **Type**: `rubric`
  - **Covers**: AC-13
  - **Scale**: 1-5
  - **Anchors**: 1 = wrapper/特权/短语法/回流根 run/双 ABI 无依据；3 = ≥2 处无注释偏离；5 = 仅 bridge/端口两偏差且有实证注释，双 ABI 跨 env 设计有 chaos 实证出处
  - **Pass Threshold**: >= 4
  - **Evidence**: Pending

- [ ] CP-U2: 产物原子性与文档一致性（AC-14）
  - **Type**: `rubric`
  - **Covers**: AC-14
  - **Scale**: 1-5
  - **Anchors**: 1 = 文档与实现矛盾/坏链/参数不一致；3 = 1-2 处过时；5 = .env/compose/任务参数三处逐字一致、链接全通
  - **Pass Threshold**: >= 4
  - **Evidence**: Pending

## Review History

### Review R1
- **Result**: Pending
- **Evidence**: Pending

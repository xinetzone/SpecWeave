# 旅行规划工作台（travel-planner）- 独立审查

- [x] CP-R1: 行程 CRUD、编排、预算、清单全部功能分支有测试证据且全绿（91 用例，迁移后于 `apps/travel-planner/` 复跑通过）
  - **Type**: `rule`
  - **Covers**: AC-1、AC-2、AC-3、AC-4
  - **Evidence**: pytest（test_storage / test_models / test_domain / test_web 对应断言）；91 passed，整体覆盖率 93%

- [x] CP-R2: 导入导出 round-trip 等价；畸形结构（非 UTF-8 / 非 JSON / 缺字段 / 未知字段）全部拒绝且零写入副作用
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Evidence**: test_export_import_roundtrip / test_export_all_wrapper / test_import_malformed_rejected（含二进制上传分支）

- [x] CP-R3: AI 草稿链路六分支容错 + 白名单校验 + 确认导入才落盘 + 取消零变化
  - **Type**: `rule`
  - **Covers**: AC-6、AC-7、AC-8（降级部分）
  - **Evidence**: test_llm.py 六分支与密钥治理；test_web.py test_ai_generate_preview_and_import / test_ai_cancel_keeps_trip_unchanged / test_ai_not_configured_degrades

- [x] CP-R4: 本地服务安全（仅 127.0.0.1；CSRF 三类拒绝 403；Origin 跨源 403；单实例锁拒绝）
  - **Type**: `rule`
  - **Covers**: AC-9
  - **Evidence**: test_web.py test_csrf_rejections / test_origin_rejection / test_bind_address_defaults_to_loopback；test_cli.py test_serve_blocked_by_existing_instance；security.py 覆盖率 100%

- [x] CP-R5: 原子写注入测试原文件不变、备份滚动保留 5 份、路径守卫拒绝越界
  - **Type**: `rule`
  - **Covers**: AC-10、AC-11（写入路径断言）
  - **Evidence**: test_storage.py test_atomic_write_keeps_original / test_backup_rolling_keep_five / test_path_guard_rejects_bad_ids

- [x] CP-R6: 仓库卫生——运行时数据全部位于 gitignore 私域区，应用目录无运行时产物
  - **Type**: `rule`
  - **Covers**: AC-11
  - **Evidence**: 实施者在仓库根执行 `git status --porcelain` 验证（见 tasks.md Task 10 证据）：仅预期入库变更；`.gitignore` 规则核验（`playground/`、`__pycache__/`、`.pytest_cache/`、`.coverage` 均覆盖）。测试套件不做 git 仓库耦合断言（保持应用可在任意目录独立运行），以人工核验替代

- [x] CP-R7: 凭证零泄露——密钥仅入请求头；异常/日志/响应/模板无密钥原文；环境变量优先
  - **Type**: `rule`
  - **Covers**: AC-12
  - **Evidence**: test_llm.py test_api_key_sent_but_never_leaked；test_web.py test_secret_never_leaked_in_responses；test_config.py env 优先用例；全部模板无 `|safe`

- [x] CP-R8: 界面品质——白底淡蓝、扁平线条图标、毛玻璃弹窗、紧凑布局，视觉评审达阈值
  - **Type**: `rubric`
  - **Covers**: AC-13
  - **Scale**: 1-5
  - **Anchors**: 1 = 通用后台模板感；3 = 配色正确但层次普通；5 = 精致本地工具质感
  - **Pass Threshold**: >= 4
  - **Evidence**: 视觉模型对 4 页截图评审：列表页 4/5（一轮打磨后自 3/5 提升：品牌色块/标题强调线/卡片渐变条与浮起/分组点标）、行程详情页 4/5、AI 草稿预览页 4/5、生成表单页结构核验通过

- [x] CP-R9: AI 生成端到端顺滑度（mock 一次通过，仅用户确认导入一步人工）
  - **Type**: `rubric`
  - **Covers**: AC-14
  - **Scale**: 1-5
  - **Anchors**: 1 = 链路断裂或静默失败；3 = 主流程可用但需 ≥2 次人工补救；5 = mock 一次通过
  - **Pass Threshold**: >= 3
  - **Evidence**: mock 全链路测试通过（生成→预览→剔除→导入，得分 5）；真实端点冒烟因用户未在场配置密钥，按 AC-14 预案以 mock 证据收口，真实冒烟转后续手动项

- [x] CP-R10: 仓库规范符合性——scikit-build-core 约定、禁 `__future__`、apps 路由表登记、spec 三件套命名合规
  - **Type**: `rule`
  - **Covers**: NFR-1、NFR-8、Constraints
  - **Evidence**: pyproject（wheel.packages/build-dir/minimum-version 0.9/无 cmake 段/requires-python>=3.14）；test_no_future_annotations + ruff TID251；apps/AGENTS.md 路由表与边界声明各 +1 行；`.trae/specs/travel-planner/` 三件套（spec/tasks/review，无 checklist.md）

## Review History

### Review R1
- **Result**: `pass`
- **Evidence**: 全新上下文独立审查（explore 子代理，只读）通读 spec/tasks/源码/测试/模板/配置，逐条裁定 14 条 AC 全部 pass；91 个测试函数与完成证据声明逐条对得上；对抗性审查（安全/边界/一致性/完整性/仓库规范五维度）未发现 P0/P1/P2 问题
- **Findings**（全部 advisory/P3，不阻塞验收）：
  1. 非 UTF-8 导入分支缺测试 → **已修复**（Review 后补齐二进制上传断言，91 用例全绿）
  2. AC-11「git status 零污染」为人工核验而非测试断言 → **接受偏差**：避免测试与 git 仓库耦合损害应用可移植性，人工核验证据见 tasks.md Task 10
  3. Origin/Referer 校验为条件性（header 缺失时仅靠 CSRF token）→ **接受偏差**：SameSite=Strict + httponly + token 比对的纵深防御已完整，浏览器同源表单必然携带 Origin；强制要求 header 会破坏非浏览器本地客户端
  4. AC-7 测试草稿数（3 条）与 spec 描述（5 条）不一致 → **接受偏差**：保留/剔除/导入语义等价，行为断言完整
  5. `/import/confirm` 可不经预览页直达（payload 仍经完整校验）→ **接受偏差**：单用户本机 + CSRF 场景无实际风险；后续迭代可引入会话绑定待确认区
- **Notes**: 单实例锁采用内核级字节范围锁（msvcrt/fcntl），优于 spec 描述的「PID 检测陈旧锁接管」——进程崩溃自动释放、无陈旧锁问题，属设计改进而非偏差

> AI生成

# Verbi OKF Wiki 对抗审查报告（V 阶段）

## 四视角审查

| 视角 | 审查问题 | 结论 |
|------|---------|------|
| 事实溯源（魔鬼代言人） | 正文有无 F 之外的数字/模型名？勘误是否落实？ | ✅ 所有数字均带 F 出处；E-1 勘误在 index/02/verification 三处呈现 |
| 结构规范（新人） | toctree 是否完整？文件能否按导航走到？ | ✅ check-toctrees 通过 |
| 读者可用性（未来读者） | 相对链接是否可达？时效边界是否清楚？ | ✅ 相对链接零 file:///；stale_after + 数据时点已声明 |
| 证伪视角（老板） | 博文核心结论是否被独立证据支持？ | ✅ 营收/MRR 双锚（创始人截图序列 + TrustMRR）；单源项已降级标注 |

## 机械门禁结果（2026-09-20）

| 检查项 | 结果 |
|--------|------|
| check-bundles-index.py | ✅ 9 域 / 59 组 / 564 束，五面一致 |
| check-toctrees.py | ✅ 全部 index 引用有效，内容文档均可达 |
| check-utf8.py | ✅ 10560 文件有效 UTF-8 |
| 双份 F 编号 | ✅ 28 = 28，Compare-Object 无差异 |
| file:/// 绝对路径 | ✅ 零出现 |
| 家目录/敏感路径 | ✅ 零出现 |

> gates 说明：本次直接运行子项目 scripts/ 下检查脚本（与 `invoke gates.*` 同一实现），结果如上。

## 勘误落实核对

- ❌ E-1「纯 App Store 自然量 / 全部来自 App 订阅」：正文 [02 定位与渠道](../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/verbi/concepts/02-positioning-growth.md) 已改为「ASO + TikTok/YouTube + UGC + Play」组合口径；index 已知边界同步。
- ⚠️ 单源项（+230.8%、3,609、55%、4.62）均保留口径标注，未拔高为审计事实。

## 未覆盖边界

- 未进行产品真机实测（案例资讯类任务，无此要求）；
- 2026-09-20 存在并发会话编辑同一索引，已通过地面真值脚本复核，最终计数以脚本通过为准。

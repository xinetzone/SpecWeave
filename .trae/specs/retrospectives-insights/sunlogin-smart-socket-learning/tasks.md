# 向日葵智能插座C1Pro/C2/C4三款产品系统性学习与深度洞察 Wiki 教程 - 实施计划

## [x] Task 1: 创建wiki教程主文件基础框架
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 docs/knowledge/learning/ 目录下创建 sunlogin-smart-socket-wiki.md 文件
  - 添加 YAML frontmatter（title/source/date/tags）
  - 创建文档标题和原文参考链接区域
  - 搭建完整的目录导航系统（锚点链接）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于 docs/knowledge/learning/sunlogin-smart-socket-wiki.md
  - `programmatic` TR-1.2: YAML frontmatter格式正确，包含title/source/date/tags四个字段
  - `human-judgement` TR-1.3: 目录导航包含所有16个主要章节，锚点链接正确
- **Notes**: 参考现有wiki格式（如text-to-cad-wiki.md），使用中文标题编号（一、二、三...）

## [ ] Task 2: 编写概述与核心概念章节
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**: 
  - 编写第一章「产品概述与学习目标」：向日葵智能插座产品线定位、三款产品概览、学习目标
  - 编写第二章「核心概念解析」：解释AC Recovery、远程开机、蓝牙配网、本地定时、电量统计、过载保护、4G联网、阻性/感性/容性负载等关键术语
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 概述清晰说明三款产品的整体定位和学习价值
  - `human-judgement` TR-2.2: 核心概念术语解释准确，通俗易懂，非技术读者也能理解
  - `human-judgement` TR-2.3: AC Recovery概念解释包含技术原理说明
  - `human-judgement` TR-2.4: 三类负载（阻性/感性/容性）有通俗解释和对应电器示例
- **Notes**: 术语解释避免过于技术化，配合实际应用场景说明

## [ ] Task 3: 编写C1Pro蓝牙版单独解析章节
- **Priority**: high
- **Depends On**: [Task 2]
- **Description**: 
  - 产品定位：入门基础款，蓝牙闪连远程开关
  - 核心功能：远程开机+延时断电、蓝牙5闪连配网、定时开关（本地定时）、倒计时开关、指示灯开关、断电记忆
  - 技术参数：完整列出C1Pro_BLE的电气参数、尺寸、材质、安全认证
  - 安全特性：一体化铜带、750℃阻燃、CCC认证、独立安全门、1KV抗浪涌
  - 适用场景：家庭/办公室电脑远程开机、定时开关小家电
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 功能列表完整，与官网信息一致
  - `programmatic` TR-3.2: 技术参数准确引用官方数据（型号C1Pro_BLE、10A/2500W、1KV抗浪涌、尺寸59.5×39×51mm等）
  - `human-judgement` TR-3.3: 明确标注C1Pro无电量统计功能
  - `human-judgement` TR-3.4: 适用场景描述具体，符合产品定位
- **Notes**: 参数必须准确，与网页提取内容一致

## [ ] Task 4: 编写C2蓝牙版单独解析章节
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**: 
  - 产品定位：功能增强款，增加电量统计
  - 核心功能：在C1Pro基础上增加实时电量统计（日/周/月功耗可视化）
  - 技术参数：完整列出C2_BLE的电气参数、尺寸、材质、安全认证
  - 安全特性：与C1Pro相同的安全设计
  - 适用场景：需要监控用电情况的用户、电脑/设备功耗监测
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 清晰说明C2相对C1Pro的核心差异（增加电量统计）
  - `programmatic` TR-4.2: 技术参数准确引用官方数据（型号C2_BLE、尺寸44×55×51mm等）
  - `human-judgement` TR-4.3: 电量统计功能说明包含"数据仅供参考"的提示
  - `human-judgement` TR-4.4: 突出C2适合关注用电消耗的用户场景
- **Notes**: 重点突出C2与C1Pro的区别，避免内容重复

## [ ] Task 5: 编写C4 4G版单独解析章节
- **Priority**: high
- **Depends On**: [Task 4]
- **Description**: 
  - 产品定位：户外/无WiFi场景旗舰款，4G联网+过载保护
  - 核心功能：4G联网（内置联通流量，送3年）、扫码绑定零配置、过载保护（2000W告警/2500W断电）、电流/电压/功率阈值设置、电量统计
  - 特色应用场景：户外浇灌、阳台设备（WiFi信号弱）、路由器远程重启、户外设备控制
  - 技术参数：完整列出C4的电气参数、尺寸、工作温度扩展、3KV抗浪涌
  - 安全特性：3000V浪涌保护、过载保护、高温阻燃、独立安全门
- **Acceptance Criteria Addressed**: [AC-3, AC-5, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 清晰说明4G联网方案（联通3年流量，后续10元/年）
  - `human-judgement` TR-5.2: 过载保护功能详细说明（阈值设置、告警和断电机制）
  - `programmatic` TR-5.3: 技术参数准确（型号C4、工作温度-10~50℃、3KV抗浪涌、尺寸59×49×29mm）
  - `human-judgement` TR-5.4: 户外三个典型场景（浇灌/阳台/路由器重启）描述具体有画面感
- **Notes**: C4是差异化最大的产品，重点突出其户外无WiFi场景的独特价值

## [ ] Task 6: 编写三款产品多维度系统对比章节
- **Priority**: high
- **Depends On**: [Task 5]
- **Description**: 
  - 创建核心功能对比矩阵表（至少12个维度：联网方式、配网方式、电量统计、过载保护、浪涌保护、工作温度、尺寸、特色功能、流量费用、适用场景等）
  - 创建技术参数对比表（电气参数、材质、认证等）
  - 编写选型指南：不同需求用户如何选择（入门/需电量统计/户外无WiFi）
  - 价格定位分层分析（推测逻辑）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 对比表格维度完整（≥10个对比项）
  - `human-judgement` TR-6.2: 对比结果准确，与各产品单独解析章节一致
  - `human-judgement` TR-6.3: 选型指南清晰，给出不同场景的明确推荐
  - `programmatic` TR-6.4: 表格格式规范，Markdown表格渲染正确
- **Notes**: 表格是本章核心，要做到一眼看清差异

## [ ] Task 7: 编写核心技术特性深度解析章节
- **Priority**: medium
- **Depends On**: [Task 6]
- **Description**: 
  - 蓝牙闪连配网技术：对比传统WiFi配网的优势，配网流程简化
  - 本地定时机制：解释为什么断网仍能运行（定时任务存储在本地）
  - 断电记忆功能：断电恢复后自动恢复之前状态的实现逻辑
  - 延时断电保护：关机3分钟后断电的设计考量（保护硬盘/主机）
  - 用电安全设计体系：从材质（V0阻燃PC）、结构（一体化铜带）、防护（安全门/浪涌）到智能保护（过载）的多层防护
- **Acceptance Criteria Addressed**: [AC-5, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 每个技术特性说明解决的用户痛点
  - `human-judgement` TR-7.2: 本地定时"断网仍运行"的技术原理解释清晰
  - `human-judgement` TR-7.3: 延时断电3分钟的原因解释清楚（保护电脑硬件）
  - `human-judgement` TR-7.4: 安全防护体系分层说明，从物理层到智能层
- **Notes**: 技术解析要有深度但不晦涩，让读者理解"为什么这样设计"

## [ ] Task 8: 编写远程开机技术原理与AC Recovery章节
- **Priority**: high
- **Depends On**: [Task 7]
- **Description**: 
  - 远程开机的完整流程：APP发指令→插座通电→主板触发AC Recovery→电脑开机
  - AC Recovery（交流电恢复）技术原理解释：BIOS设置选项的作用
  - 主板兼容性说明：为什么需要主板支持，如何检查自己的主板是否支持
  - 延时断电保护的必要性：为什么关机后要等3分钟再切断电源
  - 提供官方AC Recovery设置指南链接
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 远程开机流程描述完整，逻辑清晰
  - `human-judgement` TR-8.2: AC Recovery概念解释通俗易懂，包含BIOS设置说明
  - `programmatic` TR-8.3: 包含官方AC Recovery设置指南链接（http://url.oray.com/aYJHJr）
  - `human-judgement` TR-8.4: 明确标注不兼容的可能情况和解决方向
- **Notes**: 这是核心功能，必须讲解清楚，很多用户会卡在这里

## [ ] Task 9: 编写应用场景实战分析章节
- **Priority**: medium
- **Depends On**: [Task 8]
- **Description**: 
  - 远程办公场景：人不在公司紧急开电脑远程处理工作（三款通用）
  - 游戏预开机场景：回家前远程开机，到家直接玩（C1Pro/C2适合）
  - 定时开关场景：早上定时开电脑/台灯，到公司直接进入工作（三款通用）
  - 小家电倒计时场景：睡前加湿器/台灯定时关闭（三款通用）
  - 户外浇灌场景：远程控制水泵，无需亲临现场（仅C4）
  - 阳台/信号弱场景：WiFi信号差也能远程控制（仅C4）
  - 路由器重启场景：人在外面路由器死机，远程断电重启恢复网络（C4最佳）
  - 设备用电监控场景：查看电脑/设备每日/每周/月用电量（C2/C4）
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 至少覆盖8个典型应用场景
  - `human-judgement` TR-9.2: 每个场景描述清楚"什么痛点→用什么产品→怎么解决"
  - `human-judgement` TR-9.3: 明确标注哪些场景仅限C4支持
  - `human-judgement` TR-9.4: 场景描述具有画面感，用户能代入自身情况
- **Notes**: 场景是用户最关心的部分，要具体、实用、有代入感

## [ ] Task 10: 编写产品矩阵洞察与价值主张章节
- **Priority**: medium
- **Depends On**: [Task 9]
- **Description**: 
  - 产品矩阵分层逻辑：C1Pro（基础远程开关）→ C2（+电量统计）→ C4（+4G+户外+过载保护）的阶梯式布局
  - 差异化策略分析：从室内到户外、从基础到增强、从WiFi到4G的场景覆盖
  - 与向日葵生态的协同：智能插座如何与向日葵远程控制软件形成"软件+硬件"闭环
  - 产品设计哲学：简约实用、安全第一、场景细分
  - 商业价值分析：硬件作为远控生态入口的战略意义
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 产品分层逻辑分析清晰，能看出三款产品的定位差异
  - `human-judgement` TR-10.2: 生态协同分析说明"插座不是孤立产品，是远控生态一部分"
  - `human-judgement` TR-10.3: 洞察有深度，不只是复述功能，而是分析产品策略
- **Notes**: 这是体现"深度洞察"的章节，要有产品经理视角的分析

## [ ] Task 11: 编写用电安全与使用注意事项章节
- **Priority**: high
- **Depends On**: [Task 10]
- **Description**: 
  - 电流功率限制警告：仅支持10A，阻性2500W/感性850W/容性850W
  - 禁止使用场景：16A大功率电器（空调/电热水器）、新能源车充电（特别强调严禁）
  - WiFi网络限制：仅支持2.4G WiFi，不支持5G/WiFi6/认证网络（C1Pro/C2）
  - 工作温度范围：C1Pro/C2为-10~40℃，C4扩展到-10~50℃
  - 户外使用注意事项：C4虽支持户外但需注意温度限制
  - 使用建议：适合设备类型（电脑/台灯/路由器/小家电等）列表
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 安全警告使用醒目的提示格式（如> ⚠️ 警告）
  - `human-judgement` TR-11.2: 明确列出禁止使用场景，特别是新能源车充电的严禁提示
  - `programmatic` TR-11.3: 功率限制数据准确（2500W阻性/850W感性容性）
  - `human-judgement` TR-11.4: 网络限制说明清晰（2.4G/WiFi6兼容模式等）
- **Notes**: 安全无小事，警告必须明确醒目，这是硬性要求

## [ ] Task 12: 编写常见问题FAQ章节
- **Priority**: medium
- **Depends On**: [Task 11]
- **Description**: 
  - 配网失败怎么办？（检查2.4G WiFi、WiFi5兼容模式、蓝牙是否开启）
  - 为什么开不了机？（检查主板AC Recovery是否开启、兼容性问题）
  - 电量统计数据准确吗？（仅供参考，以电力部门为准）
  - C4的流量用完了怎么办？（3年后10元/年续费）
  - 可以接大功率电器吗？（10A限制说明，16A电器禁用）
  - 定时断网了还能用吗？（本地定时，断网仍运行）
  - 户外使用要注意什么？（温度范围、防水问题）
  - 指示灯晚上太亮怎么办？（支持指示灯开关）
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-12.1: FAQ覆盖至少8个常见问题
  - `human-judgement` TR-12.2: 回答实用，能解决用户实际疑惑
  - `human-judgement` TR-12.3: 问题符合真实用户可能遇到的场景
- **Notes**: FAQ要站在用户角度思考，问真实会遇到的问题

## [ ] Task 13: 编写资源链接章节
- **Priority**: low
- **Depends On**: [Task 12]
- **Description**: 
  - 三个产品官方页面链接
  - C1Pro使用手册链接
  - C2使用手册链接
  - AC Recovery设置指南链接
  - 向日葵远程控制软件下载
  - 向日葵官网首页
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-13.1: 包含三个产品官方页URL
  - `programmatic` TR-13.2: 包含使用手册链接（C1Pro: http://url.oray.com/scIHra, C2: http://url.oray.com/JJZXJr）
  - `programmatic` TR-13.3: 包含AC Recovery设置指南链接
  - `programmatic` TR-13.4: 所有链接URL正确无误
- **Notes**: 链接必须准确可访问

## [ ] Task 14: 更新知识库索引
- **Priority**: medium
- **Depends On**: [Task 13]
- **Description**: 
  - 在 docs/knowledge/README.md 的 learning 分类表格中添加新条目
  - 条目信息：标题、摘要、日期（2026-07-04）、标签
  - 摘要需准确概括文档内容
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-14.1: docs/knowledge/README.md 中learning分类新增了向日葵智能插座条目
  - `human-judgement` TR-14.2: 条目格式与现有条目一致（标题/摘要/日期/标签四列）
  - `programmatic` TR-14.3: 链接指向正确的wiki文件路径
- **Notes**: 严格遵循现有索引格式，不要破坏表格结构

## [ ] Task 15: 最终文档质量检查
- **Priority**: high
- **Depends On**: [Task 14]
- **Description**: 
  - 通读全文检查逻辑连贯性
  - 核对所有技术参数准确性
  - 检查所有锚点链接有效性
  - 确认安全警告醒目
  - 检查YAML frontmatter和文件命名规范
  - 运行文件名规范检查脚本
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12]
- **Test Requirements**:
  - `programmatic` TR-15.1: 文件名符合kebab-case规范（sunlogin-smart-socket-wiki.md）
  - `human-judgement` TR-15.2: 全文无明显逻辑矛盾或内容重复
  - `human-judgement` TR-15.3: 所有技术参数与网页提取内容一致
  - `human-judgement` TR-15.4: 安全提示充分醒目
  - `programmatic` TR-15.5: 文档无语法错误或格式问题
- **Notes**: 这是交付前最后一道检查，确保质量达标

# 向日葵USB远程摄像头SU1产品系统性学习与深度洞察 Wiki 教程 - 实施计划

## [x] Task 1: 创建wiki教程主文件基础框架
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 docs/knowledge/learning/ 目录下创建 sunlogin-camera-su1-wiki.md 文件
  - 添加 YAML frontmatter（title/source/date/tags）
  - 创建文档标题和原文参考链接区域
  - 搭建完整的目录导航系统（锚点链接）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于 docs/knowledge/learning/sunlogin-camera-su1-wiki.md
  - `programmatic` TR-1.2: YAML frontmatter格式正确，包含title/source/date/tags四个字段
  - `human-judgement` TR-1.3: 目录导航包含所有15个主要章节，锚点链接正确
- **Notes**: 参考现有wiki格式（如sunlogin-smart-socket-wiki.md），使用中文标题编号（一、二、三...）

## [x] Task 2: 编写概述与核心概念章节
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**: 
  - 编写第一章「产品概述与学习目标」：向日葵SU1摄像头定位、产品概览、学习目标
  - 编写第二章「核心概念解析」：解释UVC免驱、CMOS传感器、YUY2/MJPG、电子云台、双全向麦克风、视场角度(FOV)、TV畸变、数码变倍等关键术语
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 概述清晰说明SU1的产品定位（远程视频语音多面手）和学习价值
  - `human-judgement` TR-2.2: 核心概念术语解释准确，通俗易懂，非技术读者也能理解
  - `human-judgement` TR-2.3: UVC免驱概念解释包含技术原理说明（USB Video Class标准）
  - `human-judgement` TR-2.4: FOV视场角度（对角/水平/垂直）有通俗解释
- **Notes**: 术语解释避免过于技术化，配合实际应用场景说明

## [x] Task 3: 编写核心功能特性章节
- **Priority**: high
- **Depends On**: [Task 2]
- **Description**: 
  - 远程视频观看功能：通过向日葵软件远程观看画面+收听声音，多系统兼容说明，需搭配向日葵服务提示
  - 双全向麦克风：3米拾音距离，频响范围，适用远程会议/直播培训场景
  - USB免驱即插即用：UVC标准兼容，插入自动识别，无需安装驱动
  - 镜头角度调节：360度旋转，夹头180度调节，三种安装方式（PC夹持/三脚架/桌面摆放）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 四大核心功能每个都说明解决的痛点和价值
  - `human-judgement` TR-3.2: 明确标注"需搭配向日葵服务使用"的提示
  - `human-judgement` TR-3.3: 三种安装方式描述清晰，配合2米USB线长说明
  - `human-judgement` TR-3.4: 双全向麦克风与单麦克风区别说明清楚
- **Notes**: 重点突出"远程"能力，这是SU1区别于普通USB摄像头的核心

## [x] Task 4: 编写图像技术参数详解章节
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**: 
  - 图像传感器：1/3英寸CMOS高感光芯片，灵敏度<10Lux
  - 分辨率与帧率：2560×1440@30fps（400万像素）、1920×1080@60fps、多档分辨率支持
  - 镜头规格：焦距2.88mm、光圈F2.2、定焦镜头、最小对焦距离60cm
  - 视场角度：对角90°/水平82°/垂直52°，TV畸变<1%
  - 数码功能：4X数码变倍（720P下）、电子云台支持
  - 自动调节：自动增益、自动白平衡、自动/手动曝光、低亮度补偿
  - 可调节参数：亮度/对比度/色彩饱和度/清晰度/白平衡/手动曝光
  - 视频格式：YUY2/MJPG
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 技术参数准确引用官方数据（2560×1440、60fps@1080P、90°对角FOV、<1%畸变、2.88mm焦距、60cm最小对焦等）
  - `human-judgement` TR-4.2: 每个关键参数有解读说明其实际意义（如60fps的好处、90°FOV适合什么场景、畸变<1%意味着什么）
  - `human-judgement` TR-4.3: 使用表格整理参数便于查阅
  - `human-judgement` TR-4.4: 明确标注定焦镜头和最小对焦距离60cm的限制
- **Notes**: 参数必须准确，与网页提取内容一致，关键参数要解释"这对用户意味着什么"

## [x] Task 5: 编写音频技术参数详解章节
- **Priority**: high
- **Depends On**: [Task 4]
- **Description**: 
  - 麦克风配置：内置双全向麦克风设计
  - 拾音距离：50cm~300cm（3米拾音范围）
  - 频响范围：30Hz-16KHz
  - 音频采样率：支持16bit/16KHz/44.1KHz/48KHz等多档
  - 音频编码格式：PCM、UAC1.0兼容
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: 音频参数准确引用官方数据（双全向、3米拾音、30Hz-16KHz）
  - `human-judgement` TR-5.2: 解释双全向麦克风与单麦克风的区别（拾音范围更广、更适合会议场景）
  - `human-judgement` TR-5.3: 说明3米拾音距离的实际意义（适合中小型会议室）
- **Notes**: 音频是视频会议/远程指导场景的关键，要讲清楚音频规格的价值

## [x] Task 6: 编写硬件与系统兼容性章节
- **Priority**: high
- **Depends On**: [Task 5]
- **Description**: 
  - 系统兼容性：Windows 7/8.1/10+、macOS 10.14/10.15/11+、Android 5.0+（支持UVC）
  - 硬件要求：2.4GHz Intel Core 2 Duo或更高、2GB+内存、USB 2.0接口
  - 物理规格：USB 2.0 Type-A接口、机身一体式2米线长
  - 旋转调节：360度旋转可调、夹头180度调节
  - 安装方式：桌面摆放、显示器夹持、三脚架安装三种方式
  - 工作环境：工作温度0°~40°、工作湿度90%RH、存储温度-20°~60°、存储湿度95%RH
  - 其他特性：支持USB在线固件更新、蓝色LED工作指示灯、无隐私盖（NA）、最大功耗1.1W
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-6.1: 兼容性列表和硬件要求准确引用官方数据
  - `human-judgement` TR-6.2: 明确标注无隐私盖（NA）这一特性
  - `human-judgement` TR-6.3: 低功耗1.1W的优势说明（USB供电即可，无需额外电源）
  - `human-judgement` TR-6.4: 使用表格整理常规参数
- **Notes**: 客观列出所有参数，不回避无隐私盖等可能被视为不足的特性

## [x] Task 7: 编写四大核心应用场景章节
- **Priority**: high
- **Depends On**: [Task 6]
- **Description**: 
  - 远程视频指导：专业工程师不在现场时，通过摄像头画面远程指导，解决工业设备维护、IT技术支持等问题
  - 远程医疗诊断：专家远程观看医疗设备及诊断资料，为偏远地区医院提供远程医疗协助，分级诊疗场景
  - 远程视频监控：实时监控设备周围环境，无人值守时保护机房设备、实验室仪器、服务器等安全
  - 远程视频会议：在电脑/电视屏幕前进行远程会议，双全向麦克风+高清镜头实现如在同一会议室沟通
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 四大场景每个都描述清楚"什么痛点→怎么用SU1解决→带来什么价值"
  - `human-judgement` TR-7.2: 远程医疗场景突出对偏远地区的价值
  - `human-judgement` TR-7.3: 远程监控场景说明设备保护用途
  - `human-judgement` TR-7.4: 每个场景描述具有画面感，用户能代入
- **Notes**: 四大核心场景是产品定位的重点，突出"远程"能力带来的独特价值

## [x] Task 8: 编写扩展应用场景章节
- **Priority**: medium
- **Depends On**: [Task 7]
- **Description**: 
  - 网课教学：老师/学生远程上课，高清画面+清晰收音
  - 视频聊天：个人/家庭视频通话
  - 视频面试：企业远程招聘面试
  - 考试监考：在线考试远程监考场景
  - 人像采集：证件照/身份信息采集
  - 信息采集：文档/实物图像信息采集
  - 直播带货：电商直播场景使用
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 覆盖至少7个扩展应用场景
  - `human-judgement` TR-8.2: 每个场景简要说明适用性
  - `human-judgement` TR-8.3: 区分哪些场景普通摄像头也能做，哪些场景SU1的远程能力有优势
- **Notes**: 扩展场景体现产品的"多面手"定位，兼顾普通USB摄像头用途

## [x] Task 9: 编写页面布局与用户体验分析章节
- **Priority**: medium
- **Depends On**: [Task 8]
- **Description**: 
  - 信息架构分析：顶部导航→Banner区（产品定位+主图）→核心功能概览→四大核心场景（图文+视频）→硬件特性（镜头/麦克风/免驱/安装）→扩展应用→产品参数表→Footer生态矩阵
  - 视觉设计特点：蓝色主色调（向日葵品牌色）、大图+短句的简洁排版、场景配图直观
  - 营销逻辑：一句话定位→核心卖点→场景证明→技术参数支撑→生态引流
  - Footer贝锐生态矩阵：四大产品线（向日葵/蒲公英/花生壳/洋葱头）、购买渠道、下载入口、帮助支持、管理平台、账号管理、资质备案
  - 交互设计：产品演示视频、场景图标化展示、参数分类清晰
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 信息架构分层清晰（从吸引注意→建立兴趣→提供证据→促成转化）
  - `human-judgement` TR-9.2: Footer生态矩阵分析完整（四大产品线入口）
  - `human-judgement` TR-9.3: 营销逻辑分析专业，有产品页面设计视角
  - `human-judgement` TR-9.4: 客观评价页面UX的优点和可改进点
- **Notes**: UX分析要体现专业性，从产品营销页面设计角度分析，不只是罗列元素

## [x] Task 10: 编写产品设计与生态协同洞察章节
- **Priority**: medium
- **Depends On**: [Task 9]
- **Description**: 
  - 产品定位分析："远程视频语音多面手"的差异化定位——不是普通会议摄像头（强调远程能力），不是专业监控摄像头（强调办公/会议易用性），而是跨界融合
  - 软硬件协同价值：硬件（SU1）+软件（向日葵远程控制）形成闭环，这是核心竞争壁垒
  - 设计取舍分析：
    - 为什么是定焦？（成本控制、远程场景不需要特写、降低复杂度）
    - 为什么无隐私盖？（成本、2米外监控场景不需要、可手动旋转镜头）
    - 为什么低功耗1.1W？（USB2.0供电即可、兼容性好、长时间运行稳定）
    - 为什么三种安装方式？（适配多场景：桌面办公/会议/监控）
  - 贝锐生态协同：SU1作为视频入口，与向日葵远程控制、蒲公英组网、花生壳内网穿透形成协同，完善远程办公解决方案
  - 目标用户画像：IT运维人员、远程医疗工作者、中小企业主、远程教育从业者
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 产品定位分析清晰，说明与普通摄像头/监控摄像头的区别
  - `human-judgement` TR-10.2: 软硬件协同分析说明"SU1不是孤立硬件，是远控生态一部分"
  - `human-judgement` TR-10.3: 设计取舍分析有逻辑，每个取舍都说明背后的考量
  - `human-judgement` TR-10.4: 洞察有深度，不只是复述功能，而是分析产品策略
- **Notes**: 这是体现"深度洞察"的章节，要有产品经理视角的分析

## [x] Task 11: 编写使用注意事项与限制章节
- **Priority**: high
- **Depends On**: [Task 10]
- **Description**: 
  - 服务依赖提示：必须搭配向日葵服务/软件才能实现远程观看功能，单独使用仅能作为普通USB摄像头
  - 镜头限制：定焦镜头，最小对焦距离60cm，不适合近距离特写
  - 隐私提示：无物理隐私盖设计，注意使用场景隐私保护；监控使用需遵守法律法规
  - 接口限制：仅USB 2.0，非USB 3.0（但带宽足够支持1080P60fps）
  - 工作环境：工作温度0-40℃，仅适合室内使用，非户外防水设计
  - 系统兼容性：注意最低系统版本要求（Windows 7/macOS 10.14/Android 5.0）
  - 音频建议：3米拾音适合中小型会议室，大型会议室建议搭配扩展麦克风
  - 监控使用提示：遵守隐私保护相关法律法规，不得用于非法监控
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 服务依赖提示醒目
  - `human-judgement` TR-11.2: 明确标注定焦60cm最小对焦距离限制
  - `human-judgement` TR-11.3: 无隐私盖的客观说明和隐私使用建议
  - `human-judgement` TR-11.4: 法律法规合规提示（隐私保护）
  - `human-judgement` TR-11.5: 室内使用限制明确（非户外防水）
- **Notes**: 客观呈现产品限制，不回避设计取舍，安全/合规提示必须明确

## [x] Task 12: 编写常见问题FAQ章节
- **Priority**: medium
- **Depends On**: [Task 11]
- **Description**: 
  - SU1可以当普通USB摄像头用吗？（可以，UVC标准兼容，无需驱动）
  - 必须用向日葵软件吗？（远程功能必须搭配，本地使用不需要）
  - 支持哪些系统？（Windows 7+/macOS 10.14+/Android 5.0+）
  - 为什么电脑识别不到摄像头？（检查USB连接、系统版本、UVC兼容）
  - 为什么没有声音/麦克风不工作？（检查系统音频设置、麦克风权限、应用选择SU1麦克风）
  - 可以拍清楚近处的文字吗？（定焦60cm最小距离，太近会模糊）
  - 支持变焦吗？（支持4X数码变倍，仅在720P分辨率下）
  - 怎么安装固定？（三种方式：桌面摆放/显示器夹持/三脚架）
  - 有隐私盖吗？（没有，可通过旋转镜头或软件关闭实现隐私保护）
  - 可以户外使用吗？（不建议，工作温度0-40℃，无防水设计）
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-12.1: FAQ覆盖至少10个常见问题
  - `human-judgement` TR-12.2: 回答实用，能解决用户实际疑惑
  - `human-judgement` TR-12.3: 问题符合真实用户可能遇到的场景
- **Notes**: FAQ要站在用户角度思考，问真实会遇到的问题

## [x] Task 13: 编写资源链接章节
- **Priority**: low
- **Depends On**: [Task 12]
- **Description**: 
  - SU1产品官方页面链接
  - 向日葵远程控制软件下载页面
  - 向日葵官网首页
  - 贝锐向日葵管理平台
  - 向日葵硬件产品总览页面
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-13.1: 包含产品官方页URL（https://sunlogin.oray.com/hardware/camera-su1）
  - `programmatic` TR-13.2: 包含客户端下载链接
  - `programmatic` TR-13.3: 所有链接URL正确无误
- **Notes**: 链接必须准确可访问

## [x] Task 14: 更新知识库索引
- **Priority**: medium
- **Depends On**: [Task 13]
- **Description**: 
  - 在 docs/knowledge/README.md 的 learning 分类表格中添加新条目
  - 条目信息：标题、摘要、日期（2026-07-04）、标签
  - 摘要需准确概括文档内容
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-14.1: docs/knowledge/README.md 中learning分类新增了向日葵SU1摄像头条目
  - `human-judgement` TR-14.2: 条目格式与现有条目一致（标题/摘要/日期/标签四列）
  - `programmatic` TR-14.3: 链接指向正确的wiki文件路径
- **Notes**: 严格遵循现有索引格式，不要破坏表格结构

## [x] Task 15: 最终文档质量检查
- **Priority**: high
- **Depends On**: [Task 14]
- **Description**: 
  - 通读全文检查逻辑连贯性
  - 核对所有技术参数准确性（与defuddle提取和浏览器快照内容比对）
  - 检查所有锚点链接有效性
  - 确认注意事项/限制/合规提示醒目
  - 检查YAML frontmatter和文件命名规范
  - 运行文件名规范检查脚本
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12]
- **Test Requirements**:
  - `programmatic` TR-15.1: 文件名符合kebab-case规范（sunlogin-camera-su1-wiki.md）
  - `human-judgement` TR-15.2: 全文无明显逻辑矛盾或内容重复
  - `human-judgement` TR-15.3: 所有技术参数与网页提取内容一致
  - `human-judgement` TR-15.4: 注意事项和合规提示充分醒目
  - `programmatic` TR-15.5: 文档无语法错误或格式问题
- **Notes**: 这是交付前最后一道检查，确保质量达标

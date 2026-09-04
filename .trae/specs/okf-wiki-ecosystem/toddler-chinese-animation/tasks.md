# 宝宝中国风动漫 - 实施计划

## [x] Task 1: 第一性原理分析（F阶段）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 从第一性原理出发，拆解2岁幼儿的认知特点、视觉偏好、注意力持续时间
  - 分析中国风元素中哪些最适合低龄儿童（圆润造型、鲜艳柔和色彩、吉祥寓意）
  - 明确视频的核心设计原则：简单、缓慢、温馨、可爱
  - 确定视频比例（推荐竖屏9:16）、主角（推荐圆滚滚小熊猫）、场景（祥云/红灯笼/梅花等简单背景）
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 输出一份清晰的设计原则文档，包含至少5条幼儿内容设计准则
  - `human-judgement` TR-1.2: 确定的主角和场景符合"可爱、简单、中国风"三要素
- **Notes**: 参考儿童发展心理学中关于2岁幼儿的视觉认知研究结论

## [x] Task 2: 对抗审查（V阶段）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 从四个视角进行对抗审查：
    1. **幼儿视角**：会不会有任何让宝宝害怕的元素？
    2. **家长视角**：内容是否安全、积极、有文化美感？
    3. **文化专家视角**：中国风元素使用是否恰当，有无文化误读？
    4. **技术视角**：seedance/seedream能否实现预期效果，有无技术风险？
  - 识别潜在风险点并制定规避方案
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 完成四视角审查清单，每个视角至少列出2个检查点
  - `human-judgement` TR-2.2: 识别出的风险点都有对应的规避方案
- **Notes**: 重点排查：色彩是否刺眼、动作是否太快、造型是否怪异、场景是否阴暗

## [x] Task 3: 洞察落地 - 创意设计与提示词（I阶段）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 设计具体的动画场景：圆滚滚的可爱小熊猫在祥云上轻轻摇摆，旁边飘着小红灯笼，背景是柔和的中国风山水
  - 编写详细的中文提示词（prompt）用于seedream生成关键帧
  - 编写详细的视频生成提示词用于seedance，明确动作描述（轻轻摇摆、缓慢漂浮、柔和微笑等）
  - 确定视频参数：时长8秒、分辨率720p、比例9:16
- **Acceptance Criteria Addressed**: [AC-2, AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 图片提示词包含中国风、可爱、柔和色彩、圆润造型等关键词
  - `human-judgement` TR-3.2: 视频提示词详细描述缓慢、柔和的动作，无快速运动
  - `human-judgement` TR-3.3: 提示词全部使用中文描述
- **Notes**: 提示词要强调"适合2岁宝宝观看"、"温馨可爱"、"色彩柔和"

## [x] Task 4: 使用seedream生成关键帧概念图
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 使用seedream（GenerateImage工具）基于提示词生成1-2张关键帧概念图
  - 图片尺寸选择portrait_4_3或portrait_16_9（适合竖屏）
  - 如生成效果不理想，调整提示词重新生成（最多尝试3次）
  - 保存最佳概念图作为视频生成的参考
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 成功生成至少1张PNG/JPG图片文件
  - `human-judgement` TR-4.2: 图片中国风明显、主角可爱、色彩柔和、整体温馨
- **Notes**: 输出路径：d:\spaces\SpecWeave\playground\toddler-animation\ 目录下

## [x] Task 5: 使用seedance生成动漫视频
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 使用seedance（GenerateVideo工具）基于概念图和提示词生成最终视频
  - 视频参数：时长8秒、分辨率720p、比例9:16
  - 提示词详细描述：圆滚滚的小熊猫轻轻摇摆，小灯笼缓慢漂浮，祥云轻柔飘动，整体动作非常缓慢柔和
  - 如首次效果不理想，调整提示词重新生成（最多尝试2次）
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 成功生成MP4视频文件，时长在5-10秒范围内
  - `human-judgement` TR-5.2: 视频动作流畅、无卡顿、无怪异变形
  - `human-judgement` TR-5.3: 视频整体氛围温馨可爱，符合2岁幼儿观看
- **Notes**: 将概念图作为image_paths传入GenerateVideo，保持风格一致性

## [x] Task 6: 最终验证与原子交付（C阶段）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 播放视频进行最终质量检查
  - 验证所有验收标准是否通过
  - 整理产出物：概念图+视频文件
  - 输出项目总结，说明文件位置和使用建议
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 对照checklist.md完成所有检查点验证
  - `programmatic` TR-6.2: 所有产出文件都保存在指定目录
  - `human-judgement` TR-6.3: 最终视频可以给2岁宝宝观看，无不适宜内容
- **Notes**: 交付目录：d:\spaces\SpecWeave\playground\toddler-animation\

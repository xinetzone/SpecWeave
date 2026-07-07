# 更新向日葵Wiki：电脑远程控制手机功能 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 更新Wiki元数据和导航
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 更新sunlogin-comprehensive-analysis-wiki.md的YAML frontmatter，在source字段中添加新URL `https://service.oray.com/question/17615.html`
  - 更新文档顶部的目录导航，在第三章位置添加"3.2.3 移动端远程控制"子章节链接
  - 读取现有Wiki的完整结构，确认插入位置的准确性
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: YAML frontmatter格式正确，source字段包含新URL
  - `programmatic` TR-1.2: 目录导航中存在新章节链接，锚点正确
  - `human-judgement` TR-1.3: 插入位置与现有章节编号体系一致
- **Notes**: 先读取文件确认章节编号，3.2.1是核心功能矩阵，3.2.2是16.5版本新特性，新章节应为3.2.3

## [x] Task 2: 编写移动端远程控制核心内容
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在第三章3.2节末尾（3.2.2之后）新增"3.2.3 移动端远程控制"子章节
  - 结构化呈现以下内容：
    - 功能概述与服务等级要求（免费用户仅观看、付费/移动授权可控制）
    - 服务等级权限矩阵表（尝鲜版/瓜子会员/超级会员/商业&企业的功能和设备数量）
    - 手机端设置步骤（安装APP、登录、设置访问密码、三种被控方式对比表：Root权限/辅助服务/UUPro硬件）
    - 电脑端操作流程（安装客户端、登录、设备列表发起远控）
    - Android/iOS平台功能差异对比表（iOS需Q1硬件、仅桌面控制/观看；安卓支持摄像头/远程文件）
    - 三大核心功能说明（桌面控制、摄像头、远程文件）
    - 常见问题解决（远程文件路径不合法需开启"访问所有文件权限"）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 章节编号为3.2.3，层级正确
  - `human-judgement` TR-2.2: 信息点覆盖完整（对照官方文档7大信息点）
  - `programmatic` TR-2.3: 包含至少4个表格（权限矩阵、被控方式、平台差异、设备数量）
  - `human-judgement` TR-2.4: 语言风格与现有Wiki保持一致，使用中文书面语
  - `programmatic` TR-2.5: 外部链接格式正确（使用<>包裹URL）

## [x] Task 3: 补充移动端远控产品设计洞察
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 在第七章"产品哲学与设计原则"中，融入移动端远控场景体现的设计原则
  - 或在新增的3.2.3章节末尾添加"移动端远控设计洞察"子小节
  - 萃取以下洞察方向：
    - 权限分层的精细设计（免费观看vs付费控制，既做引流又不损害核心价值）
    - 多路径适配策略（Root/辅助服务/UUPro硬件三种被控方式，覆盖不同用户场景）
    - 平台差异的务实应对（iOS封闭性的硬件兜底方案Q1）
    - 系统权限的渐进式获取（远程文件需要单独开启"访问所有文件权限"）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-3.1: 洞察内容与现有第七章风格一致，不只是功能罗列
  - `human-judgement` TR-3.2: 至少提炼3个有价值的设计洞察
  - `human-judgement` TR-3.3: 洞察能够与已有原则（本地能力保底、场景化设计等）形成呼应

## [x] Task 4: 更新FAQ和相关资源章节
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 在第十一章"常见问题解答（FAQ）"中添加关于手机远控的Q&A
  - 建议问题：
    - Q：免费版可以远程控制手机吗？
    - Q：iPhone可以被远程控制吗？需要什么条件？
    - Q：远程文件功能提示"路径不合法"怎么办？
    - Q：不同会员等级可以控制多少台手机？
  - 在第十二章"相关资源链接"的官方资源部分添加"电脑远程控制手机官方教程"链接
  - 更新Wiki末尾的版本说明，标注本次更新日期和内容
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: FAQ章节新增至少3个手机远控相关问题
  - `programmatic` TR-4.2: 相关资源章节包含新的官方文档链接
  - `human-judgement` TR-4.3: FAQ回答准确、简洁，与现有FAQ风格一致
  - `programmatic` TR-4.4: 版本说明更新，标注更新日期和内容

## [x] Task 5: 一致性验证和质量检查
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 运行文件名规范检查脚本，确认文件命名符合kebab-case
  - 检查所有内部链接（目录导航锚点）的有效性
  - 检查所有外部URL格式正确
  - 通读全文，确保格式一致性（标题层级、表格样式、加粗使用等）
  - 验证信息准确性：对照官方文档确认所有关键数据（设备数量、系统要求、功能限制等）
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件名通过规范检查（python .agents/scripts/check-filename-convention.py）
  - `programmatic` TR-5.2: 所有Markdown链接格式正确
  - `human-judgement` TR-5.3: 全文通读无明显格式不一致问题
  - `human-judgement` TR-5.4: 关键数据与官方文档核对一致
- **Notes**: 使用现有的检查脚本进行自动化验证

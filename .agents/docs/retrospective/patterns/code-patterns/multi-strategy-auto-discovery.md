---
id: "multi-strategy-auto-discovery"
title: "多策略自动发现模式"
type: "code"
date: "2026-08-02"
maturity: "L2-validated"
source: "retrospective-nativebuild-automation-20260802"
related_patterns: ["version-priority-sorting", "dynamic-path-derivation", "platform-aware-dependency-detect"]
tags: ["powershell", "auto-discovery", "environment-detection", "cross-machine", "portability", "conda", "visual-studio"]
validation_count: 2
reuse_count: 2
---

# 多策略自动发现模式

## 触发场景
- 当需要在不同机器上定位外部依赖（Python、Conda、Visual Studio、JDK、SDK等），安装位置和配置因用户/机器而异时
- 适用于：跨机器可移植脚本、构建工具、环境配置自动化、开发者工具引导脚本
- 不适用于：容器化环境（路径固定）、CI/CD流水线（环境可预测）、已知固定部署路径的生产环境

## 核心做法
1. **策略注册表**：定义有序的发现策略列表，按可靠性从高到低排列（显式Hint参数 → 环境变量 → 标准目录扫描 → PATH查找 → 配置文件）
2. **候选收集**：每个策略产生0个或多个候选路径，使用HashSet数据结构自动去重
3. **有效性验证**：对每个候选执行路径存在性检查（Test-Path）+ 关键文件存在性验证（如python.exe、DevShell.dll等标志性文件）
4. **版本匹配**：执行目标程序获取版本号（如`python --version`），解析为可比较的数值类型，过滤不符合最低版本要求的候选
5. **名称偏好匹配**：如指定了NamePattern正则，优先返回目录名称匹配该模式的候选（如名称含"314"或"py314"的环境）
6. **兜底返回**：若无名称偏好匹配，返回第一个版本达标的候选；记录所有策略的执行日志便于诊断

## 反模式（不要这么做）
- ❌ 硬编码单一绝对路径（如`D:\Users\xinzo\anaconda3`）：换机器立即失效，维护成本极高
- ❌ 只查一种策略（如只查环境变量不查磁盘）：环境变量未设置时直接失败，鲁棒性差
- ❌ 不验证候选有效性：目录存在但不是有效安装（空目录、权限不足、关键文件缺失），后续步骤出现晦涩错误
- ❌ 版本比较使用字符串排序：如`"2022" > "18"`字符串比较为true，但实际版本号18 > 17（VS 2022是v17）
- ❌ 发现失败时不输出诊断日志：用户无法知道哪个策略失败、为什么失败，只能盲猜

## 检验标准
做完之后怎么知道做对了？
- 标准1：在至少2台不同配置的机器上（不同安装路径、不同版本组合）无需修改脚本即可成功定位依赖
- 标准2：显式Hint参数优先级最高，指定路径时跳过所有自动发现
- 标准3：每个候选都经过关键文件验证，无效候选被正确过滤
- 标准4：版本比较使用数值类型而非字符串，多版本共存时选择正确版本
- 标准5：发现过程输出结构化日志，失败时能明确指出哪个策略失败、有哪些候选被过滤

## 迁移示例
这个模式还能用在什么其他场景？
- 场景1（跨领域）：JDK/Android SDK/Node.js等开发工具的多版本自动发现
- 场景2（系统管理）：Windows服务、SQL Server实例、IIS站点的自动发现
- 场景3（非软件领域）：简历筛选系统——多渠道收集简历（招聘网站→内推→猎头）→验证简历真实性→匹配技能关键词→排序推荐
- 场景4（生活场景）：找餐厅——朋友推荐→大众点评→地图搜索→验证营业状态→按口味偏好排序→选择最近的一家

## 参考实现
- PowerShell实现：[NativeBuild.psm1](file:///d:/spaces/SpecWeave/.agents/scripts/lib/NativeBuild.psm1) 中 `Get-CondaRoots`、`Find-CondaEnvPython`、`Find-VisualStudio` 函数
- 应用案例：caffe-ffi、npu-ffi、demo-ffi、xuan-ext-demo四个C++扩展项目的构建脚本

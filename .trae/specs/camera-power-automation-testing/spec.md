---
id: "camera-power-automation-testing-spec"
title: "摄像头通断电自动化测试系统 PRD"
date: "2026-07-06"
---

# 摄像头通断电自动化测试系统 - Product Requirement Document

## Overview
- **Summary**: 基于涂鸦智能插座OpenAPI构建一套完整的摄像头通断电自动化测试框架，通过Python API控制智能插座开关状态，实现对连接于插座上的摄像头设备进行自动化电源通断控制，支持冷启动测试、压力测试、批量设备测试等场景，并提供完善的状态监测、异常处理、日志记录和测试报告功能。
- **Purpose**: 解决摄像头设备电源相关测试场景的自动化需求，包括冷启动稳定性测试、断电恢复验证、异常断电兼容性测试、长时间运行可靠性测试等，替代手动插拔电源的低效操作，确保测试过程可重复、结果可验证。
- **Target Users**: 测试工程师、QA团队、自动化测试框架开发者。

## Goals
- 基于现有[camera_power.py](file:///d:/AI/apps/camera-power-controller/camera_power.py)进行增强和完善，提供生产级别的自动化测试能力
- 实现涂鸦智能插座的稳定通信，包含token自动刷新、失败重试、状态验证机制
- 提供完整的摄像头状态监测扩展点（电源状态 + 设备就绪检测钩子）
- 实现结构化测试用例框架，支持冷启动、压力循环、批量测试等标准测试场景
- 提供完善的异常处理、重试机制和结构化日志记录
- 提供测试执行结果的可验证输出（测试报告、JSON结果、pytest集成）
- 支持pytest无缝集成，可作为fixture用于现有测试框架

## Non-Goals (Out of Scope)
- 不实现摄像头视频流/图像质量检测功能（仅提供钩子，由测试用例自行实现摄像头业务验证）
- 不实现向日葵P1Pro/P4等非涂鸦生态设备的直接API控制
- 不实现Web UI或图形界面（命令行+Python API+pytest集成）
- 不实现分布式多机测试调度（单机多设备控制）
- 不实现涂鸦设备配网功能（假设设备已在涂鸦APP中完成配网绑定）

## Background & Context
- 现有基础：项目中已有[camera_power.py](file:///d:/AI/apps/camera-power-controller/camera_power.py)实现了基础的开机/关机/重启/状态查询功能，以及[test_examples.py](file:///d:/AI/apps/camera-power-controller/test_examples.py)示例代码
- 涂鸦API：项目中已有[tuya_api.py](file:///d:/AI/.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py)SDK封装，支持HMAC-SHA256签名、自动区域检测、HTTP重试
- 已知问题：根据历史经验，涂鸦API存在"返回成功但设备未动作"、token失效、DP点映射错误等问题，需要在框架层做状态验证和错误处理
- 硬件需求：使用涂鸦生态WiFi智能插座（category='cz'），单孔或多孔均可，支持switch_1等标准DP点

## Functional Requirements
- **FR-1**: 智能插座通信与控制
  - FR-1.1: 支持涂鸦OpenAPI鉴权，API Key通过环境变量或配置文件传入
  - FR-1.2: 支持设备发现，自动列出账号下所有可用智能插座
  - FR-1.3: 支持单插孔独立控制（switch_1/switch_2等DP点可配置）
  - FR-1.4: 每次控制操作后必须进行状态验证（查询真实设备状态），不能仅依赖API返回值
  - FR-1.5: 支持失败自动重试（可配置重试次数和间隔）

- **FR-2**: 摄像头状态监测机制
  - FR-2.1: 电源状态监测：通过涂鸦API查询插座真实开关状态
  - FR-2.2: 设备就绪检测钩子：提供可扩展的回调机制，允许测试用例注入摄像头业务就绪检测逻辑（如ping IP、检测RTSP流、HTTP接口探测等）
  - FR-2.3: 带超时的状态等待机制：支持轮询等待电源状态变化和设备就绪
  - FR-2.4: 支持在线状态检测，设备离线时明确报错而非静默失败

- **FR-3**: 测试用例框架
  - FR-3.1: 冷启动测试用例：断电→等待→上电→等待启动→验证，支持配置断电时间和启动等待时间
  - FR-3.2: 压力循环测试：支持N次通断电循环，统计成功率、失败次数、平均耗时
  - FR-3.3: 批量多摄像头测试：支持同时配置多个摄像头，支持顺序/并行（ stagger 错开）控制
  - FR-3.4: 异常断电测试：支持随机断电时间、异常场景模拟
  - FR-3.5: 测试用例基类：提供标准化的setUp/tearDown、前置检查、后置清理

- **FR-4**: 异常处理与可靠性
  - FR-4.1: 网络异常处理：API超时、连接失败自动重试
  - FR-4.2: token失效处理：识别认证错误，清空token重新获取（如SDK支持）
  - FR-4.3: 设备离线处理：检测到设备离线时终止测试并记录失败原因
  - FR-4.4: DP点校验：启动时验证设备支持的switch属性，避免下发不存在的DP点
  - FR-4.5: 安全边界：限制最大重试次数、最大等待时间，防止无限循环

- **FR-5**: 日志记录与测试报告
  - FR-5.1: 结构化日志：记录每次操作的时间戳、设备名、操作类型、参数、结果、耗时
  - FR-5.2: 日志级别支持：DEBUG/INFO/WARNING/ERROR
  - FR-5.3: 测试结果输出：支持JSON格式测试结果输出，包含成功/失败统计、失败详情
  - FR-5.4: 控制台实时输出：测试执行过程中实时打印进度和状态
  - FR-5.5: 日志文件输出：支持将日志写入文件，便于事后分析

- **FR-6**: 配置管理
  - FR-6.1: JSON配置文件支持：摄像头设备映射、等待时间、重试次数等可配置
  - FR-6.2: 环境变量支持：敏感信息（API Key）优先从环境变量读取
  - FR-6.3: 配置模板生成：提供init-config命令生成配置模板
  - FR-6.4: 多环境支持：可配置不同环境的设备列表

- **FR-7**: pytest集成
  - FR-7.1: 提供pytest fixture示例，支持session/module/function级别的setup/teardown
  - FR-7.2: 测试失败时自动截取状态（电源状态、设备在线状态）
  - FR-7.3: 支持pytest参数化，便于多设备批量测试

## Non-Functional Requirements
- **NFR-1**: 可靠性：单次电源操作成功率>99%（含重试），状态验证准确率100%
- **NFR-2**: 可观测性：所有操作均有日志记录，失败有明确错误码和错误信息
- **NFR-3**: 可扩展性：摄像头就绪检测逻辑通过钩子注入，核心框架不耦合具体摄像头型号
- **NFR-4**: 易用性：提供清晰的CLI命令和Python API，5分钟内可完成首次配置和测试运行
- **NFR-5**: 可重复性：相同配置下多次运行结果一致，消除时序依赖导致的flaky测试
- **NFR-6**: 性能：单次状态查询API响应<3秒，单次控制操作（含验证）<10秒

## Constraints
- **Technical**: Python 3.8+，依赖requests库，基于现有[tuya_api.py](file:///d:/AI/.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py)SDK
- **Business**: 涂鸦智能插座需已在涂鸦智能APP中完成配网并绑定到对应账号
- **Dependencies**: 涂鸦OpenAPI可用性、网络连接稳定性、智能插座在线状态
- **Hardware**: 涂鸦生态WiFi智能插座（支持2.4GHz WiFi，category='cz'），摄像头设备支持AC Recovery或上电自启动

## Assumptions
- 用户已拥有涂鸦开发者账号并获取到End User API Key（sk-开头）
- 智能插座已完成配网并绑定到该API Key对应的账号下
- 摄像头设备在电源恢复后能够自动启动（或测试用例不要求验证摄像头业务就绪状态）
- 测试运行环境可以访问涂鸦OpenAPI端点（openapi.tuyacn.com等）
- 一个插座插孔对应一个摄像头设备（多孔插线板每个插孔独立配置）

## Acceptance Criteria

### AC-1: 基础电源控制功能
- **Given**: 已配置好涂鸦API Key和至少一个在线智能插座设备
- **When**: 调用power_on/power_off/power_cycle方法
- **Then**: 设备实际电源状态发生对应变化，且方法返回操作成功状态
- **Verification**: `programmatic`
- **Notes**: 每次操作后必须查询真实设备状态验证，不能仅依赖API返回success

### AC-2: 状态验证与可靠性
- **Given**: 设备在线且网络正常
- **When**: 电源控制指令发出后
- **Then**: 框架自动轮询设备状态直到状态匹配或超时，API短暂失败时自动重试
- **Verification**: `programmatic`
- **Notes**: 重试3次，每次间隔1秒；状态轮询超时可配置（默认30秒）

### AC-3: 设备就绪检测钩子
- **Given**: 测试用例注册了camera_ready_check回调函数
- **When**: 电源上电后
- **Then**: 框架自动调用回调检测摄像头是否真正就绪，回调返回True才认为测试通过
- **Verification**: `programmatic`
- **Notes**: 回调函数由测试用例实现（如ping IP、检测HTTP接口等）

### AC-4: 标准测试用例执行
- **Given**: 已配置测试参数（循环次数、等待时间等）
- **When**: 执行冷启动测试或压力循环测试
- **Then**: 测试按预设流程执行，完成后输出包含成功率、失败次数、耗时统计的测试报告
- **Verification**: `programmatic`
- **Notes**: 支持JSON格式报告输出

### AC-5: 异常处理
- **Given**: 设备离线、网络中断、API返回错误等异常场景
- **When**: 异常发生时
- **Then**: 框架捕获异常、记录详细错误日志、按策略重试或终止测试，不会无限挂起
- **Verification**: `programmatic`

### AC-6: 结构化日志
- **Given**: 任意测试执行过程
- **When**: 测试运行中
- **Then**: 所有操作（控制、查询、等待、重试、成功/失败）均产生带时间戳的结构化日志
- **Verification**: `human-judgment`
- **Notes**: 日志包含时间、级别、设备名、操作、结果、耗时等字段

### AC-7: CLI命令行可用
- **Given**: 已完成pip依赖安装
- **When**: 通过命令行执行camera_power.py相关命令
- **Then**: 支持discover/init-config/on/off/cycle/status/stress-test等命令，输出清晰
- **Verification**: `programmatic`

### AC-8: pytest集成
- **Given**: pytest环境中配置了camera controller fixture
- **When**: 运行pytest测试用例
- **Then**: fixture正确完成setup/teardown，测试用例可直接调用controller进行电源控制
- **Verification**: `human-judgment`

### AC-9: 文档与示例
- **Given**: 新用户首次使用
- **When**: 阅读README和示例代码
- **Then**: 可以在30分钟内完成配置并成功运行第一个自动化测试
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要支持多插孔插线板（如4孔）同时控制多个摄像头？（当前设计已支持通过switch_property配置）
- [ ] 是否需要支持定时测试（如指定时间执行、定时循环）？（暂不纳入，由调度系统负责）
- [ ] 是否需要收集电量统计数据（如插座支持）用于功耗分析？（作为FR-2扩展点，暂不强制）
- [ ] 摄像头就绪检测是否需要提供内置实现（如ICMP ping）？（提供可选内置ping，核心仍为钩子机制）

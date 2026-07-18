# 摄像头通断电自动化测试系统 - The Implementation Plan

## [ ] Task 1: 增强核心控制层 - 可靠性与状态验证增强
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 增强现有[camera_power.py](../../../apps/camera-power-controller/camera_power.py)的核心控制逻辑，修复历史经验中提到的问题
  - 启动时进行设备DP点校验：查询设备实际支持的properties，验证配置的switch_property是否存在
  - 设备在线状态检查：每次操作前先检查online字段，离线直接报错
  - 控制后强制状态验证：不是仅等待固定时间，而是轮询get_device_state直到状态匹配或超时
  - 细化异常类型：区分网络错误、设备离线、DP点不存在、token失效等不同错误
  - 优化重试逻辑：网络错误才重试，参数错误/DP点不存在不重试
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: 启动时如果switch_property不在设备实际properties列表中，抛出明确的配置错误
  - `programmatic` TR-1.2: 设备online=False时调用power_on/power_off，抛出DeviceOfflineError而非通用异常
  - `programmatic` TR-1.3: power_on操作后如果状态仍为OFF，在重试次数耗尽后返回False并记录警告
  - `programmatic` TR-1.4: 网络超时/5xx错误自动重试最多3次，4xx参数错误不重试
  - `human-judgement` TR-1.5: 代码审查确认没有"仅依赖API返回success就认为操作成功"的逻辑
- **Notes**: 基于`tuya_api.py`现有SDK进行封装，不修改SDK本身

## [ ] Task 2: 结构化日志系统实现
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现结构化日志模块logger.py，支持控制台彩色输出和文件输出
  - 日志格式包含：时间戳、日志级别、设备名、操作类型、耗时ms、结果状态
  - 日志级别：DEBUG（API请求详情）、INFO（操作开始/成功）、WARNING（重试）、ERROR（失败）
  - 每次电源操作记录：开始时间、结束时间、耗时、尝试次数、最终结果
  - 每次状态查询记录：查询结果、是否匹配期望状态
  - 支持通过配置文件设置日志级别和日志文件路径
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 调用power_on后日志包含INFO级别记录，包含设备名、操作类型、耗时
  - `programmatic` TR-2.2: 重试时输出WARNING级别日志，包含当前重试次数
  - `programmatic` TR-2.3: 操作失败时输出ERROR级别日志，包含错误原因
  - `programmatic` TR-2.4: 配置log_file路径后日志同时写入文件和控制台
  - `human-judgement` TR-2.5: 日志格式清晰，关键信息一目了然，便于排查问题

## [ ] Task 3: 摄像头就绪检测钩子机制
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在CameraPowerController中添加注册回调的方法：register_ready_check(camera_name, check_func)
  - check_func签名：Callable[[], bool]，返回True表示就绪，False表示未就绪
  - 新增power_on_and_wait_ready方法：上电后先等待电源状态为ON，再轮询调用check_func直到返回True或超时
  - 新增内置可选的ICMP ping检测：ping_camera(ip, timeout)作为参考实现
  - wait_for_state扩展支持业务就绪状态等待
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 注册check_func后，power_on_and_wait_ready会在电源ON后调用该函数
  - `programmatic` TR-3.2: check_func连续返回False直到超时，方法返回False并记录超时
  - `programmatic` TR-3.3: 未注册check_func时，power_on_and_wait_ready行为与power_on(wait=True)一致
  - `programmatic` TR-3.4: 内置ping检测函数在IP可达时返回True，不可达时返回False
  - `human-judgement` TR-3.5: API文档清晰说明如何自定义就绪检测函数

## [ ] Task 4: 测试用例框架与标准测试场景
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 创建test_framework.py，实现测试用例基类CameraPowerTest
  - 实现冷启动测试用例ColdBootTest：断电→等待off_time→上电→等待电源ON→等待摄像头就绪→记录结果
  - 实现压力循环测试StressTest：执行N次power_cycle，统计成功率、失败次数、每次耗时、总耗时
  - 实现批量多摄像头测试MultiCameraTest：支持顺序控制多个摄像头，支持stagger间隔避免同时上电冲击
  - 测试结果数据类：TestResult包含test_name、start_time、end_time、success、cycles_passed、cycles_failed、failures详情列表
  - 支持JSON格式测试报告输出
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: ColdBootTest执行流程严格按"断电→等待→上电→就绪"顺序
  - `programmatic` TR-4.2: StressTest(10)执行10次循环，返回TestResult包含success_count和failure_count
  - `programmatic` TR-4.3: 失败循环在failures列表中记录循环序号和失败原因
  - `programmatic` TR-4.4: 测试报告可导出为JSON格式，包含所有统计字段
  - `programmatic` TR-4.5: MultiCameraTest顺序执行时每个摄像头启动间隔为配置的stagger_seconds
  - `human-judgement` TR-4.6: 测试执行过程中控制台实时显示进度（如"Cycle 3/10: SUCCESS (2.3s)"）

## [ ] Task 5: CLI命令行增强
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 4
- **Description**:
  - 增强现有CLI，新增stress-test命令支持压力测试参数
  - 新增cold-boot命令执行冷启动测试
  - 新增--wait-ready选项支持等待摄像头就绪
  - 新增--log-file选项指定日志文件路径
  - 新增--json-output选项输出测试结果到JSON文件
  - discover命令增强：显示设备的properties列表，方便配置switch_property
  - 完善CLI帮助信息和使用示例
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: `--discover`输出每个插座的properties列表，显示可用的switch_X字段
  - `programmatic` TR-5.2: `--stress-test camera-01 --cycles 5`执行5次循环并输出统计结果
  - `programmatic` TR-5.3: `--json-output result.json`将测试结果写入JSON文件
  - `programmatic` TR-5.4: `--help`输出所有支持的命令和参数说明
  - `human-judgement` TR-5.5: CLI输出信息清晰，错误提示明确

## [ ] Task 6: pytest集成与fixture示例
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 创建conftest.py示例，提供camera_controller fixture
  - 支持session级别的setup（上电所有摄像头）和teardown（断电所有摄像头）
  - 测试失败时自动截图电源状态和设备信息附到报告
  - 创建pytest示例测试文件test_camera_power.py，包含冷启动、压力测试示例
  - 提供pytest.ini或pyproject.toml配置参考
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: fixture在测试session开始时上电，session结束时断电
  - `programmatic` TR-6.2: 测试函数可以通过参数注入controller对象直接使用
  - `programmatic` TR-6.3: 测试失败时日志中包含当时的电源状态和设备在线状态
  - `human-judgement` TR-6.4: 示例代码清晰，用户复制后修改设备配置即可运行

## [ ] Task 7: 配置管理增强与验证
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 增强配置文件支持：添加log_level、log_file、boot_timeout、ready_timeout、stagger_seconds等配置项
  - 添加配置验证逻辑：启动时校验所有必填字段，设备ID格式检查
  - 环境变量优先：TUYA_API_KEY、TUYA_CONFIG_PATH可覆盖配置文件
  - 更新config.example.json包含所有新配置项和注释说明
  - init-config命令生成包含所有新配置项的完整模板
- **Acceptance Criteria Addressed**: FR-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 配置文件缺少cameras字段时启动报错并给出明确提示
  - `programmatic` TR-7.2: 设置TUYA_API_KEY环境变量可以不配置config中的api_key
  - `programmatic` TR-7.3: --init-config生成的模板包含所有配置项和注释
  - `human-judgement` TR-7.4: 配置文件结构清晰，注释说明每个字段用途

## [ ] Task 8: 单元测试与集成测试
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - 为核心控制逻辑编写单元测试，使用mock模拟TuyaAPI
  - 测试正常流程：power_on/power_off/power_cycle成功场景
  - 测试异常场景：设备离线、网络超时、API返回错误、DP点不存在
  - 测试重试逻辑：验证失败重试、参数错误不重试
  - 测试状态验证：操作后状态不匹配时的超时处理
  - 测试日志模块：各日志级别输出正确
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 核心控制逻辑单元测试覆盖率≥80%
  - `programmatic` TR-8.2: 所有异常场景都有对应的测试用例
  - `programmatic` TR-8.3: mock API返回success但状态未变时，方法正确返回False
  - `programmatic` TR-8.4: 测试可独立运行，不依赖真实设备和网络

## [ ] Task 9: 文档与使用指南
- **Priority**: medium
- **Depends On**: Task 1-7
- **Description**:
  - 编写README.md使用文档
  - 快速开始章节：安装、配置、第一个测试（5分钟上手）
  - API参考文档：所有公开方法说明、参数、返回值、异常
  - CLI命令参考：所有命令和参数说明
  - 测试场景指南：冷启动测试、压力测试、批量测试、pytest集成的具体用法
  - 常见问题FAQ：设备发现不到、配网问题、常见错误码排查
  - 最佳实践：重试策略配置、超时设置、稳定性建议
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `human-judgement` TR-9.1: 新用户按快速开始步骤可在30分钟内跑通第一个测试
  - `human-judgement` TR-9.2: API文档每个方法都有参数说明和使用示例
  - `human-judgement` TR-9.3: FAQ覆盖最常见的3-5个问题
  - `human-judgement` TR-9.4: 代码示例可直接复制运行（替换配置后）

## [ ] Task 10: 端到端验证与示例脚本更新
- **Priority**: high
- **Depends On**: Task 1-8
- **Description**:
  - 更新test_examples.py，使用新的API
  - 新增e2e_test_example.py端到端示例脚本
  - 验证所有CLI命令正常工作
  - 验证pytest集成正常工作
  - 验证JSON报告输出正确
  - 验证异常场景处理正确
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有CLI命令--help正常显示
  - `programmatic` TR-10.2: --discover能发现设备（需要真实设备时标注可选）
  - `human-judgement` TR-10.3: 示例脚本注释清晰，可作为用户参考
  - `human-judgement` TR-10.4: 端到端流程顺畅，没有明显的bug或遗漏

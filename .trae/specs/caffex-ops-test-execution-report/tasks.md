# Caffex 算子库 Docker 环境全面测试与标准化报告生成 - The Implementation Plan

## [ ] Task 1: 环境预检与Docker镜像验证
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 检查 Docker Desktop 是否运行中（`docker info`）
  - 检查 `caffe-cpu:origin-runtime` 镜像是否存在；若不存在则进入 `docker/origin/` 执行 `./build.sh` 构建（Windows下通过WSL执行）
  - 在容器内运行 `verify-caffe.sh` 验证12项检查全部通过
  - 验证容器内可正确导入 caffe 模块并输出版本信息
  - 验证容器与宿主机目录挂载机制正常（tests/ops/ 可读写）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker info` 返回正常，Docker服务运行中
  - `programmatic` TR-1.2: `docker image inspect caffe-cpu:origin-runtime` 成功，镜像存在
  - `programmatic` TR-1.3: `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 退出码为0
  - `programmatic` TR-1.4: `docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe; print(caffe.__version__)"` 正常输出版本
- **Notes**: 若需要构建镜像，首次构建耗时约15-30分钟；Windows下通过WSL运行bash脚本

## [ ] Task 2: 适配测试运行脚本（结果目录指向 tests/.temp/）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 方案A（推荐）：基于现有 `run_ops_tests.sh` 创建一个包装脚本或修改 RESULTS_DIR 变量，将结果输出从 `docker/origin/test-results/` 改为 `tests/.temp/`
  - 方案B：直接编写一个PowerShell或Python编排脚本，调用docker run运行各类测试，收集结果
  - 确保支持的测试类型：correctness、edge、performance(slow)、all
  - 每次运行测试时，在 .temp/ 下创建时间戳子目录（如 `20260728_HHMMSS/`）保存原始数据，避免覆盖
  - 在容器内自动安装 pytest 和 pytest-cov（如现有脚本所做）
  - 设置正确的环境变量：PYTHONPATH、LD_LIBRARY_PATH、GLOG_minloglevel=2
  - 捕获容器stdout/stderr到日志文件
- **Acceptance Criteria Addressed**: AC-5, FR-3, NFR-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本可执行，能成功启动容器并进入测试
  - `programmatic` TR-2.2: 测试结果文件（junit xml、日志）保存到 tests/.temp/<timestamp>/ 目录
  - `programmatic` TR-2.3: 脚本支持 --test-type 参数选择测试类型
  - `human-judgement` TR-2.4: 脚本有错误处理，容器失败时输出有用的诊断信息
- **Notes**: 优先选择修改现有 run_ops_tests.sh 中的 RESULTS_DIR 路径，保持最小改动

## [ ] Task 3: 执行功能正确性测试（correctness）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 使用 Task 2 的脚本运行 correctness 类型测试：`pytest -m "correctness and not slow" --tb=long --junitxml=... -v`
  - 捕获完整 stdout/stderr 到日志文件
  - 保存 JUnit XML 结果
  - 记录执行开始/结束时间和总耗时
  - 无论测试是否通过，都继续后续任务（健壮性要求）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: pytest 进程正常退出（退出码记录，无论0或非0）
  - `programmatic` TR-3.2: JUnit XML 文件生成在 .temp/ 目录，格式有效（可被XML解析器读取）
  - `programmatic` TR-3.3: 日志文件包含完整测试输出（PASS/FAIL/ERROR详情）
  - `programmatic` TR-3.4: 耗时信息被记录

## [ ] Task 4: 执行边界条件测试（edge）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 运行 edge 类型测试：`pytest -m "edge" --tb=long --junitxml=... -v`
  - 同样捕获日志、保存XML、记录耗时
  - edge测试覆盖零输入、极值、特殊形状等边界条件
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: edge标记的测试全部被执行（与测试文件中@pytest.mark.edge数量一致）
  - `programmatic` TR-4.2: 结果文件和日志完整保存

## [ ] Task 5: 执行性能基准测试（performance/slow）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 运行 slow/performance 标记测试：`pytest -m "slow" --tb=short --junitxml=... -v`
  - 注意：性能测试可能耗时较长，设置合理超时（如30分钟）
  - 从日志中提取各算子的计时数据（Timer类输出的elapsed时间）
  - 若不存在 slow 标记的测试用例（检查各测试文件），记录"无专项性能测试"并基于 correctness 测试的耗时给出粗略性能参考
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有slow标记测试被执行（如存在）
  - `programmatic` TR-5.2: 性能计时数据被采集（从日志或XML中提取）
  - `human-judgement` TR-5.3: 若性能测试缺失，在报告中如实说明

## [ ] Task 6: 全量测试运行（all，作为兼容性验证）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 运行 all 类型测试（不加marker过滤）：`pytest --tb=short --junitxml=... -v`
  - 这将覆盖所有测试用例，包括未标记marker的冒烟测试
  - 作为整体兼容性和稳定性验证
  - 保存独立的JUnit XML和日志
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 全部测试文件被pytest发现并执行
  - `programmatic` TR-6.2: 结果文件包含所有32个测试文件的用例

## [ ] Task 7: 创建测试报告生成脚本（generate_report.py）
- **Priority**: high
- **Depends On**: Task 6（可与Task 3-6并行准备，但需在Task6后运行）
- **Description**:
  - 在 `tests/ops/` 或 `tests/.temp/` 下创建 `generate_report.py`（宿主机器上运行，Python 3.13+）
  - 脚本功能：
    1. 解析指定目录下的所有 JUnit XML 文件（correctness/edge/performance/all 各自的XML）
    2. 读取对应的 pytest 日志文件
    3. 从环境信息中提取镜像版本、Python版本、numpy版本、protobuf版本等
    4. 统计：总用例数、通过数、失败数、错误数、跳过数、总耗时、通过率
    5. 按marker分类统计（correctness/edge/performance各自的通过率）
    6. 按测试文件（算子）维度汇总每个算子的测试状态
    7. 从日志中提取性能计时数据（如有），生成性能排名表
    8. 提取失败用例的错误消息和traceback（截断过长的traceback，保留关键信息）
    9. 生成Markdown报告，包含FR-6要求的10个章节
    10. 记录复现命令（docker run命令、pytest参数）
  - 脚本输入：结果目录路径（.temp/<timestamp>/）
  - 脚本输出：`OPS_TEST_REPORT.md` 保存到同一目录
- **Acceptance Criteria Addressed**: FR-4, FR-5, FR-6, NFR-1, NFR-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 脚本可正确解析JUnit XML（使用xml.etree.ElementTree）
  - `programmatic` TR-7.2: 统计数据计算正确（总数=pass+fail+error+skip）
  - `programmatic` TR-7.3: 即使某些XML/日志文件缺失，脚本也不崩溃，给出提示
  - `human-judgement` TR-7.4: 报告格式清晰，Markdown表格对齐良好，章节完整
- **Notes**: 脚本使用标准库，不依赖额外第三方包；XML解析参考JUnit格式

## [ ] Task 8: 生成标准化测试报告
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**:
  - 运行 generate_report.py，传入 .temp/ 下最新的时间戳结果目录
  - 生成 OPS_TEST_REPORT.md
  - 同时收集环境信息：在容器内运行 `python3 -c "import sys, numpy, google.protobuf; print('Python:', sys.version); print('numpy:', numpy.__version__); print('protobuf:', google.protobuf.__version__)"` 附加到报告
  - 报告应在FR-6的10个章节基础上，确保每个章节有实质性内容
- **Acceptance Criteria Addressed**: AC-6, AC-7, NFR-4
- **Test Requirements**:
  - `programmatic` TR-8.1: 报告文件 OPS_TEST_REPORT.md 生成在 tests/.temp/<timestamp>/ 下
  - `human-judgement` TR-8.2: 报告包含全部10个要求章节，内容完整
  - `human-judgement` TR-8.3: 报告数据与XML原始数据一致（抽查3-5个失败/通过用例核对）
  - `human-judgement` TR-8.4: 失败用例有清晰的错误描述和复现步骤提示

## [ ] Task 9: 整理输出目录并验证可复现性
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 在 tests/.temp/ 下创建/更新一个 `LATEST` 软链接或索引文件，指向最新的测试结果目录
  - 验证 .temp/ 目录结构清晰：
    ```
    tests/.temp/
    └── 20260728_HHMMSS/
        ├── junit_correctness.xml
        ├── junit_edge.xml
        ├── junit_performance.xml
        ├── junit_all.xml
        ├── log_correctness.txt
        ├── log_edge.txt
        ├── log_performance.txt
        ├── log_all.txt
        ├── env_info.txt
        ├── OPS_TEST_REPORT.md
        └── README.md（说明文件，记录目录内容和复现步骤）
    ```
  - 在报告末尾明确写出复现步骤（cd到哪个目录、执行什么命令）
  - 确认报告中记录了使用的镜像名、pytest版本、完整命令行
- **Acceptance Criteria Addressed**: AC-5, AC-8, NFR-2, NFR-5
- **Test Requirements**:
  - `programmatic` TR-9.1: 目录结构完整，所有预期文件存在
  - `programmatic` TR-9.2: 报告中的复现命令在语法上正确（可直接复制执行）
  - `human-judgement` TR-9.3: README.md 清晰说明目录内容和复现方法
- **Notes**: Windows下软链接可能需要管理员权限，可以用一个文本文件 LATEST.txt 记录最新目录名代替

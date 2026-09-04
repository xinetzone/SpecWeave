# xmnn-releases 版本化发布产物目录 - Verification Checklist

## 目录结构
- [ ] xmnn-releases/ 目录在 external/chaos/ai/ 下成功创建
- [ ] scripts/ 子目录存在
- [ ] templates/ 子目录存在
- [ ] .gitignore 文件存在且配置合理（排除 *.whl, *.tar 等大文件，保留文本文件）

## AGENTS.md 规范
- [ ] AGENTS.md 存在且包含"启动协议"关键词
- [ ] AGENTS.md 包含启动协议四步骤（读取本文件→确认父级→加载特有规范→自检→执行）
- [ ] AGENTS.md 包含项目概述（目录用途、核心功能、目标用户）
- [ ] AGENTS.md 包含嵌套路由关系图（展示与父级和其他镜像目录的关系）
- [ ] AGENTS.md 包含上下文路由表（任务类型→必读入口映射）
- [ ] AGENTS.md 包含核心约束表（版本号规范、元数据字段、校验要求、脚本规范）
- [ ] AGENTS.md 包含目录结构说明（latest/、vX.Y.Z/、scripts/、templates/ 的组织方式）
- [ ] AGENTS.md 包含快速开始示例（如何提取whl、如何安装、如何验证）
- [ ] AGENTS.md 正确引用父级 ../AGENTS.md
- [ ] AGENTS.md 包含变更日志章节

## 版本元数据模板
- [ ] templates/version.json.template 存在
- [ ] JSON格式有效
- [ ] 包含 version 字段（语义版本号）
- [ ] 包含 build_date 字段（ISO 8601格式）
- [ ] 包含 python_version 字段
- [ ] 包含 tvm_version、vta_version、xmnn_version 字段
- [ ] 包含 git_commit 字段
- [ ] 包含 whl_filename、whl_sha256 字段
- [ ] 包含 base_image 字段
- [ ] 包含 installed_components 字段

## 客户侧安装脚本
- [ ] scripts/install.sh 存在且可执行
- [ ] bash -n 语法检查通过
- [ ] 支持 --whl 参数指定whl文件路径
- [ ] 支持 --skip-verify 参数跳过验证
- [ ] 支持 --help 参数输出帮助
- [ ] 包含whl文件存在性检查
- [ ] 包含pip install逻辑（--force-reinstall）
- [ ] 安装后自动调用verify.sh
- [ ] 使用彩色日志输出（INFO/WARN/ERROR/SUCCESS）
- [ ] 错误处理完善（set -e -o pipefail，关键步骤失败输出明确信息）

## 客户侧验证脚本
- [ ] scripts/verify.sh 存在且可执行
- [ ] bash -n 语法检查通过
- [ ] 验证 python3 可执行
- [ ] 验证 import tvm 成功
- [ ] 验证 import vta 成功
- [ ] 验证 import xmnn 成功
- [ ] 验证 xmnn._libs 目录存在且包含.so文件
- [ ] 验证 libtvm.so 可通过ctypes加载
- [ ] 每项验证输出 [PASS] 或 [FAIL] 标记
- [ ] 末尾输出 "Result: X/Y PASSED" 统计
- [ ] 全部通过返回0，有失败返回1
- [ ] 支持 --python 参数指定Python路径

## 父级AGENTS.md更新
- [ ] ai/AGENTS.md 中镜像矩阵/目录列表包含 xmnn-releases
- [ ] ai/AGENTS.md 上下文路由表包含 xmnn-releases 入口
- [ ] ai/AGENTS.md 项目概述中正确描述四层结构（开发→构建→运行时→发布产物）
- [ ] 更新不破坏原有格式和内容

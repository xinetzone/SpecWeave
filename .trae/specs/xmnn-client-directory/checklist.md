# xmnn-client 验证清单

## 目录结构
- [ ] xmnn-client/ 目录已创建在 external/chaos/ai/ 下
- [ ] examples/ 子目录存在
- [ ] scripts/ 子目录存在
- [ ] .gitignore 存在且排除 *.whl、*.whl.sha256、latest/
- [ ] 目录下无 .agents/rules/、templates/、extract-release.sh 等开发者文件
- [ ] 开发模式下 xmnn-client/ 下无 *.whl 文件（零拷贝）

## AGENTS.md
- [ ] AGENTS.md 文件存在
- [ ] 包含"启动协议"关键词
- [ ] 正确引用父级 ../AGENTS.md
- [ ] 路由表仅包含用户侧任务（安装、验证、Hello World、WSL指引、standalone打包）
- [ ] 路由表不包含"添加新版本"、"构建镜像"、"extract-release"等开发者任务
- [ ] 明确说明平台约束：仅支持 Linux/WSL2，不支持 macOS 原生
- [ ] 在嵌套路由关系图中与 xmnn-releases、xmnn-runtime 并列

## verify.sh
- [ ] verify.sh 存在且可执行
- [ ] 以 #!/bin/bash 开头，使用 set -e -o pipefail
- [ ] source ../scripts/lib/logging.sh 使用统一彩色日志
- [ ] 支持 --help/-h 参数
- [ ] 支持 --python <path> 参数
- [ ] 包含7项验证：Python可执行、import tvm、import vta、import xmnn、_libs目录、libtvm.so加载、Python版本
- [ ] 版本检测使用 importlib.metadata.version('xmnn')（非 __version__）
- [ ] _libs路径使用 os.path.join(os.path.dirname(tvm.__file__), '../_libs')
- [ ] 计数器使用 VAR=$((VAR+1)) 模式（无后置++）
- [ ] 输出 X/7 PASSED 格式，exit code 正确（0=全部通过，1=有失败）
- [ ] 使用 SCRIPT_DIR 获取脚本目录

## install.sh
- [ ] install.sh 存在且可执行
- [ ] 以 #!/bin/bash 开头，使用 set -e -o pipefail
- [ ] source ../scripts/lib/logging.sh
- [ ] 支持 --help/-h 参数
- [ ] 支持 --whl <path> 参数指定whl路径
- [ ] 支持 --python <path> 参数
- [ ] 支持 --skip-verify 参数
- [ ] 双模式whl查找：--whl > ./latest/xmnn.whl > ../xmnn-releases/latest/xmnn.whl > 报错
- [ ] 开发模式：无 ./latest/ 时自动从 ../xmnn-releases/latest/ 找到whl
- [ ] standalone模式优先：./latest/xmnn.whl 存在时优先使用
- [ ] 无whl时给出明确错误信息和解决建议
- [ ] SHA256校验（若.sha256文件存在）
- [ ] 使用 pip install --force-reinstall --no-deps
- [ ] 安装后自动调用 verify.sh（除非 --skip-verify）
- [ ] 零参数默认安装最新版
- [ ] 安装成功后提示运行 python examples/hello-world.py
- [ ] 计数器使用 VAR=$((VAR+1)) 模式

## sync-from-releases.sh
- [ ] scripts/sync-from-releases.sh 存在且可执行
- [ ] 遵循脚本规范（shebang、set -e、source logging.sh）
- [ ] 支持 --help
- [ ] 前置检查 ../xmnn-releases/latest/ 存在且包含whl
- [ ] 删除旧 xmnn-client/latest/ 后重新拷贝
- [ ] 拷贝 xmnn.whl、xmnn.whl.sha256、version.json、release-notes.md
- [ ] 输出拷贝的文件列表和大小
- [ ] 同步后 install.sh 能在 standalone 模式下工作

## Hello World 示例
- [ ] examples/hello-world.py 存在
- [ ] import tvm、import vta、import xmnn
- [ ] 使用 importlib.metadata.version 获取版本号
- [ ] 打印版本号和模块路径
- [ ] 包含简单的 TVM runtime 验证（如向量加法build+run）
- [ ] 输出成功提示（如"✅ XMNN environment is ready!"）
- [ ] import失败时给出友好错误提示和排查建议
- [ ] 代码简洁（≤50行）
- [ ] 运行成功 exit code 0

## README.md
- [ ] 快速开始区块位于文件最开头，≤15行
- [ ] 按平台分三小节：Linux、Windows (WSL2)、macOS
- [ ] Linux小节提供一行可复制命令：bash install.sh && python examples/hello-world.py
- [ ] Windows小节明确说明 WSL2+Ubuntu 前置条件
- [ ] macOS小节明确说明不支持原生，指向Docker方案
- [ ] 包含验证安装说明（verify.sh）
- [ ] 包含standalone分发包说明（sync-from-releases.sh）
- [ ] 包含安装指定版本说明（--whl参数）
- [ ] 包含简短常见问题FAQ
- [ ] 提供指向 xmnn-releases/ 的链接（开发者入口）
- [ ] 不包含构建说明、Docker镜像构建、extract-release用法、Nuitka编译等开发者内容

## 父级AGENTS.md更新
- [ ] external/chaos/ai/AGENTS.md 路由表包含 xmnn-client 条目
- [ ] 嵌套路由图包含 xmnn-client
- [ ] 正确区分 xmnn-client（使用者）vs xmnn-releases（开发者）

## 端到端测试
- [ ] bash install.sh（开发模式零参数）全流程PASS
- [ ] verify.sh 7/7 PASSED，exit code 0
- [ ] python examples/hello-world.py 运行成功
- [ ] bash scripts/sync-from-releases.sh 成功拷贝whl
- [ ] standalone模式下 install.sh 能找到本地whl并安装成功
- [ ] README和AGENTS.md人工审核通过

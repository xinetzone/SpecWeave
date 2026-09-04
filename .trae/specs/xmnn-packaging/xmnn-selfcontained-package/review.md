# xmnn-package - 自洽独立用户分发包 - Verification Checklist

## 目录结构与基础文件
- [ ] xmnn-package/目录已创建在 external/chaos/ai/ 下
- [ ] bin/、lib/、docker/、docs/、examples/ 子目录存在
- [ ] .gitignore 存在且正确排除 *.whl、*.tar、*.tar.gz、*.zip、*.sha256、version.json
- [ ] lib/.gitkeep 和 docker/.gitkeep 存在
- [ ] version.json.template 存在且包含所有必填字段

## 脚本自包含性（最关键检查）
- [ ] bin/lib/common.sh 存在，所有日志函数内嵌定义
- [ ] bin/lib/common.sh 中无 source 外部文件（无 ../../ 跳出包目录的source）
- [ ] PACKAGE_ROOT 变量正确指向包根目录（bin/的上级）
- [ ] 所有bin/下的脚本source bin/lib/common.sh（使用$PACKAGE_ROOT/bin/lib/common.sh或相对路径但不跳出包）
- [ ] grep -r "\.\./xmnn" bin/ 无匹配（无引用xmnn-releases/xmnn-runtime/xmnn-client）
- [ ] grep -r "source.*\.\./\.\." bin/ 无匹配（无source包外文件）
- [ ] grep -r "SpecWeave" bin/ docs/ 无匹配（不引用仓库名）
- [ ] 所有脚本以 #!/usr/bin/env bash 开头
- [ ] 所有脚本包含 set -e -o pipefail
- [ ] 所有计数器使用 VAR=$((VAR+1)) 模式，无 ((VAR++))

## bin/install.sh 验证
- [ ] 零参数执行时自动查找 $PACKAGE_ROOT/lib/xmnn-*.whl
- [ ] 无development模式回退（不查找../xmnn-releases）
- [ ] SHA256校验逻辑正确（.sha256存在时验证）
- [ ] pip install 使用 --force-reinstall --no-deps
- [ ] 安装后自动调用verify.sh
- [ ] 支持 --python、--skip-verify、--whl、--help 参数
- [ ] TTY检测正确，非TTY无颜色输出

## bin/verify.sh 验证
- [ ] 至少10项检查（Python、tvm、vta、xmnn、_libs、libtvm.so、Python版本>=3.14、bootstrap、version.json、计算测试）
- [ ] PASS/FAIL/WARN 统计正确
- [ ] FAIL项输出针对性修复建议
- [ ] 支持 --python、--help 参数
- [ ] 版本检测优先使用 importlib.metadata.version('xmnn')
- [ ] _libs路径使用 os.path.join(os.path.dirname(tvm.__file__), '../_libs')

## bin/docker-setup.sh 验证
- [ ] Docker不可用时友好提示安装方法
- [ ] 检测本地是否已有xmnn-runtime镜像
- [ ] docker/xmnn-runtime.tar存在时提示load
- [ ] 提供docker run命令示例
- [ ] 支持 --load、--run、--verify、--help 参数
- [ ] 无外部路径引用

## bin/hello-world.sh 验证
- [ ] 前置检查xmnn是否安装
- [ ] 未安装时提示先运行install.sh
- [ ] 成功运行examples/hello-world.py
- [ ] 支持 --python、--help 参数

## examples/hello-world.py 验证
- [ ] 输出XMNN版本
- [ ] 输出TVM版本
- [ ] 执行简单张量计算并输出结果
- [ ] 不依赖包外任何文件

## 文档自包含性
- [ ] 根目录README.md存在，3步快速开始清晰
- [ ] docs/README.md存在（详细文档索引和快速开始）
- [ ] docs/INSTALL.md存在（详细安装指南）
- [ ] docs/DOCKER.md存在（Docker使用指南）
- [ ] docs/WSL2.md存在（Windows WSL2指引）
- [ ] docs/TROUBLESHOOTING.md存在（故障排查）
- [ ] grep -r "\.\./xmnn" docs/ 无匹配
- [ ] grep -r "SpecWeave" docs/ 无匹配
- [ ] grep -r "external/chaos" docs/ 无匹配
- [ ] 所有路径引用均为相对于包根目录的路径（bin/、lib/、docs/、examples/）
- [ ] 文档语言为中文
- [ ] WSL2.md包含：WSL2安装、路径转换（/mnt/盘符）、常见问题

## package.sh 打包脚本验证
- [ ] --version参数必填，无时报错并提示
- [ ] 支持 --with-docker 参数控制是否导出镜像tar
- [ ] 支持 --output 参数指定输出目录
- [ ] 支持 --help 参数
- [ ] 正确复制bin/、docs/、examples/、README.md、.gitignore到目标目录
- [ ] 从../xmnn-releases/latest/复制whl和sha256到lib/
- [ ] 复制/生成version.json到包根目录，package_type="self-contained"
- [ ] --with-docker时执行docker save导出tar到docker/
- [ ] 打包完成后输出摘要（目录路径、文件列表、大小）
- [ ] package.sh是开发脚本，允许引用../xmnn-releases（这是唯一允许外部引用的脚本）

## 父级AGENTS.md更新
- [ ] external/chaos/ai/AGENTS.md镜像矩阵已更新，包含xmnn-package
- [ ] xmnn-client和xmnn-package定位区别清晰
- [ ] 上下文路由表已添加xmnn-package条目

## 端到端验证（最高优先级）
- [ ] 运行 bash package.sh --version vX.Y.Z 成功生成自洽包
- [ ] 将生成的xmnn-package-vX.Y.Z/复制到/tmp/（完全独立于开发仓库的路径）
- [ ] 在/tmp/xmnn-package-vX.Y.Z/下执行 bash bin/install.sh 成功
- [ ] 执行 bash bin/verify.sh 所有检查项PASS（无FAIL）
- [ ] 执行 bash bin/hello-world.sh 成功输出版本和计算结果
- [ ] 执行 python examples/hello-world.py 同样成功
- [ ] grep -r "\.\./xmnn" /tmp/xmnn-package-vX.Y.Z/ 无匹配（除package.sh外，但package.sh不应出现在分发包中——确认package.sh是否被复制到分发包）
- [ ] grep -r "source.*\.\./\.\." /tmp/xmnn-package-vX.Y.Z/ 无匹配
- [ ] 分发包大小合理（不含docker tar时<500MB）
- [ ] version.json在分发包根目录存在且字段完整

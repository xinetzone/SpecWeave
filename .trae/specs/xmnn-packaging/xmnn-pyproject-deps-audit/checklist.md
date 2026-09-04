# XMNN pyproject.toml 依赖审计与补全 - Verification Checklist

## 依赖声明完整性
- [x] pyproject.toml 的 `[project].dependencies` 包含 21 个核心依赖：numpy, scipy, pandas, matplotlib, Pillow, onnx, protobuf, openpyxl, tabulate, rich, tqdm, tomlkit, decorator, attrs, psutil, cloudpickle, typing_extensions, torch, torchvision, onnx2pytorch, telnetlib3
- [x] telnetlib3 已确认作为核心依赖（从 full 可选组移至核心 dependencies）
- [x] pytest 已从核心 dependencies 移除
- [x] pytest 存在于 `[project.optional-dependencies].dev` 组中
- [x] 可选依赖组（dev/examples/full）结构合理且 TOML 语法正确
- [x] 每个依赖都有 `>=X.Y` 格式的最低版本约束
- [x] 全面扫描确认无遗漏第三方 import（sdk/tools + npuusertools/xmnn + sdk/models，共 15 个直接 import 包全部覆盖）
- [x] tabulate 已包含（pandas.to_markdown() 需要）
- [x] 所有 21 个依赖声明通过 packaging.requirements.Requirement 解析验证

## Docker 环境同步
- [x] docker/runtime/Dockerfile 简化为"安装 torch CPU 版 + opencv + pip install wheel"模式，wheel 自动解析核心依赖
- [x] docker/runtime/Dockerfile 验证步骤覆盖所有核心依赖的 import 检查（含 telnetlib3）
- [x] docker/dev-llvm22/Dockerfile conda 依赖列表已同步（新增 pandas/matplotlib/openpyxl/tabulate/tqdm/rich/onnx/protobuf/tomlkit/pillow）
- [x] docker/dev-llvm22/Dockerfile pip 安装已同步（新增 onnx2pytorch/telnetlib3，配置清华镜像源）
- [x] docker/dev-llvm22/run-build.sh pip 依赖列表已同步（新增 telnetlib3 及其他缺失包）
- [x] docker/dev-llvm22/Dockerfile 验证脚本包含所有新增包版本检查
- [ ] runtime Dockerfile 实际构建验证（需 Docker 环境运行）
- [ ] dev Dockerfile 实际构建验证（需 Docker 环境运行）

## 端到端验证（静态检查已完成，运行时验证需 Docker 环境）
- [x] pyproject.toml TOML 语法验证通过（tomllib 可解析）
- [x] 所有依赖声明格式验证通过（packaging.requirements 解析全部成功）
- [x] full 组正确引用 `xmnn[dev,examples]`，无重复声明核心依赖
- [ ] pip --dry-run 依赖解析验证（需 Python 3.14 环境运行）
- [ ] 修改后可成功构建 wheel 包（需 Docker 构建环境）
- [ ] wheel METADATA 中包含所有 Requires-Dist
- [ ] 在纯净 Python 3.14 环境中 pip install xmnn-*.whl 成功

## 质量检查
- [x] 无 ImportError 或 ModuleNotFoundError 在核心脚本中（静态扫描确认）
- [x] rich 已包含（logger_config 使用）
- [x] tomlkit 已包含（config.toml 解析使用）
- [x] torch 使用 CPU 版本（Dockerfile 中通过 --index-url 控制）

# 模式萃取建议

## 已满足萃取条件的模式

### 无

本次任务中的洞察大多为首次发现，尚需第二案例验证后方可入库为正式模式。

## 候选模式（等待第二案例验证）

### C1: Docker .dockerignore 排除+白名单回补模式

- **状态**：候选（1案例）
- **类型**：代码模式（Docker构建）
- **来源案例**：本次Caffe Docker构建（scripts目录被.dockerignore排除）
- **核心做法**：
  ```dockerignore
  # 排除整个目录
  docker/**
  # 白名单回补需要的子目录
  !docker/origin/
  !docker/origin/scripts/
  # 排除子目录中不需要的部分
  docker/origin/.agents
  docker/origin/config
  ```
- **反模式**：简单使用 `docker` 整目录排除，会导致Dockerfile COPY所需文件不在build context中
- **等待**：其他Docker项目中出现类似.dockerignore配置错误

### C2: 深度学习框架算子正确性测试断言解包模式

- **状态**：候选（1案例）
- **类型**：代码模式（测试）
- **来源案例**：Caffe net.forward()返回单元素list vs numpy array的shape不匹配
- **核心做法**：断言函数必须处理框架返回的list/tuple/dict封装类型，在比较前自动解包单元素容器
- **反模式**：假设框架输出直接是numpy array，不处理封装类型会导致shape不匹配误报
- **等待**：PyTorch/TensorFlow/其他DL框架测试中出现类似输出封装问题

### C3: pytest marker正向选择模式

- **状态**：候选（1案例）
- **类型**：代码模式（测试配置）
- **来源案例**：`-m "not slow"` 意外包含未准备好的forward测试
- **核心做法**：使用正向marker选择（`-m "correctness"`）而非反向排除（`-m "not slow"`），配合`--strict-markers`防止拼写错误
- **反模式**：反向排除可能意外包含其他分类的测试；不使用strict-markers导致typo静默跳过测试
- **等待**：其他pytest项目中出现marker选择不精确问题

### C4: 参数化测试文件名字典类型序列化模式

- **状态**：候选（1案例）
- **类型**：代码模式（测试基础设施）
- **来源案例**：Reshape层dict参数未纳入文件名生成导致不同参数写入同一prototxt文件
- **核心做法**：动态生成文件名时必须递归序列化所有参数类型（dict/list/tuple/bool/nested），确保不同参数组合生成唯一文件名
- **反模式**：只处理基本类型(int/float/str)，不处理嵌套dict/list导致测试文件冲突
- **等待**：其他参数化测试框架中出现文件名冲突问题

### C5: 框架参数广播行为验证清单

- **状态**：候选（1案例）
- **类型**：流程模式（测试编写）
- **来源案例**：Caffe Crop层offset标量广播到所有维度导致越界
- **核心做法**：编写算子测试前，查阅文档确认参数广播/默认值/维度顺序等隐式行为，显式指定每个维度参数值而非依赖标量广播
- **反模式**：凭直觉/其他框架经验假设参数语义，标量参数在多维度算子中广播导致越界或错误结果
- **等待**：其他DL框架（PyTorch/TF）算子测试中出现类似参数广播误解问题

## 已有模式更新建议

### gitignore-validation 模式扩展

建议将 `.dockerignore` 验证纳入 `gitignore-validation` 模式的适用范围，新增：
- 构建上下文必需文件检查（Dockerfile COPY的文件是否在build context中）
- 修改.dockerignore后必须运行一次`docker build`验证
- 推荐使用"排除+白名单回补"模式而非简单整目录排除

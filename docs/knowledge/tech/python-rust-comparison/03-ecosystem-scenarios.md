---
id: "python-rust-comparison-ecosystem-scenarios"
title: "Python 与 Rust 技术对比 · 生态、应用场景与代码示例"
category: "tech"
tags: ["python", "rust", "生态", "应用场景", "代码示例"]
date: "2026-08-07"
status: stable
author: "SpecWeave"
summary: "对比 Python 与 Rust 的生态成熟度、典型应用场景，并提供对照代码示例。"
---

# Python 与 Rust 技术对比 · 生态、应用场景与代码示例

> 本文基于**最新稳定标准**（Python 3.14、Rust 1.97.1）从零创作，聚焦生态与组织成本、典型应用场景，并以真实可运行的对照代码示例佐证差异。所有内容均基于公开官方资料与生态事实，定性描述生态成熟度、社区活跃度等领域，不虚构量化数据、下载量、排名与企业案例细节。

版本与时效基准（2026-08）：
- **Python** 当前稳定版 **3.14**；生态核心为 PyPI 包仓库、pip/uv 包管理，以及 NumPy/Pandas/机器学习生态（PyTorch、scikit-learn 等）与 Web 生态（FastAPI、Flask、Django）。
- **Rust** 当前稳定版 **1.97.1**；生态核心为 crates.io 包仓库、Cargo 包管理、tokio 异步运行时、Web 框架（axum、actix-web）与系统工具（ripgrep、fd、starship 等知名 CLI）。

---

# 第一部分：生态与组织成本

生态与组织成本决定了一种语言能否在团队中长期落地。以下按统一分析模板逐维度展开。

## 1. 生态成熟度

1. **Python 视角**：Python 拥有业界最广泛、最成熟的第三方生态之一。PyPI 集中托管海量第三方包，覆盖数据科学、机器学习、Web、自动化、运维、科学计算等几乎所有领域。核心科学计算生态（NumPy、Pandas）与机器学习生态（PyTorch、scikit-learn 等）长期处于行业主导地位，Web 生态（FastAPI、Flask、Django）成熟稳定。社区历史长、活跃度高，金融、教育、科研、互联网等行业均有大规模采用。
2. **Rust 视角**：Rust 生态以 crates.io 为集中仓库，Cargo 提供统一包管理与依赖解析。核心异步生态围绕 tokio 运行时构建，Web 框架（axum、actix-web）成熟，系统工具（ripgrep、fd、starship 等）已被广泛使用并证明其工程质量。Rust 生态在性能敏感、系统级与基础设施领域增长迅速，但整体覆盖面仍小于 Python。
3. **核心差异**：Python 生态广而深，以「开箱即用」的库覆盖几乎所有业务领域；Rust 生态专注而精，在性能、系统、并发与基础设施领域成熟度突出，但在数据科学、AI 应用等「胶水层」覆盖明显不足。
4. **适用场景**：需要快速调用大量现成库的业务层、数据层与 AI 编排层选 Python；需要高性能、内存安全、并发的系统组件与基础设施选 Rust。
5. **结论与取舍**：生态成熟度上 Python 综合覆盖面更广，Rust 在性能敏感领域更聚焦。选型应结合「需要调用的库」而非「语言本身」来判断。
6. **证据与来源**：
   - Python 官方包索引：https://pypi.org/
   - Python 官方文档（版本与生态）：https://www.python.org/
   - Rust 官方包索引：https://crates.io/
   - Rust 官方文档（包管理）：https://doc.rust-lang.org/cargo/
   - Rust 异步运行时：https://tokio.rs/
7. **风险与边界**：生态成熟度是相对且动态的；本文不提供下载量、排名等量化数据，读者应结合自身领域核实具体库的维护状态与许可证。

## 2. 学习曲线

1. **Python 视角**：Python 语法简洁、动态类型、逐行解释，适合快速上手。动态类型降低了初学门槛，但也意味着大型项目需要更强的纪律与类型注解（typing）配合以保证可维护性。对绝大多数开发任务，团队可在数周内达到可交付水平。
2. **Rust 视角**：Rust 引入所有权、借用、生命周期等独特概念，编译器严谨，学习曲线陡峭。即便有经验的语言工程师，通常也需要数周至数月才能熟练写出符合 Rust 惯用法的安全且高效的代码。但严格编译期检查带来了更高的交付确定性与更少的运行时缺陷。
3. **核心差异**：Python 以「低门槛、快速上手」见长；Rust 以「高门槛、高正确性」见长。学习成本与交付质量大致呈正相关。
4. **适用场景**：业务快速试错、原型验证、跨团队协作场景适合 Python；长期维护、安全敏感、性能关键的系统适合投入 Rust 学习成本。
5. **结论与取舍**：若团队以业务交付速度优先、成员语言背景多样，Python 学习成本更低；若团队追求长期工程质量与极致性能，Rust 的前期投入通常值得。
6. **证据与来源**：
   - Python 官方教程（Getting Started）：https://docs.python.org/3/tutorial/
   - Rust 官方书《The Rust Programming Language》：https://doc.rust-lang.org/book/
   - Rust Rustlings（练习式学习）：https://github.com/rust-lang/rustlings
7. **风险与边界**：学习曲线因人而异，取决于团队既有背景（如是否熟悉 C/C++ 或函数式语言）。过度强调「难」或「易」都可能导致选型偏差，应结合团队实际能力评估。

## 3. 招聘供给

1. **Python 视角**：Python 是当前最流行的通用编程语言之一，人才供给充足，覆盖应届生到资深工程师各个层级。数据科学、AI、Web、运维等岗位普遍要求 Python，招聘渠道广、面试资料丰富。
2. **Rust 视角**：Rust 人才供给相对稀缺，尤其在非基础设施领域。但 Rust 开发者通常具备较扎实的系统与工程功底，且 Rust 社区活跃、学习资源丰富，已有 C/C++/体系背景的开发者可较快转型。
3. **核心差异**：Python 人才供给广度远超 Rust；Rust 人才供给稀缺但质量与专注度较高。招聘难度与薪资溢价是组织需权衡的现实成本。
4. **适用场景**：需要大规模快速组建团队的业务线适合 Python；关键系统组件若需长期自研，可小规模组建 Rust 团队并以培训补齐。
5. **结论与取舍**：招聘供给上 Python 显著占优。选择 Rust 需预判人才获取成本与团队扩张难度，通常更适用于核心团队小、壁垒深的场景。
6. **证据与来源**：
   - 各大招聘平台的语言需求统计数据可作参考（数据随市场动态变化，本文不做量化断言）；
   - Rust 官方职业/社区资源：https://www.rust-lang.org/community
   - Python 社区与就业资源：https://www.python.org/community/
7. **风险与边界**：人才供给是市场动态变量，且不同地区差异显著。本文不提供具体排名或占比数据，组织应结合本地市场与岗位画像评估。

## 4. 长期维护

1. **Python 视角**：Python 依赖数量多、版本演进快（如 3.13→3.14），长期维护需关注依赖锁定、虚拟环境、类型一致性（typing）与上游库兼容。动态类型在大型代码库中长期演化时易产生隐性缺陷，需借助 linter、类型检查器与强测试纪律补偿。
2. **Rust 视角**：Rust 编译期保证让「能编译即大概率正确」，内存安全、数据竞争等一大批运行时缺陷在编译期被拦截，长期维护成本中「隐性缺陷治理」占比更低。Cargo 的依赖锁定（Cargo.lock）与版本管理成熟，但严苛的编译器意味着修改公共接口时需处理较多的编译期连锁改动。
3. **核心差异**：Python 的长期维护更依赖工程纪律与测试；Rust 的长期维护更多依赖编译器保证，改造成本前置到编译期。
4. **适用场景**：重视长期演化与低缺陷率的系统组件适合 Rust；依赖快速迭代与广泛生态的业务系统适合 Python。
5. **结论与取舍**：从「长期维护确定性」看 Rust 有结构性优势，但维护成本会前移到修改与编译阶段；Python 则更依赖团队纪律来维持长期健康度。
6. **证据与来源**：
   - Python 版本发布节奏与支持策略：https://devguide.python.org/versions/
   - Rust 版本发布与稳定性承诺：https://doc.rust-lang.org/edition-guide/
   - Cargo 依赖锁定文档：https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
7. **风险与边界**：长期维护成本包含人员流动、文档、测试基建等多重因素，语言特性只是其中一环，不应孤立比较。

## 5. 企业采用

1. **Python 视角**：Python 在数据科学、AI、Web 后端、自动化运维、金融量化等领域被广泛采用，企业级案例众多，生态与人才支持成熟，属于「企业友好型」语言。
2. **Rust 视角**：Rust 在基础设施、云原生、区块链、嵌入式、高性能服务等领域被越来越多的企业采用，已知的系统工具（如 ripgrep、fd、starship）与知名项目（如 tokio、axum）已在生产环境被大规模使用。Rust 正从「新兴语言」走向「关键基础设施的可靠选择」。
3. **核心差异**：Python 的企业采用以业务广度与人才密度取胜；Rust 的企业采用以关键基础设施的可靠性与性能取胜，两者在组织内常互补共存。
4. **适用场景**：企业需要快速交付业务与数据能力时选 Python；需要高性能、安全、低资源消耗的关键组件时选 Rust，并常以混合架构组合两者。
5. **结论与取舍**：企业采用上两者各有核心阵地。决策应结合企业所在行业与架构现状，而非简单地「二选一」。
6. **证据与来源**：
   - Python 官方关于适用范围与生态的说明：https://www.python.org/about/
   - Rust 官方「生产使用」与生态介绍：https://www.rust-lang.org/production
   - crates.io 官方统计：https://crates.io/
7. **风险与边界**：本文不虚构具体企业案例细节与量化采用数据，读者应结合公开的白皮书与行业资料核实。

---

# 第二部分：典型应用场景

## 6. Web 服务

1. **Python 视角**：Python Web 生态成熟，FastAPI（基于异步与类型注解，社区增长快）、Flask（轻量灵活）、Django（全功能框架）覆盖从原型到大型系统的各类需求，开发效率高、上手快。
2. **Rust 视角**：Rust Web 生态以 tokio 异步运行时为底座，axum、actix-web 等框架成熟，具备高并发、低资源占用与内存安全优势，适合对性能与可靠性要求高的服务。
3. **核心差异**：Python 以开发效率与生态广度见长；Rust 以高吞吐、低延迟、低内存占用与并发安全性见长。
4. **适用场景**：业务迭代快的 CRUD、内部工具、AI 服务编排选 Python；高并发网关、实时服务、性能敏感 API 选 Rust。
5. **结论与取舍**：Web 服务两者都完全可行。一般业务层选 Python 降低成本，性能热点层选 Rust 提升上限。
6. **证据与来源**：
   - FastAPI 官方：https://fastapi.tiangolo.com/
   - Flask 官方：https://flask.palletsprojects.com/
   - Django 官方：https://www.djangoproject.com/
   - axum 官方：https://github.com/tokio-rs/axum
   - actix-web 官方：https://actix.rs/
   - tokio 官方：https://tokio.rs/
7. **风险与边界**：框架选择应结合团队熟练度与具体业务；「性能差异」需在相近实现与硬件下实测，本文不做跨场景的量化断言。

## 7. 系统编程与 CLI

1. **Python 视角**：Python 可快速编写脚本与 CLI 工具，开发效率高，但受 GIL 与解释执行限制，在高强度系统级任务、极致性能与资源受限场景下力不从心。
2. **Rust 视角**：Rust 是系统编程与 CLI 的强项，无自动 GC、内存安全、可编译为原生二进制，适合硬件贴近、性能敏感、资源受限的场景。一大批知名 CLI（ripgrep、fd、starship）即由 Rust 编写，验证了其在该领域的优势。
3. **核心差异**：Python 胜在快速编写与生态；Rust 胜在性能、内存安全、单二进制分发与低资源占用。
4. **适用场景**：快速自动化脚本、内部运维工具选 Python；需高性能、可独立分发、低延迟的 CLI 与系统组件选 Rust。
5. **结论与取舍**：系统编程与高性能 CLI 是 Rust 的核心优势区；Python 更适合脚本层级与快速原型。
6. **证据与来源**：
   - ripgrep：https://github.com/BurntSushi/ripgrep
   - fd：https://github.com/sharkdp/fd
   - starship：https://github.com/starship/starship
7. **风险与边界**：CLI 的选择取决于分发形态、性能需求与生态要求；Python 生态中 typer、click 等库对 CLI 也有良好支持。

## 8. 数据科学与 AI

1. **Python 视角**：数据科学与 AI 是 Python 的绝对主导领域。NumPy、Pandas 提供高效的数值与表格计算基础，PyTorch、scikit-learn 等构成机器学习与深度学习主流生态，工具链、教学资源与社区沉淀深厚。
2. **Rust 视角**：Rust 在数据科学与 AI 领域生态仍在成长，虽有数值计算与深度学习相关库，但成熟度、易用性与社区资源远不及 Python。Rust 常作为 Python 高性能后端的补充（如通过绑定/扩展）而非替代。
3. **核心差异**：Python 在数据科学与 AI 上拥有不可比拟的生态与人才优势；Rust 在该领域覆盖有限，价值更多体现在底层性能引擎。
4. **适用场景**：数据清洗、建模、训练、推理编排、可视化选 Python；对极致性能的底层算子、推理引擎可用 Rust 实现并被 Python 调用。
5. **结论与取舍**：数据科学与 AI 领域 Python 占据主导，Rust 更适合作为性能引擎的补充实现，两者常以「Python 编排 + Rust 内核」协作。
6. **证据与来源**：
   - NumPy 官方：https://numpy.org/
   - Pandas 官方：https://pandas.pydata.org/
   - PyTorch 官方：https://pytorch.org/
   - scikit-learn 官方：https://scikit-learn.org/
7. **风险与边界**：Rust 数据科学生态仍在演进，具体库能力需按项目核实；本文不虚构 PyTorch/Rust 的替代性结论。

## 9. 区块链

1. **Python 视角**：Python 在区块链领域可用于快速原型、脚本与部分公链节点实现，但因其性能与资源占用，较少作为高性能共识/执行引擎的首选。
2. **Rust 视角**：Rust 以其性能、内存安全、并发正确性与可审计性，成为区块链领域的高频选择，被广泛用于节点、共识、密码学与智能合约运行时等关键组件。
3. **核心差异**：Python 适合区块链相关工具与原型；Rust 适合对安全、性能与确定性要求极高的区块链核心组件。
4. **适用场景**：区块链节点、底层协议、密码学与高性能组件选 Rust；智能合约相关脚本、测试工具与数据分析可结合 Python。
5. **结论与取舍**：区块链核心链上组件以 Rust 更契合工程要求；Python 多用于外围工具与数据分析。
6. **证据与来源**：
   - Rust 官方生产使用页面（含各行业采用）：https://www.rust-lang.org/production
   - crates.io 区块链相关 crate 检索：https://crates.io/
7. **风险与边界**：本文不虚构具体区块链项目与量化采用数据，读者应按具体项目核实技术栈。

## 10. 云原生

1. **Python 视角**：Python 广泛用于云原生中的控制面、运维自动化、脚本与部分服务，生态丰富、开发快，但资源占用与启动速度在生产规模上需权衡。
2. **Rust 视角**：Rust 因低资源占用、快速启动、内存安全与可编译为单二进制，非常适合云原生基础设施、边车代理、Kubernetes 相关组件与高性能服务，被广泛用于关键基础设施层。
3. **核心差异**：Python 在云原生的控制面与自动化层有优势；Rust 在数据面、基础设施与性能敏感组件有优势。
4. **适用场景**：集群自动化、运维脚本、控制面聚合业务选 Python；高性能代理、边车、基础设施组件选 Rust。
5. **结论与取舍**：云原生场景常呈现「控制面 Python + 数据面 Rust」的混合形态，两者互补。
6. **证据与来源**：
   - Rust 官方生产使用与应用介绍：https://www.rust-lang.org/production
   - Kubernetes 与云原生生态中 Rust 相关项目检索：https://crates.io/
7. **风险与边界**：云原生技术栈演进快，具体组件选型应结合项目现状；本文不做具体框架的量化对比。

## 11. 嵌入式与 IoT

1. **Python 视角**：Python 可用于可运行解释器的平台与脚本场景（如 MicroPython），开发快、易调试，但受限于运行环境与资源占用，不适合极端受限的裸机场景。
2. **Rust 视角**：Rust 无运行时开销、内存安全、可面向裸机与受限资源编译，非常适合嵌入式与 IoT 设备端开发，生态（如 embedded-hal 等，以及 Rust「no_std」生态）逐步成熟。
3. **核心差异**：Python 胜在开发速度与脚本灵活性；Rust 胜在无运行时、资源效率、内存安全与可靠性。
4. **适用场景**：原型验证、需要快速迭代的脚本层选 Python；受限资源的设备端、驱动、固件与关键控制逻辑选 Rust。
5. **结论与取舍**：嵌入式与 IoT 设备端更契合 Rust 的工程特性；Python（含 MicroPython）适合快速原型与高层逻辑。
6. **证据与来源**：
   - Rust 嵌入式工作组：https://github.com/rust-embedded
   - MicroPython 官方：https://micropython.org/
7. **风险与边界**：嵌入式选型高度依赖具体芯片、工具链与生态支持，本文不做具体硬件平台的优劣断言。

---

# 第三部分：代码示例对比

以下提供 Python 与 Rust 的对照示例，均为可运行的简单程序，并标注运行方式与依赖版本。所有示例针对当前稳定标准（Python 3.14、Rust 1.97.1）编写。

## 12. HTTP 服务示例

1. **Python 视角**：使用 FastAPI（需 Python 3.14 与 uvicorn 运行器）编写一个返回 JSON 的最小 HTTP 服务，代码量少、类型注解友好。
2. **Rust 视角**：使用 axum（搭配 tokio）编写一个等价的最小 HTTP 服务，代码稍长但性能与并发特性由生态保证。
3. **核心差异**：Python 代码更短、上手更快；Rust 代码需显式处理异步运行时与类型，但具备原生级并发与低资源占用。
4. **适用场景**：快速搭建 API 选 Python；高并发、低延迟 API 选 Rust。
5. **结论与取舍**：两者都能轻松实现 HTTP 服务，抉择取决于性能与开发效率的权衡。
6. **证据与来源**：见上文 Web 服务维度的官方链接。
7. **风险与边界**：示例为最小实现，未包含生产所需的配置、日志、健康检查等，仅供理解语法与结构差异。

### Python（Python 3.14 + FastAPI）

```python
# hello.py
# 依赖：fastapi、uvicorn
# 运行：python -m uvicorn hello:app --reload
# 然后访问 http://127.0.0.1:8000/hello

from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
def hello() -> dict:
    return {"message": "Hello, Python 3.14!"}
```

**运行方式**：
```bash
# 创建虚拟环境并安装依赖
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install "fastapi>=0.115" "uvicorn>=0.30"
# 启动服务
python -m uvicorn hello:app --reload
```
访问 `http://127.0.0.1:8000/hello` 应返回 `{"message":"Hello, Python 3.14!"}`。

### Rust（Rust 1.97.1 + axum）

创建新项目并添加依赖：
```bash
cargo new hello_axum
cd hello_axum
cargo add axum tokio --features tokio/macros --features tokio/rt-multi-thread
```

`src/main.rs`：
```rust
use axum::{routing::get, Router};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    let app = Router::new().route(
        "/hello",
        get(|| async { "Hello, Rust 1.97.1!" }),
    );
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    println!("Listening on http://{addr}");
    axum::serve(listener, app).await.unwrap();
}
```

**运行方式**：
```bash
cargo run
```
访问 `http://127.0.0.1:3000/hello` 应返回 `Hello, Rust 1.97.1!`。

## 13. 质数计算示例

1. **Python 视角**：用纯 Python 实现质数筛，逻辑直观，但受解释执行影响，计算密集型性能有限。
2. **Rust 视角**：用等价逻辑实现质数筛，编译为原生代码，计算性能远高于纯 Python。
3. **核心差异**：同一算法下 Rust 的运行时性能显著优于纯 Python；Python 可通过 NumPy/C 扩展提升但复杂度上升。
4. **适用场景**：快速原型与脚本选 Python；计算密集型且需极致性能选 Rust。
5. **结论与取舍**：正确性等价，性能差异明显；若追求性能又需 Python 生态，可考虑将热点用 Rust 实现并通过扩展调用。
6. **证据与来源**：见上文数据科学与 AI、系统编程维度的官方链接。
7. **风险与边界**：本示例未做基准测量，不提供具体性能倍数；读者应在相同硬件与输入规模下自行验证。

### Python（Python 3.14）

```python
# prime.py
# 运行：python prime.py 100
import sys


def count_primes(n: int) -> int:
    if n < 2:
        return 0
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return sum(is_prime)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"<= {limit} 的质数个数: {count_primes(limit)}")
```

**运行方式**：
```bash
python prime.py 1000000
```

### Rust（Rust 1.97.1）

`src/main.rs`：
```rust
use std::env;

fn count_primes(n: usize) -> usize {
    if n < 2 {
        return 0;
    }
    let mut is_prime = vec![true; n + 1];
    is_prime[0] = false;
    is_prime[1] = false;
    let mut i = 2;
    while i * i <= n {
        if is_prime[i] {
            let mut j = i * i;
            while j <= n {
                is_prime[j] = false;
                j += i;
            }
        }
        i += 1;
    }
    is_prime.iter().filter(|&&v| v).count()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let limit: usize = if args.len() > 1 {
        args[1].parse().unwrap_or(100)
    } else {
        100
    };
    println!("<= {} 的质数个数: {}", limit, count_primes(limit));
}
```

**运行方式**（先 `cargo new prime` 放入 `src/main.rs`）：
```bash
cargo run -- 1000000
```

## 14. 并发任务示例

1. **Python 视角**：Python 可用 asyncio 实现并发 I/O 任务，适合网络/文件等 I/O 密集场景；CPU 密集场景受 GIL 限制需用多进程（multiprocessing）弥补。
2. **Rust 视角**：Rust 依赖 tokio 异步运行时与 async/await 实现高并发 I/O，同时可借助多线程（std::thread）与并发原语实现 CPU 并行，无 GIL 限制。
3. **核心差异**：两者都支持 async/await 与并发 I/O；Rust 在 CPU 并行与极端并发下限制更少、性能上限更高。
4. **适用场景**：I/O 密集的网络服务二者皆宜；CPU 密集并行与高并发基础设施更倾向 Rust。
5. **结论与取舍**：并发编程范式相似，但 Rust 在资源与性能边界上更宽，Python 在 I/O 密集业务上已足够。
6. **证据与来源**：
   - Python asyncio 官方文档：https://docs.python.org/3/library/asyncio.html
   - Rust async 编程书：https://rust-lang.github.io/async-book/
   - tokio 官方：https://tokio.rs/
7. **风险与边界**：并发模型的效率依赖具体任务类型（I/O 密集 vs CPU 密集）与实现方式，不可一概而论。

### Python（Python 3.14 + asyncio）

```python
# async_fetch.py
# 运行：python async_fetch.py
import asyncio


async def worker(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} 完成，耗时 {delay}s"


async def main() -> None:
    tasks = [worker(f"任务{i}", i * 0.1) for i in range(1, 6)]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
```

**运行方式**：
```bash
python async_fetch.py
```

### Rust（Rust 1.97.1 + tokio）

`src/main.rs`：
```rust
use std::time::Duration;

async fn worker(name: &str, delay: u64) -> String {
    tokio::time::sleep(Duration::from_millis(delay)).await;
    format!("{} 完成，耗时 {}ms", name, delay)
}

#[tokio::main]
async fn main() {
    let tasks: Vec<_> = (1..=5)
        .map(|i| worker(&format!("任务{}", i), i * 100))
        .collect();
    let results = futures::future::join_all(tasks).await;
    for r in results {
        println!("{}", r);
    }
}
```

**运行方式**：
```bash
# 在 Cargo.toml 中添加依赖：
#   axum 不需要；需要 tokio 与 futures
cargo add tokio --features macros,rt-multi-thread
cargo add futures
cargo run
```

> 说明：Rust 示例中 `futures::future::join_all` 用于并发等待多个异步任务；若已通过 `cargo add tokio --features macros,rt-multi-thread` 添加 `#[tokio::main]` 宏，则上述代码可直接运行。

---

## 小结

- **生态与组织成本**：Python 以生态广度、低门槛、人才供给与长期维护的工程化生态见长；Rust 以性能、内存安全、并发正确性及系统级生态的专注优势见长。两者在组织内常互补，形成「Python 编排 + Rust 内核」的混合架构。
- **典型应用场景**：Python 主导数据科学与 AI、业务 Web 与快速自动化；Rust 强于系统编程与 CLI、高性能 Web、区块链核心、云原生数据面与嵌入式设备端。
- **代码示例对比**：HTTP 服务、质数计算、并发任务三类示例表明，两者语法与生态形式不同，但能力边界清晰——Python 重开发效率，Rust 重运行时性能与可靠性。

[返回总览](00-overview.md)
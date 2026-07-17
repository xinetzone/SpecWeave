# 本地依赖缓存代理体系 - 五层缓存架构图

```mermaid
flowchart TD
    Client["客户端/构建工具<br/>(docker/conda/pip/npm)"]
    
    subgraph L1 ["第一层：Docker Registry Mirror"]
        direction LR
        DM1["公共镜像加速器<br/>DaoCloud/网易/1Panel"]
        DM2["Harbor 私有仓库<br/>(团队级)"]
    end
    
    subgraph L2 ["第二层：Dockerfile 构建缓存"]
        direction LR
        DC1["层缓存排序<br/>(依赖前置)"]
        DC2["BuildKit 本地卷缓存"]
    end
    
    subgraph L3 ["第三层：Conda 包缓存"]
        direction LR
        CC1["pkgs_dirs 本地目录"]
        CC2["conda-proxy 代理缓存"]
    end
    
    subgraph L4 ["第四层：Pip 包缓存"]
        direction LR
        PC1["pip 本地缓存"]
        PC2["devpi 私有 PyPI"]
    end
    
    subgraph L5 ["第五层：NPM 包缓存"]
        direction LR
        NC1["npm 本地缓存"]
        NC2["verdaccio 私有仓库"]
    end
    
    subgraph Upstream ["上游公共源"]
        direction LR
        U1["Docker Hub"]
        U2["清华/中科大镜像"]
        U3["PyPI 官方"]
        U4["NPM 官方"]
    end
    
    LocalHit["✅ 本地缓存命中<br/>(秒级返回)"]
    CacheMiss["❌ 缓存未命中<br/>(回源下载)"]
    
    Client -->|"请求"| L1
    Client -->|"构建"| L2
    Client -->|"安装"| L3
    Client -->|"安装"| L4
    Client -->|"安装"| L5
    
    L1 -->|"命中"| LocalHit
    L2 -->|"命中"| LocalHit
    L3 -->|"命中"| LocalHit
    L4 -->|"命中"| LocalHit
    L5 -->|"命中"| LocalHit
    
    L1 -->|"未命中"| CacheMiss
    L2 -->|"基础镜像回源"| L1
    L3 -->|"未命中"| CacheMiss
    L4 -->|"未命中"| CacheMiss
    L5 -->|"未命中"| CacheMiss
    
    CacheMiss -->|"下载"| Upstream
    Upstream -->|"缓存写入"| L1
    Upstream -->|"缓存写入"| L3
    Upstream -->|"缓存写入"| L4
    Upstream -->|"缓存写入"| L5
    
    style L1 fill:#E3F2FD,stroke:#1976D2
    style L2 fill:#E8F5E9,stroke:#388E3C
    style L3 fill:#FFF3E0,stroke:#F57C00
    style L4 fill:#F3E5F5,stroke:#7B1FA2
    style L5 fill:#FFEBEE,stroke:#C62828
    style LocalHit fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px
    style CacheMiss fill:#FFCDD2,stroke:#B71C1C,stroke-width:2px
    style Upstream fill:#F5F5F5,stroke:#616161,stroke-dasharray:5 5
```

## 图例

| 颜色 | 层级 | 说明 |
|------|------|------|
| 🔵 蓝色 | 第一层 | Docker Registry Mirror - 镜像层缓存 |
| 🟢 绿色 | 第二层 | Dockerfile 构建缓存 - 指令层缓存 |
| 🟠 橙色 | 第三层 | Conda 包缓存 - Python 环境缓存 |
| 🟣 紫色 | 第四层 | Pip 包缓存 - Python 包缓存 |
| 🔴 红色 | 第五层 | NPM 包缓存 - Node.js 包缓存 |
| ✅ 绿色 | 快路径 | 本地缓存命中（秒级返回） |
| ❌ 红色 | 慢路径 | 缓存未命中（回源下载） |
| ⚪ 灰色虚线 | 上游源 | Docker Hub、清华镜像、PyPI、NPM 官方 |

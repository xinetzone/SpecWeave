# 三环闭环设计

## 总览

```mermaid
flowchart LR
    A["结伴闭环（人）<br/>邀请制入群<br/>四频道沉淀墙"]
    B["学习闭环（学）<br/>测→学→练→测<br/>7天复评"]
    C["变现闭环（钱）<br/>工具付费<br/>9.9元深度报告"]

    A -->|"想成长"| B
    B -->|"需要深度工具"| C
    C -->|"分享故事带来新人"| A
```

---

## 环一：结伴闭环（人）

### 入口机制

```mermaid
flowchart TD
    Entry["看到结伴站"] --> Choose["选频道卡片"]
    Choose --> Find["底部「找大师兄」入口"]
    Find --> Msg["一段话申请<br/>你好，我是大师兄。<br/>想进哪个频道？<br/>最近在安顿哪件事？"]
    Msg --> Review["人工审核"]
    Review -->|"答得认真"| Group["进微信群"]
    Review -->|"发广告或灌水"| Reject["不通过"]
```

### 四个沉淀墙

```mermaid
flowchart LR
    Jieban["结伴四频道"] --> s1
    Jieban --> s2
    Jieban --> s3
    Jieban --> s4

    subgraph s1 ["知足心"]
        Wall1["好事墙<br/>每天精选几条<br/>按日期倒序"]
    end
    subgraph s2 ["恒与伴"]
        Wall2["同行故事墙<br/>因为结伴而认识<br/>征得同意后上墙"]
    end
    subgraph s3 ["知和家"]
        Wall3["经验墙<br/>按阶段分<br/>备婚新婚已婚有娃"]
    end
    subgraph s4 ["愈多业"]
        Wall4["案例本<br/>AI真案例<br/>每条带踩坑"]
    end
```

### 设计原则

```mermaid
flowchart TD
    Principle["结伴设计三原则"] --> P1["不替代群聊<br/>只承接沉淀"]
    Principle --> P2["只看不写也能待得住<br/>行动可选不强迫"]
    Principle --> P3["匿名展示<br/>不强制实名"]
```

---

## 环二：学习闭环（学）

### 完整循环

```mermaid
flowchart LR
    T1["测<br/>3分钟体检<br/>三维雷达图"] --> S["学<br/>策略手册"]
    S --> P["练<br/>结伴频道日常"]
    P --> T2["测<br/>7天复评"]
    T2 --> Cmp["雷达图对比<br/>看到进步"]
    Cmp --> P
```

### 三维雷达图

```mermaid
flowchart TD
    Radar["学习体检三维"]
    D1["认知外包度<br/>多少事交给AI替你想"]
    D2["策略健康度<br/>学习方法对不对"]
    D3["动机自主度<br/>真想学还是焦虑驱动"]

    Radar --> D1
    Radar --> D2
    Radar --> D3
```

### 和结伴频道咬合

```mermaid
flowchart TB
    subgraph s5 ["结伴频道"]
        Zhizu["知足心<br/>每天三件好事"]
        Yuduo["愈多业<br/>AI案例分享"]
        Hengyu["恒与伴<br/>同行者打卡"]
        Zhihe["知和家<br/>婚姻沟通练习"]
    end

    subgraph s6 ["学习闭环练习"]
        Ex1["积极心理练习<br/>注意力从缺失转向拥有"]
        Ex2["费曼输出练习<br/>输出驱动输入"]
        Ex3["社会支持动机<br/>互相 accountability"]
        Ex4["关系学习实验<br/>关系先于道理"]
    end

    Zhizu -.-> Ex1
    Yuduo -.-> Ex2
    Hengyu -.-> Ex3
    Zhihe -.-> Ex4
```

### 学习记录

```mermaid
flowchart TD
    Record["我的学习记录"]
    R1["连续练习天数"]
    R2["体检记录对比<br/>第1天 第7天 第30天"]
    R3["好事墙案例本个人存档"]

    Record --> R1
    Record --> R2
    Record --> R3
```

---

## 环三：变现闭环（钱）

### 第一个付费产品

```mermaid
flowchart LR
    subgraph s7 ["免费版"]
        F1["10道题"]
        F2["三维雷达图"]
        F3["一句话总评"]
    end

    subgraph s8 ["付费版 9.9元"]
        P1["逐题解析"]
        P2["三维深度解读"]
        P3["个性化学习路径"]
        P4["7天练习计划"]
        P5["30天后复评邀请"]
    end

    F3 -->|"想深入了解自己"| P1
```

### 后续产品路线

```mermaid
flowchart LR
    V1["v1 学习体检深度报告<br/>9.9元"] --> V2["v2 好事墙高级版<br/>月度报告 年度回顾 导出"]
    V2 --> V3["v3 帛书老子注解库<br/>原文 逐句注解 版本对照"]
```

### 红线

```mermaid
flowchart TD
    Ban["变现红线"]
    Ban1["不卖课、不做训练营"]
    Ban2["不卖会员"]
    Ban3["不晒收入、不晒单"]
    Ban4["只卖工具：干净的价值交换"]

    Ban --> Ban1
    Ban --> Ban2
    Ban --> Ban3
    Ban --> Ban4
```

---

## 用户完整旅程

```mermaid
journey
    title 一个用户从邀请到付费的完整路径
    section 第0天
      看到结伴站: 5: 新人
      选频道: 5: 新人
      找大师兄申请: 5: 新人
    section 第1到3天
      进群融入: 4: 用户
      看别人内容: 4: 用户
      开始参与: 4: 用户
    section 第4天
      做学习体检: 4: 用户
      看到雷达图: 4: 用户
    section 第5到11天
      日常练习: 4: 用户
      记好事分享案例: 4: 用户
    section 第11天
      复评体检: 4: 用户
      看到进步: 5: 用户
    section 付费节点
      解锁深度报告: 3: 用户
    section 长期
      分享故事: 4: 用户
      带来新人: 4: 用户
```

## 数据流

```mermaid
flowchart TD
    subgraph s9 ["群聊日常"]
        Z["知足：三件好事"]
        Y["愈多：AI案例"]
        H["恒与：同行者"]
    end

    subgraph s10 ["沉淀墙"]
        W1["好事墙"]
        W2["案例本"]
        W3["故事墙"]
    end

    subgraph s11 ["学习记录"]
        R1["练习天数"]
        R2["输出次数"]
        R3["动机支持"]
    end

    C["学习体检器<br/>第1天 第7天 第30天"]
    Cmp["雷达图对比"]
    Rpt["深度报告（付费）"]

    Z --> W1 --> R1
    Y --> W2 --> R2
    H --> W3 --> R3

    R1 --> C
    R2 --> C
    R3 --> C
    C --> Cmp
    Cmp --> Rpt
```

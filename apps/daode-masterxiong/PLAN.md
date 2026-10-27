# 品牌蓝图总览

## 品牌层级

```mermaid
flowchart TD
    Brand["道德大师兄<br/>微信小程序 · 品牌"]
    Jieban["结伴（主推）<br/>/jieban/"]
    Xuexi["学习实验室<br/>/xuexi/"]
    Fupan["复盘<br/>/fupan/ · 待建"]

    Zhizu["知足·心<br/>感恩记录"]
    Hengyu["恒与·伴<br/>熟人介绍"]
    Zhihe["知和·家<br/>婚姻经营"]
    Yuduo["愈多·业<br/>AI实战"]

    Checkup["学习体检器"]
    Cycle["教学相长机制"]
    Playbook["循证策略手册"]

    Brand --> Jieban
    Brand --> Xuexi
    Brand --> Fupan
    Jieban --> Zhizu
    Jieban --> Hengyu
    Jieban --> Zhihe
    Jieban --> Yuduo
    Xuexi --> Checkup
    Xuexi --> Cycle
    Xuexi --> Playbook
```

## 三环闭环

```mermaid
flowchart LR
    A["结伴闭环（人）<br/>邀请制入群<br/>四频道沉淀墙"]
    B["学习闭环（学）<br/>测→学→练→测<br/>7天复评"]
    C["变现闭环（钱）<br/>工具付费<br/>9.9元深度报告"]

    A -->|"想成长"| B
    B -->|"需要深度工具"| C
    C -->|"分享故事带来新人"| A
```

### 环一：结伴闭环（人）

```mermaid
flowchart TD
    Entry["看到结伴站"] --> Choose["选频道"]
    Choose --> Apply["找大师兄申请"]
    Apply --> Review["人工审核"]
    Review -->|"答得认真"| Group["进微信群"]
    Review -->|"发广告/灌水"| Reject["不通过"]
    Group --> Chat["群聊日常"]
    Chat --> Settle["沉淀到小程序<br/>好事墙/故事墙/经验墙/案例本"]
    Settle --> New["新人看到故事<br/>申请进来"]
    New --> Entry
```

### 环二：学习闭环（学）

```mermaid
flowchart LR
    Test1["测<br/>3分钟体检<br/>三维雷达图"] --> Study["学<br/>策略手册"]
    Study --> Practice["练<br/>结伴频道日常"]
    Practice --> Test2["测<br/>7天复评"]
    Test2 --> Compare["雷达图对比<br/>看到进步"]
    Compare --> Practice
```

### 学习闭环与结伴频道咬合

```mermaid
flowchart TB
    subgraph s1 ["结伴频道"]
        Zhizu["知足·心<br/>每天三件好事"]
        Yuduo["愈多·业<br/>AI案例分享"]
        Hengyu["恒与·伴<br/>同行者打卡"]
        Zhihe["知和·家<br/>婚姻沟通练习"]
    end

    subgraph s2 ["学习闭环"]
        Practice["积极心理练习"]
        Feynman["费曼输出练习"]
        Account["社会支持动机"]
        Relational["关系学习实验"]
    end

    Zhizu -.-> Practice
    Yuduo -.-> Feynman
    Hengyu -.-> Account
    Zhihe -.-> Relational
```

### 环三：变现闭环（钱）

```mermaid
flowchart LR
    Free["免费版<br/>10题+雷达图+一句话"] -->|"想深入了解自己"| Pay["付费版 9.9元<br/>逐题解析+个性化路径+7天计划"]
    Pay --> Future["后续产品<br/>好事墙高级版<br/>帛书老子注解库"]
```

## 用户完整旅程

```mermaid
journey
    title 用户从邀请到付费的完整路径
    section 第0天
      看到结伴站: 5: 新人
      选频道: 5: 新人
      找大师兄申请: 5: 新人
    section 第1-3天
      进群融入: 4: 用户
      看别人内容: 4: 用户
      开始参与: 4: 用户
    section 第4天
      做学习体检: 4: 用户
      看到雷达图: 4: 用户
    section 第5-11天
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

## MVP路径

```mermaid
gantt
    title MVP 三阶段
    dateFormat YYYY-MM-DD
    section MVP1本周
    结伴闭环跑通           :done, m1a, 2026-10-26, 7d
    小程序首页四频道入口    :active, m1b, after m1a, 3d
    section MVP2两到四周
    学习体检器可交互       :m2a, after m1b, 14d
    我的练习记录页          :m2b, after m2a, 7d
    section MVP3一到两月
    体检器付费墙            :m3a, after m2b, 14d
    微信支付接入            :m3b, after m3a, 7d
    深度报告上线            :milestone, m3c, after m3b, 0d
```

## 数据流

```mermaid
flowchart TD
    subgraph s3 ["群聊日常"]
        Zhizu["知足：三件好事"]
        Yuduo["愈多：AI案例"]
        Hengyu["恒与：同行者"]
    end

    subgraph s4 ["沉淀墙"]
        Wall1["好事墙"]
        Wall2["案例本"]
        Wall3["故事墙"]
    end

    subgraph s5 ["学习记录"]
        Days["练习天数"]
        Outputs["输出次数"]
        Motive["动机支持"]
    end

    Checkup["学习体检器<br/>第1/7/30天"]
    Compare["雷达图对比"]
    Report["深度报告（付费）"]

    Zhizu --> Wall1 --> Days
    Yuduo --> Wall2 --> Outputs
    Hengyu --> Wall3 --> Motive

    Days --> Checkup
    Outputs --> Checkup
    Motive --> Checkup
    Checkup --> Compare
    Compare --> Report
```

## 核心红线

- 不催婚、不打分、不围观
- 零收费导流、反杀猪盘
- 不设表单、不收集个人信息
- 不卖课、不做训练营
- 邀请制是筛选，不是限制

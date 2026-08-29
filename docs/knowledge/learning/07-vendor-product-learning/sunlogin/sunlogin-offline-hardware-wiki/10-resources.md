---
id: "sunlogin-offline-hardware-wiki-10"
title: "参考资料与链接"
source: "../sunlogin-offline-hardware-wiki.md#参考资料与链接"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.toml"
date: "2026-07-04"
tags: ["参考资料", "官方链接", "技术名词", "市场报告", "相关Wiki", "版本信息", "术语解释"]
---
## 十一、参考资料与链接

### 官方产品页面

| 产品 | 官方链接 |
|---|---|
| 向日葵官网 | https://sunlogin.oray.com/ |
| 控控2（旗舰IPKVM） | https://sunlogin.oray.com/hardware/kongkong2/ |
| Q1（消费级入门） | https://sunlogin.oray.com/hardware/q1 |
| Q2Pro（工业级4G） | https://sunlogin.oray.com/hardware/q2pro-ble/ |
| Q0.5（口袋近场） | https://sunlogin.oray.com/hardware/Q0.5 |
| Q5Pro（专业级5G） | https://sunlogin.oray.com/hardware/Q5Pro |
| 向日葵硬件产品总览 | https://sunlogin.oray.com/hardware/ |
| 向日葵服务定价 | https://sunlogin.oray.com/price |

### 向日葵官方文档与支持

- 向日葵帮助中心：https://service.oray.com/
- Q1双唤醒方式说明：https://service.oray.com/question/47288.html
- Q2Pro分辨率说明：https://service.oray.com/question/17454.html
- 控控2 HDMI/VGA转接说明：http://service.oray.com/question/5409.html
- Q5Pro分辨率说明：https://url.oray.com/tWZHrq
- 手机兼容性列表：https://url.oray.com/HZHHrs
- Q2Pro技术支持服务：http://url.oray.com/tccsGb

### 市场报告与行业数据

- **洛图科技（RUNTO）**：《中国IPKVM线上零售市场年度数据报告》
  - 2024年度：贝锐向日葵无网远控IPKVM设备市场销量份额中国第一（统计范围：京东、天猫；产品：A2、Q2Pro）
  - 2025年度：贝锐向日葵无网远控IPKVM设备市场销量份额中国第一（统计范围：京东、天猫；产品：Q1、Q1Pro、Q2Pro、A2、Q0.5）
  - 数据统计时间：分别为2024年1月-12月、2025年1月-12月

### 相关技术名词解释

#### IPKVM相关

- **KVM**：Keyboard, Video, Mouse（键盘、视频、鼠标），一种通过一套键盘、显示器、鼠标控制多台计算机的硬件设备
- **IPKVM**：KVM over IP，基于IP网络的KVM技术，允许通过网络远程访问KVM控制端
- **BIOS/UEFI**：计算机基本输入输出系统/统一可扩展固件接口，计算机开机时最先运行的固件，负责硬件初始化和引导操作系统
- **HID**：Human Interface Device（人机接口设备），USB设备类规范中的一类，包括键盘、鼠标、游戏手柄等，操作系统原生支持无需驱动
- **HDMI**：High-Definition Multimedia Interface（高清多媒体接口），传输未压缩的视频和音频数据
- **HDMI-OUT环出**：IPKVM设备在采集HDMI输入信号的同时，将信号复制一份输出到本地显示器，不影响现场使用

#### 网络相关

- **WOL**：Wake-on-LAN（网络唤醒），通过发送特定网络数据包（Magic Packet）唤醒处于关机或休眠状态的计算机
- **P2P**：Peer-to-Peer（点对点），两台设备直接通信，数据不经过中间服务器中转
- **WiFi6**：即802.11ax标准，第六代WiFi技术，更高带宽、更低延迟、更多设备并发
- **4G LTE**：第四代移动通信长期演进技术，包括FDD-LTE和TDD-LTE两种制式
- **5G NR**：第五代移动通信新空口技术，支持NSA（非独立组网）和SA（独立组网）两种模式
- **SMA接口**：SubMiniature version A，一种常见的射频同轴天线接口，用于连接外置天线
- **DIN导轨**：德国工业标准导轨（DIN 35mm），工业电气设备安装的标准导轨，广泛用于机柜中PLC、断路器等设备的安装

#### 安全相关

- **RSA 2048**：RSA非对称加密算法，使用2048位密钥，用于密钥交换和数字签名
- **AES**：Advanced Encryption Standard（高级加密标准），对称加密算法，用于数据加密传输
- **多因子验证（MFA）**：使用两种或以上验证方式进行身份认证，提升安全性
- **物理隔离**：网络与其他网络完全没有物理连接，是最高等级的安全防护措施
- **跳板攻击**：攻击者通过控制一台设备作为"跳板"，进而攻击网络中的其他设备
- **看门狗（Watchdog）**：一种硬件定时器，设备异常死机时自动重启设备，保障高可用性

#### 工业相关

- **SECC**：Steel Electrolytic Cold Commercial（电解镀锌钢板），具有良好的耐腐蚀性和刚性，常用于工业设备外壳
- **宽温设计**：设备能够在较宽的温度范围内正常工作，工业级通常为-20~70℃
- **防浪涌**：Surge Protection，防止电压瞬间过高（如雷击）损坏设备的保护电路
- **双电源冗余**：设备支持两种电源输入方式（如DC电源+端子供电），一路断电时另一路可继续供电
- **导轨安装**：通过卡扣将设备固定在DIN35标准导轨上，是工业机柜的标准安装方式

### 本系列相关Wiki

- [向日葵开机盒子硬件分析](../sunlogin-bootbox-analysis.md)
- [向日葵智能插座Wiki](../sunlogin-smart-socket-wiki.md)
- [向日葵PDU电源分配器Wiki](../sunlogin-pdu-hardware-wiki.md)
- [向日葵摄像头SU1 Wiki](../sunlogin-camera-su1-wiki.md)
- [向日葵鼠标BM110/MM110分析](../sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵P4/P1Pro对比Wiki](../sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵安全Wiki](../sunlogin-security-wiki.md)

### 向日葵产品线覆盖

向日葵硬件产品线覆盖远程控制全场景：
- **无网远控IPKVM**：控控2、Q1、Q2Pro、Q0.5、Q5Pro、A2、Q1Pro（本教程介绍）
- **开机控制**：开机盒子、智能插座
- **电源管理**：智能PDU电源分配器
- **视频监控**：USB摄像头、SU1摄像头
- **外设**：蓝牙鼠标、键鼠等

### 版本信息

- **本教程版本**：v1.0
- **最后更新**：2026年7月4日
- **基于资料**：向日葵官方网站2026年公开产品页面内容
- **免责声明**：本教程基于官方公开资料整理，产品规格和价格以向日葵官方最新信息为准。本教程中标注"官方未详细公开"或"推测"的内容为基于产品定位和同系列产品的合理推断，仅供参考，不构成购买建议。

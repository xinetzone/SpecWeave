---
title: "openKylin 3.0 Kylin AI SDK 文字识别（OCR）能力落机 POC 实测（Desktop WSL）"
date: 2026-10-08
category: "tech"
tags:
  - openkylin
  - wsl
  - ai-sdk
  - ocr
  - tesseract
  - poc
  - llm
status: "verified"
security_level: "public"
source: "2026-10-08 本机实测（openKylin-3.0-desktop WSL 发行版，huanghe，WSL 3.0.2.0/内核6.18.40，gcc/g++ 15.2）；方法论 session sc-20261008-openkylin-ai-poc，链路 R→I→F→V→C。闭环主教程 I-3 自登记的『最小 POC』缺口；API 文档级事实见 [05 AI 三层体系](../concepts/05-ai-stack.md) 与 F-029，安装环境见 [双 WSL 镜像对照](wsl-dual-image-selection.md)。"
---

# openKylin 3.0 Kylin AI SDK 文字识别（OCR）能力落机 POC

> 本文回答一个被主教程 [I-3](../index.md) 明确登记为缺口的问题：官方那份 137K 字《OpenKylin AI SDK 开发手册》描述的 8 个能力域，**到底能不能在装好的 openKylin 3.0 上真的调通**？2026-10-08 我们在 Desktop WSL 发行版上完成了最小闭环——**安装 SDK → 编译调用「文字识别」接口 → 喂中英文图片拿到识别文本**，并钉死其本地后端就是 tesseract。结论先行：**OCR 能力域实测可用（本地 CPU、离线、不依赖云密钥/GPU/大模型），但识别精度中等、SDK 头文件只友好 C++、配置查询接口与系统权威值存在读数错位**；其余 7 个能力域仍停留在"成文未验证"。

---

## 1. POC 目标与判定标准

主教程 I-3 的证据边界原话："未实机安装 AI SDK 开发包、未逐接口跑通 8 个能力域……文档规模与接口形态只能证明『能力被设计并文档化』，不能证明『在任何硬件上当下可用』。最终采信仍需一次最小 POC（装包→调通一个文字识别或文本生成接口）。"

**本 POC 的最小通过判据**（全部满足才算闭环）：

1. `libkylin-ai-base` SDK 能从官方源装上；
2. 调用 `ocr_create_session()` 返回成功、拿到非空会话；
3. `ocr_get_text_from_image_file()` 对一张含中文的图片返回非空文本；
4. 证据能区分这次识别究竟走**本地引擎**还是**公有云**（不能"出了字就算"）。

> 为什么首选 OCR 而非文本生成：文字识别是 8 域中唯一**本地后端为传统 OCR 引擎（tesseract）、不需要下载大模型、不需要 GPU** 的能力，在无独显的 WSL 虚拟机上可确定性复现；而文本生成本地路径需自备 GGUF 模型（见 §7）。

---

## 2. 环境与镜像预装现状（R 阶段取证）

POC 前先对 1900 包的 Desktop 镜像做 AI 组件盘点，得到三个此前知识包未记录的事实：

| 组件 | 版本 | 实质 | 状态 |
|---|---|---|---|
| `kytensor-llm` | 1.0.0-ok0.7~1 | 包描述原文 "Inference of Meta's LLaMA model (and others) in pure C/C++"，即 **llama.cpp 的 openKylin 打包**（`libllama.so` + `libggml-cpu-*` 全套 CPU 指令集后端） | **已预装**，但无模型、无运行进程 |
| `kytensor-server` / `-client` / `-python` | 2.49.0.6-0ok11 | Triton Inference Server 2.49 定制；`/usr/bin/kytensor` 的 `--help` 输出即 tritonserver 用法 | 已随体系安装 |
| `llm-backend` | 1.0.1-0ok3 | Triton 的 llama.cpp 后端插件 `/opt/tritonserver/backends/llamacpp/libtriton_llamacpp.so` | **已预装**，但无 Triton 模型仓库配置 |
| `libkylin-ai-base2` / `-dev` | 2.0.0.0-ok1.0 | Kylin AI SDK 运行库（294 KB 薄封装）+ 开发头文件（70 KB） | **未预装**，官方源可装 |
| `kylin-ai-runtime` | 1.1.0.1-ok0.21 | AI SDK Runtime（46 MB，依赖 opencv 4.10、document-qa-service、vector-engine-client 等） | **未预装**，随 SDK 依赖拉入 |
| `kylin-ai-model-manager` | 0.0.0.1-ok7 | F-022 的端侧模型下载工具 | 未预装，可装 |
| `ollama` | — | F-023 的 DeepSeek-R1 工具 | **不在 openKylin 官方源**（需官方 install.sh 等文档三方式） |

**解读**：Desktop 镜像出厂即内置了一套「**Triton + llama.cpp CPU 推理引擎**」骨架，但不带模型、不启动服务——这是"预置能力、按需配模型"的设计；而面向应用的 Kylin AI SDK 与运行时反而要用户自行 `apt install`。系统侧开铭助手服务 `org.kylin.kaiming.service`（`/opt/kaiming-tools/bin/kaiming-system-dbus` DBus 守护）默认 enabled+active。

---

## 3. 安装与依赖链

```bash
# 在 openKylin-3.0-desktop 内（sudo 密码 openkylin）
sudo apt-get update
sudo apt-get install -y --no-install-recommends libkylin-ai-base-dev
```

- 实测下载 **39.1 MB**（官方源 `archive.build.openkylin.top`，约 1 秒），新增 4 个直接包：`libkylin-ai-base-dev`、`libkylin-ai-base2`、`kylin-ai-runtime`、`libkylin-ai-document-qa-service`；opencv/tesseract 等硬依赖多数已在镜像内。
- `libkylin-ai-base2` 的 Depends 直接揭示了 OCR 的技术栈：`libtesseract5 (>= 5.3.4)`、`tesseract-ocr-eng`、`tesseract-ocr-chi-sim`、`liblept5`（leptonica 图像处理）、`kylin-ai-runtime`。
- 落地版本：**tesseract 5.3.4-ok4**（leptonica-1.82.0）+ 语言包 `chi_sim / eng / osd`（4.1.0）。
- 磁盘：安装后 VHD 逻辑大小 14.36 GiB（15,414,067,200 字节，非稀疏、非 NTFS 压缩），较刚导入时 13.01 GiB 增约 **1.35 GiB**。
  > 测量纪律：曾用 `GetCompressedFileSizeW` 得到一次 4.00 GiB 的"真实占用"，与文件非稀疏/非压缩属性矛盾；经文件属性（Archive、无 Compressed）、`fsutil sparse queryflag`（NOT sparse）、`Length` 三源交叉，判定该次为 P/Invoke 测量假象，**不采信**。

---

## 4. SDK 接口形态（头文件实证）

开发包安装后头文件位于 `/usr/include/kylin-ai/`：

```
kylin-ai/
├── base.h common.h config.h
└── ai-base/
    ├── ocr.h nlp.h speech.h vision.h
    ├── modelconfig.h datamanagement.h remotemodelvendor.h
    └── private/
```

**OCR（`ai-base/ocr.h`，本文闭环的能力）**——接口极简洁，纯 C ABI：

```c
typedef enum { OCR_SUCCESS=0, OCR_SESSION_ERROR, OCR_PARAM_ERROR } OcrResult;
typedef void* OcrSession;
OcrResult ocr_create_session(OcrSession* session);
const char* ocr_get_text_from_image_file(OcrSession session, const char* image_file);
const char* ocr_get_text_from_image_data(OcrSession session,
                                         const char* image_data, unsigned int len);
void ocr_destroy_session(OcrSession session);
```

**部署策略（`config.h`）**：

```c
enum Capability   { CAPABILITY_NLP=0, CAPABILITY_SPEECH=1, CAPABILITY_VISION=2 };
enum DeployPolicy { LOCAL=0, PUBLIC_CLOUD=1, PRIVATE_CLOUD=2 };
// 一组 capability_settings_* 用于查询/设置各能力的开关、部署策略、模型与密钥(JSON)
```

**NLP 文本生成（`ai-base/nlp.h`，本文只登记未跑通）**：`nlp_create_session / nlp_init_session / nlp_set_result_callback / nlp_text_chat / nlp_text_chat_async / nlp_set_context_size / nlp_clear_context`——典型的**异步回调对话**接口，与 OCR 的同步取字符串不同。

---

## 5. 最小 POC：代码、编译与结果

### 5.1 一个坑：头文件是 C++ 友好、纯 C 不可编译

第一次用 `gcc` 编译 `.c` 文件直接失败：`config.h` 以 `enum ErrorCode {...}`、`enum Capability {...}` 定义，却用**裸类型名** `ErrorCode`/`Capability`/`DeployPolicy` 声明函数，而整个头文件树没有对应 `typedef`。C++ 中 enum 标签名可直接当类型名，纯 C 则报 `unknown type name 'ErrorCode'`。函数本身用 `extern "C"` 守卫、以 C ABI 导出，但**头文件要走 g++（.cpp）**。这对"按手册用 C 开发"的用户是个实际阻碍，建议官方补 typedef 或在手册注明 C++。

### 5.2 POC 程序（C++）

```cpp
// ocr_poc.cpp —— g++ -Wall -o ocr_poc ocr_poc.cpp -lkylin-ai-base
#include <cstdio>
#include <cstring>
#include <kylin-ai/config.h>
#include <kylin-ai/ai-base/ocr.h>

int main(int argc, char **argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s <img> [local|cloud]\n", argv[0]); return 2; }

    std::printf("[cap] enabled=%d policy=%d (0=LOCAL,1=PUB_CLOUD,2=PRIV_CLOUD)\n",
                capability_settings_is_enabled(CAPABILITY_VISION),
                capability_settings_get_deploy_policy(CAPABILITY_VISION));
    if (argc >= 3) {  // 可选：强制部署策略
        DeployPolicy p = (std::strcmp(argv[2], "local") == 0) ? LOCAL : PUBLIC_CLOUD;
        int rc = capability_settings_set_deploy_policy(CAPABILITY_VISION, p);
        std::printf("[cap] set(%d) ret=%d -> readback=%d\n", p, rc,
                    capability_settings_get_deploy_policy(CAPABILITY_VISION));
    }

    OcrSession session = nullptr;
    OcrResult rc = ocr_create_session(&session);          // ① 建会话
    std::printf("[ocr] create_session ret=%d session=%p\n", (int)rc, (void*)session);
    if (rc != OCR_SUCCESS || !session) return 1;

    const char* text = ocr_get_text_from_image_file(session, argv[1]);  // ② 识别
    if (text) std::printf("---- TEXT ----\n%s\n----------------\n", text);

    ocr_destroy_session(session);                          // ③ 销毁
    return 0;
}
```

造一张 720×220 中英文测试图（Pillow + 系统中文字体 `/usr/share/fonts/gb/国标小标宋-GBT2312.ttf`，白字内容 `openKylin AI SDK OCR 测试` / `Hello 2026 银河麒麟 12345`）。

### 5.3 实测结果

```
$ g++ -Wall -o ocr_poc ocr_poc.cpp -lkylin-ai-base && ./ocr_poc ocr_test.png
[cap] enabled=1 policy=1 (0=LOCAL,1=PUB_CLOUD,2=PRIV_CLOUD)
[ocr] create_session ret=0 session=0x31c89710
---- TEXT ----
openKvylin AI SDK OCR 测试
Hello 2026 银河户有12345
----------------
```

**判据 1–3 全部满足**：装包成功、建会话 `ret=0`、返回非空文本。识别出大部分中英文与数字，但带明显形近误识（`Kylin→Kvylin`、`麒麟→户有`），属开源 tesseract 中等精度的典型表现，不是高准确率商用 OCR。

### 5.4 判据 4：这次识别到底走本地还是云？（三源同轴钉死）

仅"出了字"不能证明走本地——默认策略查询一度返回 `PUBLIC_CLOUD`。用三条独立证据交叉：

1. **动态库直链本地引擎**：
   ```
   $ ldd /usr/lib/x86_64-linux-gnu/libkylin-ai-base.so.2 | grep -iE 'tesseract|lept|curl|ssl'
       libtesseract.so.5 => /usr/lib/.../libtesseract.so.5
       liblept.so.5     => /usr/lib/.../liblept.so.5
       libcurl.so.4 / libnghttp2.so.14 / libssl.so.3      # 云端能力的网络通道也在
   ```
   OCR 引擎（tesseract/leptonica）被**进程内直接链接**，无需联网即可调用。

2. **系统权威配置 = 本地、且无任何云密钥**：
   ```
   $ gsettings list-recursively org.openkylin.aisdk | grep -E 'vision|text'
   org.openkylin.aisdk.vision deploy-policy  'LOCAL'      # ← OCR 所属能力默认本地
   org.openkylin.aisdk.vision model-config  @a{sv} {}      # ← 空，无云端密钥
   org.openkylin.aisdk.text   deploy-policy 'PUBLICCLOUD'  # ← 文本生成默认云
   ```

3. **强制 LOCAL 后识别成功，且与 tesseract CLI 同源**：

   | 调用方式 | 识别输出 |
   |---|---|
   | SDK `set_deploy_policy(LOCAL)` | `openKvylin AI SDK OCR 测试` / `Hello 2026 银河户有12345` |
   | `tesseract ocr_test.png - -l chi_sim+eng`（CLI 直出） | `openKylin AI SDK OCR 测试` / `Hello 2026 银河麒蛮 12345` |

   两者**引擎质感一致、具体误识字不同**（CLI 把 Kylin 认对、却把"麒麟"认成"麒蛮"）——说明 SDK 不是 shell 调用 tesseract 命令，而是经 **libtesseract 库 API** 调用，页面分割/二值化等预处理参数与 CLI 默认不同，故结果略异。

**结论**：OCR 能力 = **本地 tesseract 5.3.4（chi_sim+eng）CPU 离线识别**，不依赖网络、云密钥、GPU、大模型。

### 5.5 发现一个接口一致性问题（待官方确认）

- C API `capability_settings_get_deploy_policy(CAPABILITY_VISION)` **首读返回 1（PUBLIC_CLOUD）**，与 dconf/gsettings 权威持久值 `LOCAL` **不一致**；
- `capability_settings_set_deploy_policy(CAPABILITY_VISION, LOCAL)` **返回 1（按 config.h 是 CONFIG_FAILED）**，但随后读回与 gsettings 都确认为 LOCAL——即**实际生效了、返回码却像失败**。

本 POC 不强行归因（可能是枚举映射、dconf 缓存初始化时序，或该返回码语义并非"成败"），仅如实登记：**部署策略以 `gsettings org.openkylin.aisdk.vision deploy-policy` 为权威，SDK 查询/设置 API 的返回值在 2.0.0.0 上不宜单独作为判据**。POC 结束后该键仍为系统出厂值 `LOCAL`，未留下配置副作用。

---

## 6. 对主教程 I-3 证据边界的裁决

| I-3 原话（2026-09-29） | 2026-10-08 POC 裁决 |
|---|---|
| 未实机安装 AI SDK 开发包 | ✅ 已安装 `libkylin-ai-base-dev 2.0.0.0` + runtime，官方源可得 |
| 未逐接口跑通 8 个能力域 | 🟡 **8 域中跑通 1 域（OCR/属 VISION）**；音频、向量化、文本生成、图像生成、主体分割、通用分割 6 域 + 错误码体系仍为**成文未验证** |
| 成文度只能证明"被设计并文档化"，不证明"当下可用" | ✅ 对 OCR 已升级为**本机实测可用**：本地 CPU 离线、中英识别可出结果但精度中等；"必要非充分"判断成立——有手册确实能装能调，但准确率、配置 API 一致性都达不到"看手册就放心" |
| 最终采信需最小 POC（装包→调通一个 OCR/文本生成接口） | ✅ 本文即该 POC，判据四项全满足 |

**新增可迁移教训**：评估这类"一套接口适配本地/云多家模型"的 OS 级 AI SDK，"能力可调通"与"配置 API 可信"、"本地引擎可用"与"识别质量可用于生产"是三件不同的事，必须分别取证；默认部署策略要以系统持久配置（dconf/注册表）为权威，不能只信运行时查询接口的一次读数。

---

## 7. 未闭环项与后续 POC 建议

1. **文本生成（NLP）本地路径**：`org.openkylin.aisdk.text` 默认 `PUBLIC_CLOUD` 且无密钥；离线对话需要用镜像**已预装的 kytensor-server（Triton 2.49）+ llama.cpp backend**，自备一份 GGUF（如 DeepSeek-R1 蒸馏 Qwen 1.5B/7B Q4，约 1–5 GB）并按 llama.cpp backend 规范组织模型仓库（`config.pbtxt`）。本机 16 GiB 内存、CPU only，1.5B/7B-Q4 可跑、更大档不行；这是下一个确定性较高的 POC。
2. **云端路径**：需申请百度/讯飞等平台密钥（`capability_settings_set_model_config` 的 JSON 形态见 `config.h` 注释），属账号与网络行为，本环境不做。
3. **其余能力域**：speech（含实时/流式）、embedding 向量化、图像生成、两类图像分割均未测；它们对模型文件/硬件的要求各异。
4. **接口一致性**：§5.5 的部署策略读数/返回码错位，建议在正式环境或向社区 issue 复核后再定性。
5. 本 POC 工程（`ocr_poc.cpp`、`make_image.py`、`ocr_test.png`）位于 WSL 挂载的 Windows 工作目录 `C:\Users\xinzo\ai-poc\`（非本仓文件，仅用于复现）。

---

## 8. 相关文档

- [05 AI 三层体系：使用、配置、开发](../concepts/05-ai-stack.md)（8 能力域文档级导读、模型配置分版、AI 贡献守则）
- [openKylin 主教程 I 阶段 I-3](../index.md)（AI"三层成文"洞察与证据边界）
- [双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md)（本 POC 所用 Desktop 镜像的安装、磁盘与 xrdp）
- [openKylin 桌面启动与日常使用教程](wsl-desktop-startup-tutorial.md)

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261008-openkylin-ai-poc | msg=AI SDK 落机 POC：闭环主教程 I-3 最小验证缺口 | ctx={"scenario":"problem","chain":"R-I-F-V-C","target":"libkylin-ai-base 2.0 OCR"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R9 | event=GATE_PASSED | session=sc-20261008-openkylin-ai-poc | msg=取证：镜像预装kytensor-llm(llama.cpp)+Triton后端无模型；SDK/runtime未预装可apt；OCR=tesseract栈
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=F3 | event=POC_PASSED | session=sc-20261008-openkylin-ai-poc | msg=OCR四判据全满足：装包/g++编译/create_session=0/中英文出文本；ldd+gsettings+CLI三源钉死本地tesseract CPU离线
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V6 | event=FINDINGS | session=sc-20261008-openkylin-ai-poc | msg=发现2问题：config.h纯C不可编译(C++友好)、配置API读数与dconf错位/set返回码反直觉；7能力域仍成文未验证；NLP本地需自备GGUF
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261008-openkylin-ai-poc | msg=AI SDK OCR 能力域成文→实测可用；新增事实F-058~F-066、信源S34 | ctx={"gates":["G1","G2","V","G4"]}
```

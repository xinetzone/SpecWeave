---
title: "百度Unlimited-OCR技术文章分析"
source: "微信公众号文章（defuddle提取）"
date: "2026-07-09"
project: "Baidu Unlimited-OCR"
total_params: "3B"
active_params: "500M"
sota_benchmark: "OmniDocBench v1.5: 93.23%, v1.6: 93.92%"
github_url: "https://github.com/baidu/Unlimited-OCR"
---

# 百度Unlimited-OCR技术文章

<!-- 章节划分说明：
  第1章：项目概述（核心突破与定位）
  第2章：R-SWA机制（Reference Sliding Window Attention）
  第3章：DeepEncoder（视觉编码压缩）
  第4章：性能数据（基准测试与效率对比）
  第5章：推理方式与使用教程（Transformers/SGLang部署）
  第6章：局限性与结语（当前不足与项目信息）
-->

---

## 第1章：项目概述

就在刚刚，百度闷声干了票大的。

最新的开源项目Unlimited-OCR，总参数为3B，实际激活只有500M，在大模型时代已经可以忽略不计了。

但是就是这么小的一个模型。

在OmniDocBench v1.5上得到93.23%的总分，在v1.6上又提高到93.92%，刷新了端到端SOTA。

更夸张的是，它还做了一件以前的所有OCR模型都没有做过的事情：

一口气把40多页的文档全部解析出来，并且不会出现记忆丢失或者速度下降的情况。

概括起来就是一句话。

其实它就是用来一口气把几十页PDF读完，不丢东西、不减速的文档解析工具。

究其原因，在标准的注意力机制下KV cache会随着输出长度线性增加。

内存承受不了了，速度越来越慢，并不是模型不想记住东西，而是记不住。

Unlimited-OCR 的主要突破是将"软遗忘"机制加入到模型中。

---

## 第2章：R-SWA机制

它把长文档解析的痛点给解决了。

**01 R-SWA 机制。**

它提出了一种叫做Reference Sliding Window Attention(R-SWA)的方法来模仿人抄书时的注意方式。

眼睛盯着原文，只回头看刚写下的几行。

![R-SWA示意图](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLiaLYaTJcOIic43FJsknibQompECvLsLvNMJUeCLauVq1JsvUy54icLibKicoPE3IwDTjHiaTj4ibJzjS0ictjHDRm5P4s2BL3JESZEbTg/640?wx_fmt=png&from=appmsg)

每生成一个 token，R-SWA 都会去看全部"参考 token"，以确保模型一直能看到完整的原文。

但是在输出的那边，它只回溯到前面的 128 个 token，就跟你抄书的时候只看了一眼刚刚写下的那几行一样。

![R-SWA对比图](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblIybVEHHf5I8Xp83mIN0RzyMQLTFnZVfiaaibH5Tavcgfibv6ANic3iaW99AcqGEamrCyV4YOHib0DickMBKG1GibXfJaUKpoCk1hyQZEE/640?wx_fmt=png&from=appmsg)

落实到实现上就是把所有的注意力层都换成R-SWA。

把KV cache变成一个固定大小的队列，在产生新的token的时候，最旧的一个会被挤出去。

输出 1 万个 token 和 10 万个 token，内存占用是完全一样的。

---

## 第3章：DeepEncoder

**02 DeepEncoder。**

配合 R-SWA 的，是继承自 DeepSeek-OCR 的 DeepEncoder。

该编码器可以将一个 1024×1024 的 PDF 页面压缩成只有 256 个视觉 token，压缩比达到 16 倍。

![DeepEncoder示意图](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblLKDBHLgiaEAmx7mwnGvQZ0bQW8Xz54Qv42Zz0AmEJ7NhIp3z8bOdGicm2hERasYbpc4zrxYolgibGzxG6lTl4SRy4DmSm0ic6RSIQ/640?wx_fmt=png&from=appmsg)

对于长文档而言，视觉token编码只进行一次就停止了，整个解码过程不参与状态转移。

图像信息一直都很清楚，并不会变得越来越模糊。

这个设计有个很关键的地方：视觉 token 不参与状态转移。

R-SWA 把视觉token挡在了状态转移之外，这就是它与普通的线性注意拉开距离的地方。

---

## 第4章：性能数据

**03 性能数据。**

在OmniDocBench v1.5上，Unlimited-OCR 得到了 93.23% 的总分。

![OmniDocBench v1.5结果](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblI2hoZ7Mjx0nQwibomnbAHCOdQfCjDdJQ1z2icqwL77jdTzEVN6ZSnQZ1Jq8EZmuvgU8nVficB4HgtZlOC3ZwwAHXLKgVTjSbkF6I/640?wx_fmt=png&from=appmsg)

比DeepSeek-OCR的87.01%高出6.22个百分点，在更新后的 v1.6 上也以 93.92% 的成绩获得端到端SOTA。

更牛X的是，它只用了 500M 的激活参数就超过了 235B 的 Qwen3-VL（89.15%）。

就连 Gemini-2.5Pro 也只达到了 88.03%，而激活参数不足他们十分之一的人，反而把他们都甩在了后面。

长文档测试结果也十分有力：同时输入 20 页文档，编辑距离只有 0.057。

即使输入了40页以上的内容，也仍然被限制在了 0.11 以内，而 Distinct-35 则达到了 97%。

几十页一气呵成地转录下来，没有重复的地方。

![长文档测试结果](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblJbSicMt2MA1skhh3WXxCXVZI58fqyIR5IHjRXoVHwhjxfWVUZYkmOQIG3hlDXicgtU1tprgH4EFZQiaGy1NvBILnDIHfxyetNMuI/640?wx_fmt=png&from=appmsg)

在效率上也占了上风，在输出到 6144 个 token 的时候，Unlimited-OCR 的 TPS 达到了 7847。

![TPS对比](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblKLM0HibNJDj6XcQhcoibc1zwrDEyj8IeZx9j7XOwPcTticsLcSTEYkRBFYkhmZ8JBCJvYjs7KL2GcicnxxUp84dweQuwibE8kSIUW8/640?wx_fmt=png&from=appmsg)

DeepSeek-OCR 已经跌到了 5822，差距达到了 35%。

说实话，这个结果有点超出预期。

这其实只是一个激活参数约 5 亿的 MoE 小模型。

它基于 DeepSeek-OCR 稍微继续训练了 4000 步左右，就跑出了这样的结果。

投入不大，但是效果很好——R-SWA 对于解析任务来说就是一份真正的"免费午餐"。

**04 两种推理方式。**

Unlimited-OCR 有两种推理方式：Transformers、SGLang。

用 Transformers，安装好 torch、transformers、PyMuPDF 这几个依赖之后，就可以直接从 Hugging Face 加载模型来运行了。

![Transformers代码示例](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblKzibG7KaRBg8YGaWrA0JjwPBcYkyBEUemj6aLsyw6ibYaK61CysfXr6m0y3UDxp6xiaAGC6DCvAxkwknJ6QQQCFKLPL4VSRFNB0Q/640?wx_fmt=png&from=appmsg)

PDF 处理比较麻烦一些：要先用 PyMuPDF 把 PDF 页面转换为图片，然后再进行批量解析。

README 中有完整的示例代码，dpi 默认为 300，已经很清晰了。

SGLang方式适用于大批量处理以及高效率推理。

启动服务器之后可以使用OpenAI-compatible API来发送请求，并且支持流式输出。

---

## 第5章：推理方式与使用教程

看完这些功能，相信各位已经迫不及待了。

最低门槛的打开方式其实很简单。

第一种方法是使用 transformers 快速上手

先安装依赖：

pip install torch、transformers、pymupdf

加载模型并解析单页文档：

![单页解析代码](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblIV0XfmrKveNjIyE9gzM0dXicicqsy478VSkCWcEFE4I1ZUHB0icpib2UlpPSfHTfZ9j00iaL5OwzcMdA7nGm4UQ7MyxgppPtXdkmTs/640?wx_fmt=png&from=appmsg)

PDF 多页处理示例：

![多页处理代码](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblIpCDXPCKpD14ickBdImYjmPACSib9XWibiag5wU3Ivus6LgECEJNUNKWeQf4CxsbbELmV6z65MkprJEkTAup72GcdsVBdpGoibNdKQ/640?wx_fmt=png&from=appmsg)

第二种方法是使用SGLang进行高效率的推理

启动服务器：

python -m sglang.launch_server --model-path baidu/Unlimited-OCR --port 30000

使用API调用的方式为：

![SGLang API示例](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblIKwFfZn80mJibVrCL0zJ1drmu6sHHVp9djiblWKyWhHM9EpYn0ib5yI5KJEFgkRWr8BMHRWXMMkznYb0ibauQCQQ3qP5zZPqocYiak/640?wx_fmt=png&from=appmsg)

---

## 第6章：局限性与结语

到这里缺点也给大家提提。

目前只支持 Base 和 Gundam 两种模式，而且多页文档功能只有 Base 模式能用。

模型上下文为 32K 左右，如果文档很长就需要自己进行分段再处理。

PDF 不能直接丢进去识别，要先转换成图片。

推理要用到GPU，目前还没有CPU方案。

另外在 README 中没有找到明确的开源协议说明，如果要商用的话，最好先核实一下授权的问题。

## 写在最后

有趣的是，在 GitHub 的致谢中，DeepSeek-OCR 排名靠前。

![GitHub致谢截图](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLD5oOh3ExYIgDNfadto5zoa1zS0JZx3K35m9PfzuLOvsicDicm0qyzAzTQF4hEleSwKSFmPphIukjicsIyo8oXIiba9MoN1De7c/640?wx_fmt=png&from=appmsg)

业内爆料的主要人物是 DeepSeek 离职的 OCR 大神魏浩然。

他之前在阶跃星辰搞过 GOT-OCR2.0，履历以及时间上都是相符的。

最后我想说的是，大神走到哪里都是大神。

有意向的朋友可以在项目中自己尝试一下。

项目刚开源，还没有开源协议，感兴趣的同学可以去 GitHub 仓库看看源码和文档。

开源地址：https://github.com/baidu/Unlimited-OCR

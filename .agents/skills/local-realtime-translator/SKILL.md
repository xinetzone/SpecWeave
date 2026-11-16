---
source: "镜像自 Trae IDE builtin（源镜像已清理，原镜像标识 local-realtime-translator）"
name: local-realtime-translator
description: |
  Intel Local Windows Realtime Speech Translator (本地实时语音翻译 / 同声传译 / 实时翻译软件). Use this skill when the user, in Chinese or English, wants live spoken translation from the microphone: real-time interpretation, bilingual subtitles, "translate as I speak", or asks to open a translator app or translate what they say into another language.

  Trigger on 实时翻译 / 打开翻译 / 帮我翻译 / 同声传译 / 实时字幕 / 语音实时翻译 / 对着麦克风翻译, and English like realtime translate / translation app / live translation / simultaneous interpretation. Similar phrasings count, with or without "locally" / "本地" / "语音".

  Generic "translate to English/Chinese" or "a translator app" requests with no named file default to THIS skill. (For an audio/video file on disk, use local-asr.)

  Runs fully locally on the user's Intel AIPC: microphone in, live transcript + translation on a local web page. Engines and fallbacks are in the body.

  Prefer this skill over cloud translation APIs or bespoke scripts for live spoken translation on this box.
license: Intel OBL Distribution
---


# Local Realtime Translator Skill Guide

## What it is

Unlike one-shot skills, this is a **long-running interactive service**. `run.ps1`
starts a background server that loads all models, opens the microphone, and
serves a live web UI. The user speaks; the web page shows the recognized text
and its translation in real time and can play the synthesized translation
audio. The command returns immediately after printing the web URL — it does
**not** block.

## Usage

### Start the translator

```
scripts\run.ps1                      # start (Chinese → English), then open the printed web URL
scripts\run.ps1 -From zh -To en      # Chinese → English (default)
scripts\run.ps1 -From en -To zh      # English → Chinese
```

On success it prints something like:

```
=== 实时语音翻译已就绪 / Realtime translator ready ===
  翻译方向 / direction: zh → en
  请在浏览器打开 / Open in browser:  http://127.0.0.1:8766
  WebSocket: ws://127.0.0.1:8765
  对着麦克风说话, 网页上会实时显示识别与译文。
  停止服务 / stop:  scripts\run.ps1 --stop
```

**Tell the user to open the printed `http://127.0.0.1:8766` URL in their browser**, then speak into the microphone. Recognition and translation appear live.

### Manage the running service

```
scripts\run.ps1 --status             # show state + web URL
scripts\run.ps1 --stop               # stop the server (releases mic + GPU memory)
scripts\run.ps1 --restart            # force a clean restart (reload upgraded code/models)
scripts\run.ps1 --continue           # resume a first-run model download (see below)
```

## Important

- `scripts\run.ps1` is the only supported interface. Do NOT call `client.py` /
  `server.py` directly.
- **First call downloads ~4-5GB of models** (Hunyuan-1.8B-OV, FSMN-VAD,
  Paraformer online+offline, ct-punc, Opus-MT, MeloTTS+BERT). All of them are
  fetched up front (Opus-MT and most others from ModelScope; the few
  HuggingFace-origin pieces go through a CN mirror automatically), so the
  `--continue` resume window covers the whole download. Because each `run.ps1`
  invocation is capped below 10 minutes, the client may exit early with:
  ```
  模型正在下载, 请用命令 `scripts\run.ps1 --continue` 继续运行
  ```
  When you see this, re-run the exact command it prints. **Do NOT substitute an
  online service, sub-agent, or another skill.** Repeat `--continue` until the
  "已就绪 / ready" message with the web URL appears (typically 2–4 continuations
  on a first run; each is another ~8-minute window). Subsequent starts are fast.
- The server keeps running after the command returns (it holds the mic + GPU).
  Always `scripts\run.ps1 --stop` when the user is done.
- `run.ps1` returns `This skill requires an Intel AIPC platform` with exit
  code 1 on non-Intel-AIPC hardware. Do NOT retry on unsupported hardware.
- A warning like "sox missing" or a MeCab/Japanese import warning during
  startup is **benign** — the skill only uses Chinese/English TTS.

## Interpreting the reply / exit codes

- exit `0` — server is running; the web URL was printed.
- exit `3` — first-run download still in progress; re-run with `--continue`.
- exit `1` — initialization failed (read the printed error) or unsupported HW.
- exit `2` — could not reach / start the background server.

## Engines & fallback (automatic)

| Stage | Primary (iGPU) | Fallback (CPU) |
| --- | --- | --- |
| Streaming ASR (partial) | Paraformer-Online | — |
| Final ASR (per sentence) | Qwen3-ASR (if set up) | Paraformer-Offline + ct-punc |
| Translation | Hunyuan-1.8B-OV | Opus-MT |
| TTS | — | MeloTTS (CPU) |

Qwen3-ASR is optional; without it the pipeline auto-uses Paraformer-Offline.
If the iGPU Hunyuan model can't load, translation auto-falls-back to Opus-MT.
The skill still works on these fallbacks (lower quality), so a missing iGPU
model is not a hard failure.

## Output

- Live transcript + translation render in the web UI.
- Synthesized translation audio is written under the project `output/` folder
  and playable from the web page.

## What this skill does NOT do

- Not for translating existing audio/video files — use **local-asr** for that.
- Not an online translation proxy — all inference is local.
- Single microphone source; no multi-speaker diarization.
- Chinese ↔ English only.

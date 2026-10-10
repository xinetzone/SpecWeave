# 配套工程：sticker-studio

Wiki《xuan-compose 实战：手帐贴纸风格照片生成》的可运行配套工程。目录结构：



```
examples/
├── compose.yaml          # 编排主文件（generator / gallery / keychroma 三服务）
├── .env.example          # 环境变量样板（复制为 .env，勿提交真实值）
├── secrets/
│   └── ark_key.txt       # 需自行创建：写入火山方舟 ARK_API_KEY（勿提交）
├── photos/               # 输入照片（自行放入，bind 到容器 /work/photos）
├── out/                  # 双产物输出（card.png / stickers-chroma.png / stickers.png）
├── prompts/
│   ├── card.txt          # 记忆卡 I2I 提示词模板（六贴纸 + 三关键词规范）
│   └── stickers.txt      # 色幕贴纸稿 I2I 模板（{CHROMA_KEY} 占位）
├── generator/            # 生图服务镜像（FastAPI 长驻 + CLI 一次性双形态）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── generate.py
└── keychroma/            # 色幕去底一次性任务镜像
    ├── Dockerfile
    ├── requirements.txt
    └── remove_chroma_key.py
```

## 最小跑通步骤



```
cd examples
cp .env.example .env                 # 需要覆盖时再改
mkdir -p secrets photos out
printf '你的ARK_API_KEY' > secrets/ark_key.txt
# 把一张旅行/街景照片放到 photos/in.jpg

# 1) 静态校验与预演（不需要真正起容器）
xuan-compose config --quiet
xuan-compose --dry-run up

# 2) 一次性流水线：照片 → 记忆卡 + 色幕贴纸稿
xuan-compose run --rm --entrypoint python generator generate.py pipeline photos/in.jpg "Crater Smoke" "Blue Summit" "Quiet Ridge"

# 3) 一次性去底：色幕贴纸稿 → 透明底 PNG
xuan-compose run --rm keychroma -- /work/out/stickers-chroma.png /work/out/stickers.png --soft-matte --despill --edge-contract 1

# 4) 可选：起长驻 API + 成品画廊
xuan-compose --profile web up -d
#   API：http://localhost:8000/health    画廊：http://localhost:8080
xuan-compose --profile web down   # 清理同样要带 --profile web，否则 gallery 容器会被漏掉
```

> 前置：已安装 Podman 与 
>
> `xuan-compose`
>
> （
>
> `pip install -e .`
>
> ，Python ≥ 3.14）。
> 生图环节调用火山方舟 Seedream 5.0 Pro（OpenAI 兼容 
>
> `images/generations`
>
> ），
> 需要可用的 
>
> `ARK_API_KEY`
>
> ；去底环节纯本地 Pillow/numpy，不产生网络调用。
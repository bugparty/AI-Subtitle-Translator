# 🎬 AI 驱动的字幕翻译器（AV 风格识别，多语言支持）

本项目使用 OpenAI/Gemini 模型，将任意语言的字幕文件批量翻译为自然流畅的简体中文或英文字幕，**自动识别 AV（成人影片）风格字幕**，并动态切换适当的翻译风格。

---

**English users, please refer to the [English version](README.md)**

---

## ✨ 特性功能

- ✅ **自动识别 AV 风格字幕**
- 🎭 普通对白使用专业书面翻译，AV 对白使用真实、情绪化、口语化的翻译
- 💬 支持 GPT-4、Gemini、Cloudflare AI Gateway 等接口
- 🔁 支持中断恢复、翻译进度保存
- 🧠 去重处理，仅对唯一句子进行翻译，节省 API 调用
- 🧼 自动将翻译结果合并回 `.srt` 字幕中，支持中文或英文输出

---

## 📦 安装依赖

需要 Python 3.8+，并安装以下依赖：

```bash
pip install openai tqdm python-dotenv srt
```

---

## 🔐 配置 API 密钥

创建 `.env` 文件，可以从 `.env.sample` 文件复制，并填入以下内容：

```env
GEMINI_API_KEY=你的 API Key
CLOUDFLARE_GATEWAY_URL=https://api.openai.com/v1  # 可选，用于 Cloudflare Gateway 代理
OPENAI_MODEL_NAME=你的模型名（默认 gemini-2.0-flash 或 gpt-4）
```

---

## 🚀 使用方法

```bash
python translate_srt.py -i input.srt
```

### 可选参数：

```bash
-o, --output   指定输出文件路径（默认自动命名为 input.zh.srt 或 input.en.srt，取决于语言）
-l, --language 指定目标语言（默认：zh 表示简体中文，en 表示英文）
```

运行后脚本将：

1. 提取字幕中唯一的句子
2. 自动判断是否为 AV 风格内容
3. 使用对应翻译 prompt 调用 GPT 模型翻译
4. 生成翻译字幕并保存为 `.zh.srt` 或 `.en.srt`

---

## 📁 输出示例

输入文件：

```
input.srt
```

输出文件：

```
input.zh.srt
translation_progress.json  # 中间进度缓存，可断点续译
```

---

## 🧠 AV 风格识别规则

脚本会自动检测字幕中是否包含如下高频词汇：

```
イく、舐めて、おまんこ、乳首、気持ちいい、喘ぎ、制服、透けてる、生活指導 等
```

匹配后即使用“真实情色翻译”风格进行处理。

---

## 🛠️ 自定义 Prompt（可选）

你可以修改 `AV_PROMPT` 与 `GENERIC_PROMPT` 常量，自定义你的翻译风格。例如是否保留语气助词、是否带羞涩语调等。

---

## 📌 TODO（可选扩展）

* [ ] 支持多语言字幕格式（ASS、VTT、JSON）
* [ ] 双语对照字幕输出
* [ ] 命令行指定强制风格 `--force-style av` / `generic`
* [ ] 翻译结果打标签（高潮、命令、情绪等）

---

## 📄 版权声明

本项目仅供**学习与研究用途**，请勿用于任何违反法律法规的用途。请自行确保 API 使用和字幕内容的合规性。

---


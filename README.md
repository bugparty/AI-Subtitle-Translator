# 🎬 Japanese Subtitle Translator (AV-aware GPT Subtitle Translation)

This project uses OpenAI/Gemini models to batch translate Japanese `.srt` subtitle files into natural and fluent Simplified Chinese or English subtitles. It **automatically detects AV (adult video) style subtitles** and dynamically switches to the appropriate translation style.

---

**中文用户请参考 [中文版介绍](README_cn.md)**

---

## ✨ Features

- ✅ **Automatic detection of AV-style subtitles**
- 🎭 Professional written translation for normal dialogues, realistic and emotional translation for AV dialogues
- 💬 Supports GPT-4, Gemini, Cloudflare AI Gateway, and more
- 🔁 Supports interruption recovery and progress saving
- 🧠 De-duplication: translates only unique sentences to save API calls
- 🧼 Automatically merges translations back into `.srt` subtitles with support for Chinese or English output

---

## 📦 Installation

Requires Python 3.8+ and the following dependencies:

```bash
pip install openai tqdm python-dotenv srt
```

---

## 🔐 API Key Configuration

Create a `.env` file  by copy from .env.sample, and add the following:

```env
GEMINI_API_KEY=your_api_key_here
CLOUDFLARE_GATEWAY_URL=https://api.openai.com/v1  # Optional, for Cloudflare Gateway proxy
OPENAI_MODEL_NAME=your_model_name (default: gemini-2.0-flash or gpt-4)
```

---

## 🚀 Usage

```bash
python translate_srt.py -i input.srt
```

### Optional Parameters:

```bash
-o, --output   Specify output file path (default: input.zh.srt or input.en.srt based on language)
-l, --language Specify target language (default: zh for Simplified Chinese, en for English)
```

After running, the script will:

1. Extract unique sentences from the subtitles
2. Automatically detect if the content is AV-style
3. Use the appropriate translation prompt to call the GPT model
4. Generate translated subtitles and save them as `.zh.srt` or `.en.srt`

---

## 📁 Output Example

Input file:

```
input.srt
```

Output files:

```
input.zh.srt
translation_progress.json  # Intermediate progress cache for resuming
```

---

## 🧠 AV Style Detection Rules

The script automatically detects subtitles containing the following keywords:

```
イく, 舐めて, おまんこ, 乳首, 気持ちいい, 喘ぎ, 制服, 透けてる, 生活指導, etc.
```

If detected, it uses the "realistic erotic translation" style.

---

## 🛠️ Customizing Prompts (Optional)

You can modify the `AV_PROMPT` and `GENERIC_PROMPT` constants in `prompts.py` to customize your translation style. For example, whether to retain interjections, add shy tones, etc.

---

## 📌 TODO (Optional Extensions)

* [ ] Support for multi-language subtitle formats (ASS, VTT, JSON)
* [ ] Bilingual subtitle output
* [ ] Command-line option to force style `--force-style av` / `generic`
* [ ] Tagging translation results (e.g., climax, command, emotion)

---

## 📄 Disclaimer

This project is for **educational and research purposes only**. Do not use it for any illegal activities. Ensure compliance with API usage and subtitle content regulations.

---

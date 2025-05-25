import srt
from openai import OpenAI
import os
from tqdm import tqdm
from collections import OrderedDict
from dotenv import load_dotenv
import json # Added import
from prompts import GENERIC_PROMPT_ZH, GENERIC_PROMPT_EN, AV_PROMPT_EN, AV_PROMPT_CH  # Import prompts

# === Load environment variables (requires .env file with OPENAI_API_KEY) ===
load_dotenv()

client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),
                base_url=os.getenv("CLOUDFLARE_GATEWAY_URL",
                os.getenv("OPENAI_COMPETIBLE_API_URL", "https://api.openai.com/v1")))

def is_av_line(text):
    av_keywords = [
        "イく", "イク", "イきそう", "おまんこ", "乳首", "中に出して", "気持ちいい", "舐めて",
        "喘ぎ", "あっ", "うっ", "はぁ", "んっ", "だめ", "もっと", "入れて", "やめて",
        "奥まで", "いっぱい出して", "変な校則", "透けてる", "制服", "生活指導", "退学", "先生"
    ]
    return any(word in text for word in av_keywords)

# === Extract unique subtitle lines ===
def extract_unique_lines(subs):
    unique_map = OrderedDict()
    for sub in subs:
        text = sub.content.strip()
        if text and text not in unique_map:
            unique_map[text] = None
    return list(unique_map.keys()), unique_map

# === GPT batch translation ===
def translate_unique_lines(unique_lines, system_prompt, target_lang="zh", batch_size=100, max_retries=5, retry_delay=5, progress_file="translation_progress.json"): # Added progress_file and target_lang
    translated_map = {}
    # Load progress if exists
    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            translated_map = json.load(f)
        print(f"[i] Loaded {len(translated_map)} translated sentences from {progress_file}.")
    except FileNotFoundError:
        print(f"[i] Progress file {progress_file} not found, translating from scratch.")
    except json.JSONDecodeError:
        print(f"[!] Progress file {progress_file} is malformed, translating from scratch.")

    lines_to_translate = [line for line in unique_lines if line not in translated_map]
    print(f"[i] {len(lines_to_translate)} unique lines remaining to be translated.")

    # Set target language for user prompt
    lang_name = "Simplified Chinese" if target_lang == "zh" else "English"

    for i in tqdm(range(0, len(lines_to_translate), batch_size), desc="GPT Batch Translating"):
        batch = lines_to_translate[i:i + batch_size]
        prompt = "\\n".join([f"[{j}] {text}" for j, text in enumerate(batch)])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate the following lines to {lang_name}. Return in format [0] translation:\\n\\n{prompt}"}
        ]
        
        retries = 0
        while retries < max_retries:
            try:
                model_name = os.getenv("OPENAI_MODEL_NAME", "gemini-2.0-flash")
                resp = client.chat.completions.create(model=model_name, messages=messages)
                content = resp.choices[0].message.content
                for line in content.splitlines():
                    if line.startswith("[") and "]" in line:
                        try:
                            idx = int(line[1:line.index("]")])
                            result = line[line.index("]")+1:].strip()
                            if 0 <= idx < len(batch):
                                original_text = batch[idx]
                                translated_map[original_text] = result
                                print(f"Original: {original_text}")
                                print(f"Translated: {result}")
                        except ValueError: # More specific exception for int conversion
                            print(f"[!] ValueError parsing index or result in line: {line}")
                            continue
                break # Success, exit retry loop
            except Exception as e:
                if "429" in str(e): # Check for rate limit error
                    retries += 1
                    print(f"[!] Rate limit hit for batch starting at index {i}. Retrying ({retries}/{max_retries}) in {retry_delay}s... Error: {e}")
                    import time
                    time.sleep(retry_delay)
                else:
                    print(f"[!] GPT API error at batch {i}: {e}")
                    # Save progress before breaking
                    with open(progress_file, "w", encoding="utf-8") as f:
                        json.dump(translated_map, f, ensure_ascii=False, indent=4)
                    print(f"[i] Translation progress saved to {progress_file}")
                    break # Non-rate-limit error, break and skip batch
        if retries == max_retries:
            print(f"[!] Max retries reached for batch starting at index {i}. Skipping this batch.")
            # Save progress before skipping
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(translated_map, f, ensure_ascii=False, indent=4)
            print(f"[i] Translation progress saved to {progress_file}")
        else:
            # Save progress after each successful batch
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(translated_map, f, ensure_ascii=False, indent=4)

    return translated_map

# === Apply translations back to subtitles ===
def assign_translations(subs, translated_map):
    for sub in subs:
        original = sub.content.strip()
        if original in translated_map:
            sub.content = translated_map[original]
        else:
            sub.content = "[Translation failed]" # Mark failed translations
    return subs

# === Main processing function ===
def translate_srt_file(input_path, output_path, target_lang="zh"):
    with open(input_path, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    unique_lines, _ = extract_unique_lines(subs)
    print(f"Total {len(subs)} subtitle lines, with {len(unique_lines)} unique sentences.")

    # Automatically detect if it's AV-style subtitles
    is_av_content = any(is_av_line(line) for line in unique_lines)
    
    # Select appropriate prompt based on content type and target language
    if is_av_content:
        if target_lang == "zh":
            system_prompt = AV_PROMPT_CH
            print("[🔞] Detected AV-style subtitles, using spicy Chinese translation prompt.")
        else:  # en
            system_prompt = AV_PROMPT_EN
            print("[🔞] Detected AV-style subtitles, using spicy English translation prompt.")
    else:
        if target_lang == "zh":
            system_prompt = GENERIC_PROMPT_ZH
            print("[ℹ️] Using generic Chinese translation prompt.")
        else:  # en
            system_prompt = GENERIC_PROMPT_EN
            print("[ℹ️] Using generic English translation prompt.")

    # Generate progress file name based on input file and target language
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    progress_file = f"translation_progress_{base_name}_{target_lang}.json"
    
    translated_map = translate_unique_lines(unique_lines, system_prompt, target_lang, progress_file=progress_file)

    translated_subs = assign_translations(subs, translated_map)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(translated_subs))

    print(f"✅ Translation complete, saved to {output_path}")

# === CLI ===
if __name__ == "__main__":
    import argparse
    import os # Add os import for path manipulation

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input SRT file path")
    parser.add_argument("-o", "--output", help="Output translated SRT file path (Optional, defaults to <input_filename>.zh.srt)") # Made output optional and updated help text
    parser.add_argument("-l", "--language", choices=["zh", "en"], default="zh", help="Target language for translation (default: zh)") # Added language option
    args = parser.parse_args()

    output_path = args.output
    if not output_path:
        base, ext = os.path.splitext(args.input)
        if ext.lower() == ".srt":
            # Use language code in the output filename
            output_path = base + f".{args.language}.srt"
        else:
            # If the input doesn't have .srt, just append .{lang}.srt
            output_path = args.input + f".{args.language}.srt" 
            print(f"[!] Warning: Input file '{args.input}' does not have .srt extension. Outputting to '{output_path}'.")


    translate_srt_file(args.input, output_path, args.language)

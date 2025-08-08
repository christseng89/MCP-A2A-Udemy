import os
import time
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

# ========= 基本設定 =========
BATCH_SIZE = 20
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")   # 需要可用的模型名稱
TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "120"))  # 秒
RETRIES = int(os.getenv("OPENAI_RETRIES", "3"))

INPUT_CSV = "Comparison.csv"
OUTPUT_CSV = "Comparison_Translated.csv"
SRC_COL = "Local Language"
DST_COL = "Translated_English"

# ========= 初始化 =========
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 未設定。請在 .env 或環境變數中加入。")

client = OpenAI(api_key=api_key, timeout=TIMEOUT)

# ========= 載入資料（支援斷點續跑）=========
if os.path.exists(OUTPUT_CSV):
    df = pd.read_csv(OUTPUT_CSV)
else:
    df = pd.read_csv(INPUT_CSV)

# 欄位檢查
if SRC_COL not in df.columns:
    raise KeyError(f"CSV 必須包含欄位 '{SRC_COL}'。目前欄位: {list(df.columns)}")

if DST_COL not in df.columns:
    df[DST_COL] = ""

# ========= 工具函式 =========
def _chunk_indices(n_rows, size):
    for start in range(0, n_rows, size):
        end = min(start + size, n_rows)
        yield start, end

def _build_batch_prompt(rows):
    """
    要求模型回傳「只輸出翻譯結果，每行一條，行數要與輸入相同」。
    使用「行號 + TAB + 翻譯」格式，便於精準解析。
    """
    numbered = []
    for i, text in enumerate(rows, start=1):
        text = "" if (pd.isna(text) or str(text).strip() == "") else str(text)
        numbered.append(f"{i}. {text}")
    user_content = "\n".join(numbered)

    system_msg = (
        "You are a professional translator with deep Trade Finance knowledge. "
        "Translate each line into English separately. "
        "Output ONLY the translations, one per line, with the SAME number of lines as input. "
        "For each line, respond in the format: '<index>\\t<English translation>'. "
        "Do not add extra text, explanations, or blank lines."
    )

    return system_msg, user_content

def translate_batch(texts, retries=RETRIES):
    """
    批次翻譯。回傳 list[str]，長度與 texts 相同。
    失敗時會重試，仍失敗則以占位字串返回。
    """
    system_msg, user_content = _build_batch_prompt(texts)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_content},
                ],
                # 若 SDK 支援，可保留；不支援也沒關係
                # response_format={"type": "text"},
                timeout=TIMEOUT,
            )
            content = resp.choices[0].message.content.strip()

            # 解析為 dict: index -> translation
            mapping = {}
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                # 期望格式: "<index>\t<translation>"
                if "\t" in line:
                    idx_str, trans = line.split("\t", 1)
                else:
                    # 有些模型可能回 "<index>. <translation>"，做個寬鬆解析
                    if ". " in line:
                        idx_str, trans = line.split(". ", 1)
                    elif "." in line:
                        idx_str, trans = line.split(".", 1)
                        trans = trans.lstrip()
                    else:
                        # 實在解析不了就當成整行翻譯，index 以遞增補
                        idx_str, trans = None, line

                try:
                    idx = int(idx_str) if idx_str is not None else None
                except Exception:
                    idx = None

                if idx is None:
                    # 放到下一個可用 index（很少見）
                    idx = len(mapping) + 1

                mapping[idx] = trans.strip()

            # 依原順序 1..N 組回陣列，缺漏用空字串補
            out = [mapping.get(i + 1, "") for i in range(len(texts))]
            # 確保長度相同
            if len(out) != len(texts):
                # 長度不符，視為錯誤重試
                raise ValueError(f"Parsed lines {len(out)} != input lines {len(texts)}")

            return out

        except Exception as e:
            last_err = e
            wait = 2 * attempt  # 簡單遞增 backoff
            print(f"⚠️ 批次翻譯失敗（第 {attempt}/{retries} 次）：{e}。{wait}s 後重試…")
            time.sleep(wait)

    # 全部重試失敗
    print(f"❌ 批次翻譯最終失敗：{last_err}")
    return ["[Translation failed]"] * len(texts)

# ========= 主流程 =========
total_rows = len(df)
print(df.columns)

# 只處理尚未翻譯的列
indices_to_process = [i for i in range(total_rows) if not isinstance(df.at[i, DST_COL], str) or df.at[i, DST_COL].strip() == ""]
pbar = tqdm(total=len(indices_to_process), desc="Translating", unit="row")

for start, end in _chunk_indices(total_rows, BATCH_SIZE):
    # 找出這個 batch 中尚未翻譯的 index
    batch_idx = [i for i in range(start, end) if i in indices_to_process]
    if not batch_idx:
        continue

    texts = [df.at[i, SRC_COL] for i in batch_idx]
    translations = translate_batch(texts, retries=RETRIES)

    # 寫回結果
    for i, t in zip(batch_idx, translations):
        df.at[i, DST_COL] = t

    # 即時存檔（斷點續跑）
    df.to_csv(OUTPUT_CSV, index=False)

    # 更新進度列
    pbar.update(len(batch_idx))

pbar.close()
print(f"✅ Translation completed! Saved to {OUTPUT_CSV}")

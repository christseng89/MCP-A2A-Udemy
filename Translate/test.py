import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Initialize OpenAI client

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0)

# Load CSV file
file_path = "Comparison.csv"
df = pd.read_csv(file_path)

print(df.columns)

# Ensure "Local Language" column exists
if "Local Language" not in df.columns:
    raise KeyError("The CSV file must have a column named 'Local Language'.")

# Prepare column for translations
if "Translated_English" not in df.columns:
    df["Translated_English"] = ""

# Translation function
def translate_to_english(text):
    if pd.isna(text) or text.strip() == "":
        return ""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional translator with superior Trade Finance knowledge. Translate the text to English."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

# Process translations in chunks of 50 rows
batch_size = 10
total_rows = len(df)

for start in tqdm(range(0, total_rows, batch_size), desc="Translating"):
    end = min(start + batch_size, total_rows)
    batch = df.iloc[start:end]

    for idx, row in batch.iterrows():
        if not df.at[idx, "Translated_English"]:  # Skip already translated rows
            df.at[idx, "Translated_English"] = translate_to_english(row["Local Language"])

    # Save intermediate results
    df.to_csv("Comparison_Translated.csv", index=False)

print("✅ Translation completed! Saved to Comparison_Translated.csv")
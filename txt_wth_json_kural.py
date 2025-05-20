import os
import asyncio
import pandas as pd
import edge_tts
import json

# === Settings ===
EXCEL_FILE = "Thirukkural_Extracted.xlsx"
OUTPUT_BASE = "new_audio"
VOICE = "ta-IN-ValluvarNeural"
RATE = "-70%"
PITCH = "-27Hz"
VOLUME = "+0%"

def clean_text(text):
    text = str(text)
    for ch in ["\u200c", "\u200b", "\n", "\r"]:
        text = text.replace(ch, " ")
    return text.strip()

def sanitize_folder_name(name):
    return clean_text(name).replace("/", "-").replace("\\", "-")

async def generate_tts_with_timestamps(filepath, text):
    # First, generate and save the audio using built-in save method
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME
    )
    await communicate.save(filepath)

    # Now re-stream to get word-level timestamps
    word_timestamps = []
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME
    )
    async for message in communicate.stream():
        if message["type"] == "WordBoundary":
            word_timestamps.append({
                "word": message["text"],
                "start_time": message["offset"] / 10**7  # 100-ns to seconds
            })

    return word_timestamps

def generate_json(kural_num, line1, line2, word_timestamps, folder_path):
    json_data = {
        "kural_number": int(kural_num),
        "line1": line1,
        "line2": line2,
        "word_timings": word_timestamps
    }

    json_path = os.path.join(folder_path, f"Kural_{int(kural_num):03d}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print(f"📄 JSON Saved: {json_path}")

async def main():
    df = pd.read_excel(EXCEL_FILE)

    for idx, row in df.iterrows():
        num = row.get("Kural Number") or row.get("kural no") or row.get("No")
        section = sanitize_folder_name(row.get("Section Name") or "Unknown_Section")
        unit = sanitize_folder_name(row.get("Unit Name") or "Unknown_Unit")
        chapter = sanitize_folder_name(row.get("Chapter Name") or "Unknown_Chapter")
        line1 = clean_text(row.get("Kural Line 1") or "")
        line2 = clean_text(row.get("Kural Line 2") or "")

        if pd.isna(num) or not line1 or not line2:
            print(f"⚠️ Skipping invalid entry at row {idx + 1}")
            continue

        combined_text = f"{line1}, {line2}"

        # Create the chapter folder path
        chapter_folder_path = os.path.join(OUTPUT_BASE, section, unit, chapter)
        # Create the kural subfolder inside chapter folder
        kural_folder = f"Kural_{int(num):03d}"
        folder_path = os.path.join(chapter_folder_path, kural_folder)
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{kural_folder}.mp3"
        output_path = os.path.join(folder_path, filename)

        print(f"🔊 Generating Kural {int(num)} → {output_path}")

        try:
            word_timestamps = await generate_tts_with_timestamps(output_path, combined_text)
            generate_json(num, line1, line2, word_timestamps, folder_path)
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"❌ Error generating Kural {num}: {e}")

if __name__ == "__main__":
    asyncio.run(main())

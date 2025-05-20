import json

# Load the enriched kural data with 'unit'
with open("thirukural_git_with_units.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Initialize final structure
structured = {
    "sections": []
}

section_map = {}

# Go through each kural and nest it under section → unit → chapter
for kural in data["kurals"]:
    section = kural["section"].strip()
    unit = kural["unit"].strip()
    chapter = kural["chapter"].strip()

    # Prepare kural entry
    kural_entry = {
        "number": kural["number"],
        "kural": kural["kural"],
        "meaning": kural["meaning"]
    }

    # Ensure section
    if section not in section_map:
        section_obj = {
            "name": section,
            "units": []
        }
        section_map[section] = section_obj
        structured["sections"].append(section_obj)

    # Ensure unit
    unit_map = {u["name"]: u for u in section_map[section]["units"]}
    if unit not in unit_map:
        unit_obj = {
            "name": unit,
            "chapters": []
        }
        unit_map[unit] = unit_obj
        section_map[section]["units"].append(unit_obj)

    # Ensure chapter
    chapter_map = {c["name"]: c for c in unit_map[unit]["chapters"]}
    if chapter not in chapter_map:
        chapter_obj = {
            "name": chapter,
            "kurals": []
        }
        chapter_map[chapter] = chapter_obj
        unit_map[unit]["chapters"].append(chapter_obj)

    # Add kural
    chapter_map[chapter]["kurals"].append(kural_entry)

# Save final structured JSON
with open("defined_nested_thirukkural.json", "w", encoding="utf-8") as f:
    json.dump(structured, f, ensure_ascii=False, indent=2)

print("✅ Saved full structured JSON to 'defined_nested_thirukkural.json'")

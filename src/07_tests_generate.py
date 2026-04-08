
import json
import re
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SPEC_PATH = "spec/spec_auto.md"
OUTPUT_PATH = "tests/tests_auto.json"

# Extract requirement IDs
with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec_text = f.read()

requirement_ids = re.findall(r"FR\d+", spec_text)

def generate_test(req_id):
    prompt = f"""
You must return ONLY valid JSON. No explanations, no extra text.

Generate ONE validation test for requirement {req_id}.

Return EXACTLY this format:

{{
  "test_id": "T1",
  "requirement_id": "{req_id}",
  "scenario": "Short description",
  "steps": ["Step 1", "Step 2"],
  "expected_result": "Expected outcome"
}}

Rules:
- Output MUST be valid JSON
- Use double quotes only
- No text before or after JSON
- Steps must be a list of strings
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()



import re

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

tests = []

for i, req_id in enumerate(requirement_ids):
    raw = generate_test(req_id)

    json_str = extract_json(raw)

    if json_str:
        try:
            test = json.loads(json_str)
            test["test_id"] = f"T_auto_{i+1}"
            test["requirement_id"] = req_id
            tests.append(test)
        except:
            print(f"Still invalid JSON for {req_id}")
            print("RAW OUTPUT:\n", raw)
    else:
        print(f"No JSON found for {req_id}")
        print("RAW OUTPUT:\n", raw)

# Save
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump({"tests": tests}, f, indent=2)

print(f"Tests saved to {OUTPUT_PATH}")
import json
import re
import os
from groq import Groq

#Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#File paths
SPEC_PATH = "spec/spec_auto.md"
OUTPUT_PATH = "tests/tests_auto.json"

#Read the spec_auto.md file
with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec_text = f.read()

#Extract all requirement IDs
requirement_ids = re.findall(r"FR\d+", spec_text)

#Function to extract the full requirement text for a given ID
def get_requirement_text(req_id):
    match = re.search(rf"(# Requirement ID: {req_id}[\s\S]*?)(?=# Requirement ID:|$)", spec_text)
    if match:
        return match.group(0).strip()
    return None

#Function to generate a test from Groq
def generate_test(req_id, requirement_text):
    prompt = f"""
You must return ONLY valid JSON. No explanations, no extra text.

Generate ONE validation test for the following requirement:

{requirement_text}

Rules:
- Output MUST be valid JSON
- Use double quotes only
- No text before or after JSON
- Steps must be realistic actions a user would take
- The expected result must match the requirement's acceptance criteria
- Return exactly this JSON format:

{{
  "test_id": "T1",
  "requirement_id": "{req_id}",
  "scenario": "Short description",
  "steps": ["Step 1", "Step 2"],
  "expected_result": "Expected outcome"
}}
"""
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

#Function to extract JSON from model output
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

#Generate tests
tests = []
for i, req_id in enumerate(requirement_ids):
    req_text = get_requirement_text(req_id)
    if not req_text:
        print(f"Requirement text not found for {req_id}")
        continue

    raw_output = generate_test(req_id, req_text)
    json_str = extract_json(raw_output)

    if json_str:
        try:
            test = json.loads(json_str)
            test["test_id"] = f"T_auto_{i+1}"  #Use auto numbering
            test["requirement_id"] = req_id     #Keep original FR ID
            tests.append(test)
        except json.JSONDecodeError:
            print(f"Invalid JSON for {req_id}")
            print("RAW OUTPUT:\n", raw_output)
    else:
        print(f"No JSON found for {req_id}")
        print("RAW OUTPUT:\n", raw_output)

#Save to JSON file
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump({"tests": tests}, f, indent=2)

print(f"Tests saved to {OUTPUT_PATH}")
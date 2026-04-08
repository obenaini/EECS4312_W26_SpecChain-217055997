import json
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
INPUT_PATH = "personas/personas_auto.json"
OUTPUT_PATH = "spec/spec_auto.md"

# Load personas
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    personas = json.load(f)["personas"]

def generate_requirements(persona):
    prompt = f"""
You are generating system requirements from a persona.

Persona:
{json.dumps(persona, indent=2)}

Generate 2 requirements.

Each requirement must include:
- Requirement ID (FRX)
- Description
- Source Persona
- Traceability (group ID)
- Acceptance Criteria (Given/When/Then format)

Format EXACTLY like:

# Requirement ID: FRX
- Description: ...
- Source Persona: ...
- Traceability: ...
- Acceptance Criteria: ...

Return only text.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# Generate spec
spec_text = ""

req_counter = 1

for persona in personas:
    text = generate_requirements(persona)

    # Fix IDs sequentially
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# Requirement ID:"):
            lines[i] = f"# Requirement ID: FR{req_counter}"
            req_counter += 1

    spec_text += "\n".join(lines) + "\n\n"

# Save
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(spec_text)

print(f"Specification saved to {OUTPUT_PATH}")
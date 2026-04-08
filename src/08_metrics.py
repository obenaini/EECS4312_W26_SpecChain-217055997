"""computes metrics: coverage/traceability/ambiguity/testability"""

import json
import re


GROUPS_PATH = "data/review_groups_hybrid.json"
PERSONAS_PATH = "personas/personas_hybrid.json"
SPEC_PATH = "spec/spec_hybrid.md"
TESTS_PATH = "tests/tests_hybrid.json"
DATASET_PATH = "data/reviews_clean.jsonl"
OUTPUT_PATH = "metrics/metrics_hybrid.json"


with open(GROUPS_PATH, "r", encoding="utf-8") as f:
    groups = json.load(f)["groups"]

with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
    personas = json.load(f)["personas"]

with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec_text = f.read()

with open(TESTS_PATH, "r", encoding="utf-8") as f:
    tests = json.load(f)["tests"]

# Count total reviews
total_reviews = sum(1 for _ in open(DATASET_PATH, "r", encoding="utf-8"))


# Personas to Groups
p_to_g = len(personas)

# Requirements to Personas
req_ids = re.findall(r"# Requirement ID: (FR\d+)", spec_text)
r_to_p = len(req_ids)

# Tests to Requirements
t_to_r = len(tests)

traceability_links = p_to_g + r_to_p + t_to_r


covered_reviews = set()

for group in groups:
    for rid in group["review_ids"]:
        covered_reviews.add(str(rid))

review_coverage_ratio = len(covered_reviews) / total_reviews

# Count requirements that mention a persona
req_blocks = spec_text.split("# Requirement ID:")
req_blocks = req_blocks[1:]  # remove first empty

traceable_reqs = 0

for block in req_blocks:
    if "Source Persona:" in block:
        traceable_reqs += 1

traceability_ratio = traceable_reqs / len(req_blocks)

tested_req_ids = set([t["requirement_id"] for t in tests])

testable_count = 0

for req_id in req_ids:
    if req_id in tested_req_ids:
        testable_count += 1

testability_rate = testable_count / len(req_ids)

ambiguous_keywords = [
    "fast", "easy", "better", "user-friendly",
    "quick", "intuitive", "simple", "efficient",
    "clear", "minimal", "seamless", "smooth"
]

ambiguous_count = 0

for block in req_blocks:
    text = block.lower()
    if any(word in text for word in ambiguous_keywords):
        ambiguous_count += 1

ambiguity_ratio = ambiguous_count / len(req_blocks)


metrics = {
    "traceability_links": traceability_links,
    "review_coverage_ratio": round(review_coverage_ratio, 4),
    "traceability_ratio": round(traceability_ratio, 4),
    "testability_rate": round(testability_rate, 4),
    "ambiguity_ratio": round(ambiguity_ratio, 4)
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("Metrics saved to", OUTPUT_PATH)

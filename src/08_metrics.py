"""Compute metrics for manual, automated, and hybrid pipelines"""

import json
import re
from pathlib import Path

# Define all pipelines and their paths
pipelines = {
    "manual": {
        "groups": "data/review_groups_manual.json",
        "personas": "personas/personas_manual.json",
        "spec": "spec/spec_manual.md",
        "tests": "tests/tests_manual.json",
        "dataset": "data/reviews_clean.jsonl",
        "output": "metrics/metrics_manual.json"
    },
    "automated": {
        "groups": "data/review_groups_auto.json",
        "personas": "personas/personas_auto.json",
        "spec": "spec/spec_auto.md",
        "tests": "tests/tests_auto.json",
        "dataset": "data/reviews_clean.jsonl",
        "output": "metrics/metrics_auto.json"
    },
    "hybrid": {
        "groups": "data/review_groups_hybrid.json",
        "personas": "personas/personas_hybrid.json",
        "spec": "spec/spec_hybrid.md",
        "tests": "tests/tests_hybrid.json",
        "dataset": "data/reviews_clean.jsonl",
        "output": "metrics/metrics_hybrid.json"
    }
}

def compute_metrics(groups_path, personas_path, spec_path, tests_path, dataset_path):
    # Load files
    with open(groups_path, "r", encoding="utf-8") as f:
        groups = json.load(f)["groups"]

    with open(personas_path, "r", encoding="utf-8") as f:
        personas = json.load(f)["personas"]

    with open(spec_path, "r", encoding="utf-8") as f:
        spec_text = f.read()

    with open(tests_path, "r", encoding="utf-8") as f:
        tests = json.load(f)["tests"]

    total_reviews = sum(1 for _ in open(dataset_path, "r", encoding="utf-8"))
    persona_count = len(personas)
    
    # Requirements
    req_ids = re.findall(r"# Requirement ID: (FR\d+)", spec_text)
    requirements_count = len(req_ids)
    
    # Tests
    tests_count = len(tests)
    
    # Traceability links 
    traceability_links = persona_count + requirements_count + tests_count
    
    # Review coverage
    covered_reviews = set()
    for group in groups:
        for rid in group["review_ids"]:
            covered_reviews.add(str(rid))
    review_coverage = len(covered_reviews) / total_reviews if total_reviews > 0 else 0
    
    # Traceability ratio
    req_blocks = spec_text.split("# Requirement ID:")[1:]
    traceable_reqs = sum(1 for block in req_blocks if "Source Persona:" in block)
    traceability_ratio = traceable_reqs / len(req_blocks) if req_blocks else 0
    
    # Testability rate
    tested_req_ids = set([t["requirement_id"] for t in tests])
    testable_count = sum(1 for rid in req_ids if rid in tested_req_ids)
    testability_rate = testable_count / len(req_ids) if req_ids else 0
    
    # Ambiguity ratio
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
    ambiguity_ratio = ambiguous_count / len(req_blocks) if req_blocks else 0
    
    metrics = {
        "dataset_size": total_reviews,
        "persona_count": persona_count,
        "requirements_count": requirements_count,
        "tests_count": tests_count,
        "traceability_links": traceability_links,
        "review_coverage": round(review_coverage, 4),
        "traceability_ratio": round(traceability_ratio, 4),
        "testability_rate": round(testability_rate, 4),
        "ambiguity_ratio": round(ambiguity_ratio, 4)
    }
    
    return metrics

summary_metrics = {}

# Compute metrics for all pipelines
for name, paths in pipelines.items():
    metrics = compute_metrics(
        paths["groups"], paths["personas"], paths["spec"], paths["tests"], paths["dataset"]
    )
    summary_metrics[name] = metrics
    
    # Save individual metrics file
    Path(paths["output"]).parent.mkdir(parents=True, exist_ok=True)
    with open(paths["output"], "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics for {name} pipeline to {paths['output']}")

# Save summary metrics file
with open("metrics/metrics_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary_metrics, f, indent=2)
print("Saved metrics summary to metrics/metrics_summary.json")
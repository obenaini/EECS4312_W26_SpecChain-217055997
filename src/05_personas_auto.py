import json
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np
from groq import Groq
import random
import os

INPUT_PATH = "data/reviews_clean.jsonl"
OUTPUT_PATH = "data/review_groups_auto.json"
NUM_GROUPS = 5
SAMPLE_PER_CLUSTER = 10  # reviews sent to LLM


embed_model = SentenceTransformer('all-MiniLM-L6-v2')

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


reviews = []
review_ids = []

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        reviews.append(obj["review"])
        review_ids.append(obj["ID"])


embeddings = embed_model.encode(reviews, show_progress_bar=True)


kmeans = KMeans(n_clusters=NUM_GROUPS, random_state=42, n_init=10)
labels = kmeans.fit_predict(embeddings)

clusters = {i: [] for i in range(NUM_GROUPS)}

for idx, label in enumerate(labels):
    clusters[label].append({
        "id": review_ids[idx],
        "text": reviews[idx]
    })


def generate_theme(sample_reviews):
    prompt = f"""
    You are analyzing user reviews for a meditation app.

    Reviews:
    {chr(10).join(sample_reviews)}

    Task:
    1. Identify the SINGLE most common, SPECIFIC issue or complaint.
    2. Ignore generic topics like "meditation", "stress", or "mental health".
    3. Focus on concrete problems (e.g., crashes, subscription cost, UI issues).
    4. Write a short theme (max 8 words).

    Good examples:
    - "Frequent app crashes during sessions"
    - "Subscription cost and billing issues"
    - "Slow performance and laggy interface"

    Bad examples:
    - "Users struggle with meditation"
    - "General dissatisfaction"

    Return ONLY the theme.
    """
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


output = {"groups": []}

for i in range(NUM_GROUPS):
    cluster_reviews = clusters[i]

    #Sample reviews for theme generation
    #Get cluster center
    center = kmeans.cluster_centers_[i]

    #Compute distance to center
    distances = np.linalg.norm(embeddings - center, axis=1)

    #Get indices belonging to this cluster
    cluster_indices = [idx for idx, label in enumerate(labels) if label == i]

    #Sort by closeness to center
    cluster_indices = sorted(cluster_indices, key=lambda x: distances[x])

    #Take top N most representative
    sample_indices = cluster_indices[:SAMPLE_PER_CLUSTER]

    sample_texts = [reviews[idx] for idx in sample_indices]

    theme = generate_theme(sample_texts)

    group = {
        "group_id": f"G{i+1}",
        "theme": theme,
        "review_ids": [r["id"] for r in cluster_reviews[:10]],  # limit for readability
        "example_reviews": [r["text"] for r in cluster_reviews[:10]]
    }

    output["groups"].append(group)


PERSONA_OUTPUT_PATH = "personas/personas_auto.json"

def generate_persona(group):
    prompt = f"""
You must return ONLY valid JSON. No explanations, no extra text.

Create a persona from these app reviews.

Theme:
{group["theme"]}

Reviews:
{chr(10).join(group["example_reviews"])}

Return EXACTLY this JSON format:

{{
  "id": "P1",
  "name": "...",
  "description": "...",
  "derived_from_group": "{group["group_id"]}",
  "goals": ["...", "..."],
  "pain_points": ["...", "..."],
  "context": ["...", "..."],
  "constraints": ["...", "..."],
  "evidence_reviews": ["...", "...", "..."]
}}

Rules:
- Output MUST be valid JSON
- No text before or after JSON
- Use double quotes only
"""
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

personas = []
import re

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

for i, group in enumerate(output["groups"]):
    raw = generate_persona(group)

    json_str = extract_json(raw)

    if json_str:
        try:
            persona = json.loads(json_str)
            persona["id"] = f"P{i+1}"
            persona["derived_from_group"] = group["group_id"]
            personas.append(persona)
        except:
            print(f"Still invalid JSON for {group['group_id']}")
    else:
        print(f"No JSON found for {group['group_id']}")

# Save personas
with open(PERSONA_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump({"personas": personas}, f, indent=2)

print(f"Personas saved to {PERSONA_OUTPUT_PATH}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Saved to {OUTPUT_PATH}")
import json
from openai import OpenAI
from .utils import normalize_weights, clamp

client = OpenAI()  # env var automatically loads API key


# ------------------ 1. Compute Strengths ------------------
def compute_strengths(category_means, default_overall):
    strengths_prompt = f"""
You are given a student's historical Canvas performance by category (percent 0-100), possibly with nulls:

{json.dumps(category_means, indent=2)}

Return pure JSON with:
- "category_strengths": object with keys "projects","assignments","exams","participation" (0-100 floats).
- "overall_strength": float 0-100 (average of the four categories).
- "punctual_strength": float 0-100 (use 100 because lateness already baked in historically).

Rules:
- If any category is null, replace with this fallback overall: {default_overall:.2f}
- Ensure ALL four categories exist.
- Do NOT include any extra fields or prose. JSON only.
"""

    try:
        stage = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": strengths_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(stage.choices[0].message.content)

    except Exception as e:
        cs = {
            k: (category_means[k] if category_means[k] is not None else default_overall)
            for k in ["projects", "assignments", "exams", "participation"]
        }
        return {
            "category_strengths": cs,
            "overall_strength": float(sum(cs.values()) / 4.0),
            "punctual_strength": 100.0,
            "_note": f"AI strengths fallback due to: {e}",
        }


# ------------------ 2. Compute Prediction ------------------
def compute_prediction(strengths, syllabus_text, rmp_pack):
    prediction_prompt = """
Use the provided data to produce a JSON object with:
- "projects","assignments","exams","participation": syllabus weights as percentages (floats), each 0–100, sum ≈ 100.
- "final_score": number (0–100)
- "margin_of_error": number (e.g., 3,4,6)
- "range": [low, high] (floats, clamped 0–100)

Inputs:
1) strengths: student's category_strengths (0–100), overall_strength, punctual_strength.
2) syllabus: free text that may mention grading breakdowns.
3) rmp: { "avg_difficulty": 0–5 or null, "would_take_again_percent": 0–100 or null }.

Method:
- Parse syllabus text to infer weights. If unclear, use defaults: projects=25, assignments=35, exams=35, participation=5.
- Normalize weights to sum to 100.
- Base score = sum(strength[cat] * weight[cat]/100 for each category).
- Difficulty drag: if rmp.avg_difficulty:
    4.0–5.0  => -3
    3.3–3.99 => -2
    2.7–3.29 => -1
    else     => 0
- Punctual bonus: if punctual_strength > 90 => +2, else +0.
- Extra credit: if syllabus text explicitly mentions "extra credit" => +3.
- Margin of error:
    if rmp.would_take_again_percent is null => 5
    elif <30 => 6
    elif 30–100 => 4
    else => 3
- Clamp final_score to 0–100; range = [final_score - margin, final_score + margin] clamped to 0–100.

Return JSON only.
"""
    ai_inputs = {
        "strengths": strengths,
        "rmp": rmp_pack,
        "syllabus": syllabus_text,
    }

    try:
        stage2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prediction_prompt},
                {"role": "user", "content": json.dumps(ai_inputs, indent=2)},
            ],
            response_format={"type": "json_object"},
        )
        final = json.loads(stage2.choices[0].message.content)

    except Exception as e:
        defaults = {"projects": 25.0, "assignments": 35.0, "exams": 35.0, "participation": 5.0}
        cs = strengths.get("category_strengths", {})
        base = sum(float(cs.get(k, 85.0)) * (defaults[k] / 100.0) for k in defaults)
        margin = 5.0
        final = {
            **defaults,
            "final_score": clamp(base),
            "margin_of_error": margin,
            "range": [clamp(base - margin), clamp(base + margin)],
            "_note": f"prediction fallback due to: {e}",
        }

    # Normalize weights exactly as original
    weights = {}
    for k in ["projects", "assignments", "exams", "participation"]:
        try:
            weights[k] = float(final.get(k)) if final.get(k) is not None else None
        except Exception:
            weights[k] = None

    if any(v is None for v in weights.values()):
        weights = {"projects": 25.0, "assignments": 35.0, "exams": 35.0, "participation": 5.0}

    weights = normalize_weights(weights)

    final["projects"] = round(weights["projects"], 2)
    final["assignments"] = round(weights["assignments"], 2)
    final["exams"] = round(weights["exams"], 2)
    final["participation"] = round(weights["participation"], 2)

    return final


# ------------------ 3. Compute Advice ------------------
def compute_advice(final, strengths, course_name, rmp_pack):
    advice_prompt = f"""
A student is considering "{course_name}".
Predicted grade: {final.get("final_score")} ±{final.get("margin_of_error")}.
Strengths: {json.dumps(strengths.get("category_strengths"), indent=2)}.
Syllabus weights: {{
  projects: {final.get("projects")},
  assignments: {final.get("assignments")},
  exams: {final.get("exams")},
  participation: {final.get("participation")}
}}
Professor info: {rmp_pack}.

Write advice in 3 sections. Each section must be 5–6 sentences minimum:

Areas You Will Do Well At:
...

Areas You May Struggle With:
...

Final Verdict:
...
Do NOT use markdown. No bullet points. Plain text only.
"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": advice_prompt}],
            max_tokens=600,
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"(Advice unavailable due to error: {e})"

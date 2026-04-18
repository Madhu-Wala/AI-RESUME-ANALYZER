from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# score computing function
def compute_score(resume_text, jd_text, resume_skills, jd_skills):

    # ===== 1. Skill Score =====
    must_have = jd_skills[:len(jd_skills)//2]
    good_to_have = jd_skills[len(jd_skills)//2:]

    must_score = len(set(resume_skills) & set(must_have)) / max(len(must_have), 1)
    good_score = len(set(resume_skills) & set(good_to_have)) / max(len(good_to_have), 1)

    skill_score = (0.7 * must_score) + (0.3 * good_score)

    # ===== 2. Semantic Score =====
    jd_chunks = jd_text.split(".")
    jd_embeddings = model.encode(jd_chunks)

    resume_emb = model.encode(resume_text)

    scores = [float(util.cos_sim(resume_emb, jd_emb)) for jd_emb in jd_embeddings]
    semantic_score = sum(sorted(scores, reverse=True)[:3]) / max(len(scores[:3]), 1)

    # ===== 3. Experience Score =====
    import re
    def extract_exp(text):
        matches = re.findall(r'(\d+)\+?\s*(years|yrs)', text.lower())
        return max([int(m[0]) for m in matches], default=0)

    jd_exp = extract_exp(jd_text)
    res_exp = extract_exp(resume_text)

    exp_score = 1 if jd_exp == 0 else min(res_exp / jd_exp, 1)

    # ===== 4. Keyword Score =====
    jd_words = jd_text.lower().split()
    resume_words = resume_text.lower().split()

    match_count = sum(1 for w in jd_words if w in resume_words)
    keyword_score = match_count / max(len(jd_words), 1)

    # ===== 5. Penalty =====
    missing = list(set(jd_skills) - set(resume_skills))
    penalty = len(missing) / max(len(jd_skills), 1)

    # ===== FINAL SCORE =====
    final_score = (
        0.30 * skill_score +
        0.25 * semantic_score +
        0.20 * exp_score +
        0.15 * keyword_score -
        0.10 * penalty
    )

    return round(final_score * 100, 2)
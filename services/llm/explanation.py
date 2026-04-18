from .llm_client import ask_llm

def generate_explanation(resume_text, jd_text, score):
    prompt = f"""
    You are an AI recruiter.

    Job Description:
    {jd_text}

    Candidate Resume:
    {resume_text}

    Score: {score}

    Give output in this format:
    1. Strengths
    2. Weaknesses
    3. Missing Skills
    4. Final Decision (Hire / Maybe / Reject with reason)
    """
    return ask_llm(prompt)
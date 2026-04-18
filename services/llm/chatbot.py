from .llm_client import ask_llm

def ask_candidate_question(resume_text, jd_text, score, question):
    prompt = f"""
        JD:
        {jd_text}

        Resume:
        {resume_text}

        Score: {score}

        Question:
        {question}
        """
    return ask_llm(prompt)
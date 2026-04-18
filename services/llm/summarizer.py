from .llm_client import ask_llm

def summarize_resume(resume_text):
    prompt = f"Summarize this resume in 5 bullet points:\n{resume_text}"
    return ask_llm(prompt)
SKILLS = [
    "python", "java", "sql", "machine learning",
    "nlp", "react", "node", "data analysis",
    "mern","django","flask","aws","azure","gcp", 
    "docker", "kubernetes", "git", "linux", "c++", 
    "c#", "ruby", "php", "swift", "go", "typescript", 
    "angular", "vue", "spring", "hibernate", "tensorflow", 
    "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", 
    "seaborn", "power bi", "tableau", "excel", "spark", 
    "hadoop", "kafka", "redis", "mongodb", "postgresql", 
    "mysql", "oracle", "sql server"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return list(set(found))
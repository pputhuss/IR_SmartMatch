from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def rank_companies(resume_text, companies):
    resume_embedding = model.encode([resume_text])
    results = []

    for company in companies:
        comp_embedding = model.encode([company["description"]])
        score = cosine_similarity(resume_embedding, comp_embedding)[0][0]
        results.append((company["company"], float(score)))

    return sorted(results, key=lambda x: x[1], reverse=True)
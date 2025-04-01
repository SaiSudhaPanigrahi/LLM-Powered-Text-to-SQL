from sentence_transformers import util

def is_question_relevant_to_schema(question, schema_text, model, threshold=0.35):
    question_embedding = model.encode(question, convert_to_tensor=True)

    schema_lines = schema_text.lower().splitlines()
    schema_parts = [line.strip() for line in schema_lines if line.strip()]
    schema_embeddings = model.encode(schema_parts, convert_to_tensor=True)

    similarity = util.cos_sim(question_embedding, schema_embeddings)
    max_score = similarity.max().item()

    print(f"🔍 Max schema similarity score: {max_score:.3f}")
    return max_score >= threshold
import os
import json
from models.schema_matcher import SchemaMatcher
from models.generator_llm import SQLGenerator

matcher = SchemaMatcher("data/spider/tables.json")
generator = SQLGenerator()

def normalize_sql(sql):
    import re
    return re.sub(r"\s+", "", sql.strip().lower())

def process_natural_language_question(question: str):
    print(f"\n💬 User Question: {question}")

    # Match schema
    db_id, schema_text = matcher.match(question)
    print(f"✅ Matched DB ID: {db_id}")
    print(f"📦 Matched Schema:\n{schema_text}")

    # Generate SQL
    print("🧾 Generating SQL...")
    predicted_sql = generator.generate(question, schema_text)
    print(f"✅ Predicted SQL:\n{predicted_sql}")

    return {
        "question": question,
        "db_id": db_id,
        "schema": schema_text,
        "predicted_sql": predicted_sql
    }

if __name__ == "__main__":
    print("\n🧠 Ask your question below (Ctrl+C to exit):")
    try:
        while True:
            user_input = input("\n>> ")
            result = process_natural_language_question(user_input)

    except KeyboardInterrupt:
        print("\n👋 Exiting. Goodbye!")

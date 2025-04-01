import os
import json
import sqlparse
from models.schema_matcher import SchemaMatcher
from models.generator_llm import SQLGenerator
from utils.validation import is_question_relevant_to_schema

matcher = SchemaMatcher("data/spider/tables.json")
generator = SQLGenerator()

def normalize_sql(sql):
    import re
    return re.sub(r"\s+", "", sql.strip().lower())

def is_valid_sql(sql: str) -> bool:
    try:
        parsed = sqlparse.parse(sql)
        return bool(parsed and parsed[0].tokens)
    except Exception as e:
        print(f"❌ SQL Parsing Failed: {e}")
        return False

def process_natural_language_question(question: str):
    print(f"\n💬 User Question: {question}")

    # Match schema
    db_id, schema_text = matcher.match(question)
    print(f"✅ Matched DB ID: {db_id}")
    print(f"📦 Matched Schema:\n{schema_text}")

    if not is_question_relevant_to_schema(question, schema_text, matcher.get_model()):
        print("❌ Question is not relevant to the matched database schema.")
        return {
            "question": question,
            "db_id": db_id,
            "schema": schema_text,
            "predicted_sql": None,
            "error": "Question is not relevant to the schema."
        }

    # Generate SQL
    print("🧾 Generating SQL...")
    predicted_sql = generator.generate(question, schema_text)
    if is_valid_sql(predicted_sql):
        print("✅ SQL Syntax: Valid")
        print(f"✅ Predicted SQL:\n{predicted_sql}")
    else:
        print("❌ SQL Syntax: Invalid")
        return {
            "question": question,
            "db_id": db_id,
            "schema": schema_text,
            "predicted_sql": None,
            "error": "Generated SQL is invalid. Please try rephrasing your question."
        }
    

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

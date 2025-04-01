import os
import json
import sqlparse
from models.schema_matcher import SchemaMatcher
from models.generator_llm import SQLGenerator
from utils.validation import is_question_relevant_to_schema
from utils.fine_grained_schema import get_fine_grained_schema
from utils.prompt_formatter import format_schema_prompt
from utils.schema_parser import load_parsed_schema
from utils.sql_postchecker import validate_sql_against_schema

matcher = SchemaMatcher("data/spider/tables.json")
generator = SQLGenerator()
parsed_schemas = load_parsed_schema("data/spider/tables.json")

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
    db_schemas = load_parsed_schema("data/spider/tables.json")
    print(f"\n💬 User Question: {question}")

    # Match schema
    db_id, _ = matcher.match(question)
    print(f"✅ Matched DB ID: {db_id}")

    schema_obj = parsed_schemas.get(db_id)

    # schema_info = db_schemas[db_id] 
    # schema_text = format_schema_prompt(schema_info)  

    schema_text = get_fine_grained_schema(matcher.schema_by_id[db_id])
    print(f"📦 Matched Schema:\n{schema_text}")

    print(f"📦 Fine-Grained Schema:{schema_text}")


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
    
    if not validate_sql_against_schema(predicted_sql, schema_obj):
        print("❌ SQL uses invalid table or column names.")
        return {
            "question": question,
            "db_id": db_id,
            "schema": schema_text,
            "predicted_sql": None,
            "error": "Generated SQL uses invalid table or column names."
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

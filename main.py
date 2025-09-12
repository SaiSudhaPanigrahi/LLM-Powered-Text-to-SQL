# main_api.py

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from models.schema_matcher import SchemaMatcher
from models.generator_llm import SQLGenerator
from utils.validation import is_question_relevant_to_schema
from utils.fine_grained_schema import get_fine_grained_schema
from utils.schema_parser import load_parsed_schema
from utils.sql_postchecker import validate_sql_against_schema
from fastapi.middleware.cors import CORSMiddleware
from utils_text2sql import generate_sql
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List
import sqlparse
import sqlite3
import torch

app = FastAPI()
DB_PATH = "/Users/vatsalvatsyayan/Class/NLP/database/allInOne/final.sqlite"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

matcher = SchemaMatcher("data/spider/tables.json")
generator = SQLGenerator()
parsed_schemas = load_parsed_schema("data/spider/tables.json")

class QuestionInput(BaseModel):
    question: str

class ConfirmInput(BaseModel):
    question: str
    db_id: str

class QuestionOnlyRequest(BaseModel):
    question: str

class QueryRequest(BaseModel):
    query: str


def is_valid_sql(sql: str) -> bool:
    try:
        parsed = sqlparse.parse(sql)
        return bool(parsed and parsed[0].tokens)
    except:
        return False

@app.post("/match_schema/")
def match_schema(input: QuestionInput):
    question = input.question
    db_id, _ = matcher.match(question)
    schema_obj = parsed_schemas.get(db_id)
    schema_text = get_fine_grained_schema(matcher.schema_by_id[db_id])

    if not is_question_relevant_to_schema(question, schema_text, matcher.get_model()):
        return {
            "db_id": db_id,
            "schema": schema_text,
            "relevant": False,
            "message": "Question is not relevant to the matched database schema."
        }

    return {
        "db_id": db_id,
        "schema": schema_text,
        "relevant": True
    }

@app.post("/generate-sql/")
async def generate_sql_from_question(request: QuestionOnlyRequest):
    question = request.question

    db_id, _ = matcher.match(question)
    schema_obj = parsed_schemas[db_id]

    schema_prompt = get_relevant_schema_prompt(request.question, schema_obj, matcher.get_model())

    print(f"schema prompt: {schema_prompt}")

    sql = generator.generate(question=question, schema=schema_prompt)

    return {
        "question": request.question,
        "sql": sql.strip()
    }


@app.post("/execute-query")
def execute_query(request: QueryRequest):


    print(request)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(request.query)
        
        if request.query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return {"results": results}
        else:
            conn.commit()
            return {"message": "Query executed successfully."}
    except sqlite3.Error as e:
        print("Error Message:", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


model = SentenceTransformer("all-MiniLM-L6-v2")

def get_relevant_schema_prompt(question: str, schema_obj: dict, model: SentenceTransformer) -> str:
    
    table_names = schema_obj["tables"]
    table_columns = schema_obj["table_columns"]

    table_texts = [
        f"{table}: {', '.join(cols)}" for table, cols in table_columns.items()
    ]

    question_embedding = model.encode(question, convert_to_tensor=True)
    table_embeddings = model.encode(table_texts, convert_to_tensor=True)
    scores = util.cos_sim(question_embedding, table_embeddings)[0]

    top_idx = scores.argmax().item()
    top_table = table_names[top_idx]
    top_cols = table_columns[top_table]
    col_str = ", ".join([f"<col>{col}</col>" for col in top_cols])

    return f"<tab>{top_table}</tab>({col_str})"

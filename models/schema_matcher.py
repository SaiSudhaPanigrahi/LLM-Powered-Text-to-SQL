# 

from sentence_transformers import SentenceTransformer, util
import json

class SchemaMatcher:
    def __init__(self, tables_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        with open(tables_path, "r") as f:
            self.schemas = json.load(f)

        # Preprocess schemas: create full descriptions and precompute embeddings
        self.db_texts = []
        self.db_ids = []
        self.schema_by_id = {}
        for schema in self.schemas:
            db_id = schema["db_id"]
            schema_text = self._format_schema(schema)
            self.db_texts.append(schema_text)
            self.db_ids.append(db_id)
            self.schema_by_id[db_id] = schema

        self.db_embeddings = self.model.encode(self.db_texts, convert_to_tensor=True)

    def _format_schema(self, schema_obj):
        lines = []
        for i, table in enumerate(schema_obj['table_names_original']):
            columns = [
                col[1] for col in schema_obj['column_names_original']
                if col[0] == i and col[1] != "*"
            ]
            if columns:
                lines.append(f"Table {table}: {', '.join(columns)}")
        return "\n".join(lines)

    def match(self, question):
        question_embedding = self.model.encode(question, convert_to_tensor=True)
        scores = util.cos_sim(question_embedding, self.db_embeddings)[0]
        best_idx = scores.argmax().item()
        best_db_id = self.db_ids[best_idx]
        best_schema_text = self.db_texts[best_idx]
        return best_db_id, best_schema_text
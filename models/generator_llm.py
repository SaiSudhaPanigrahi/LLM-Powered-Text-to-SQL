# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# class SQLGenerator:
#     def __init__(self):
#         self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
#         self.model = AutoModelForCausalLM.from_pretrained(
#             "microsoft/phi-1_5",
#             device_map={"": "cpu"}
#         )
#         self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

#     def generate(self, question, validated_schema_json):
#         prompt = f"""
#         You are a SQL expert. Given the database schema and a question, write a valid SQL query using only the relevant tables and columns.

#         Schema:
#         {validated_schema_json}

#         Question:
#         {question}

#         SQL Query:
#         """.strip()


#         output = self.pipe(prompt, max_new_tokens=256)[0]['generated_text']
#         return output.split(prompt)[-1].strip()

import os
import re
import logging
from llama_cpp import Llama

class SQLGenerator:
    def __init__(self):
        """Initialize with local GGUF model"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "sqlcoder-7b.Q4_K_M.gguf")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")
        
        # def safe_del(self):
        #     try:
        #         if hasattr(self, "_ctx") and self._ctx:
        #             self.close()
        #     except Exception:
        #         pass

        # Llama.__del__ = safe_del

        self.model = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_gpu_layers=1,
            n_threads=6,
            verbose=False
        )

        logging.info(f"✅ Loaded model from: {self.model_path}")

    

    def generate(self, question: str, schema: str) -> str:
        try:
            prompt = f"""### Postgres SQL tables, with their properties:
{schema}

### Question:
{question}

### SQL query (no aliases, no extra formatting, lowercase only):
select """

            output = self.model(
                prompt=prompt,
                max_tokens=300,
                temperature=0.1,
                stop=["\n\n", ";"]
            )

            raw_output = output["choices"][0]["text"]
            logging.debug(f"📤 Raw output: {raw_output}")
            return self._clean_output(raw_output)

        except Exception as e:
            logging.error(f"Generation failed: {str(e)}")
            raise

    def _clean_output(self, raw_text: str) -> str:
        try:
            sql = "select " + raw_text.lower().split("select", 1)[-1].split(";")[0].strip()
            sql = sql.replace("  ", " ").replace(" ;", ";")
            # Remove aliases like "as something"
            sql = re.sub(r"\s+as\s+\w+", "", sql)
            return sql + ";"
        except Exception:
            return raw_text.strip() + ";"

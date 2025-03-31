# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# class SchemaValidator:
#     def __init__(self):
#         self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
#         self.model = AutoModelForCausalLM.from_pretrained(
#             "microsoft/phi-1_5",
#             device_map={"": "cpu"}
#         )
#         self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

#     def validate(self, question, schema_text):
#         prompt = f"Schema: {schema_text}\nQuestion: '{question}'\nWhat tables and columns are needed? Provide JSON."
#         output = self.pipe(prompt, max_new_tokens=128)[0]['generated_text']
#         return output.split(prompt)[-1].strip()


from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class SchemaValidator:
    def __init__(self):
        print("🧠 Loading validator LLM (microsoft/phi-1_5)...")

        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-1_5",
            device_map="auto"
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def validate(self, question, schema_text):
        prompt = f"""You are a helpful assistant.

Given a database schema and a question, return a JSON listing only the relevant tables and columns needed to answer the question.

Schema:
{schema_text}

Question:
{question}

Output JSON only:
{{ "table_name": ["column1", "column2"] }}
"""

        output = self.pipe(prompt, max_new_tokens=128)[0]['generated_text'].strip()

        try:
            json_start = output.index('{')
            json_end = output.rindex('}') + 1
            json_like = output[json_start:json_end]
        except ValueError:
            json_like = output.strip()

        return json_like
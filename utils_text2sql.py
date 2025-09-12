import os
import re
import torch
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration
from torch.serialization import safe_globals

# Calculate absolute paths relative to this file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tokenizer_path = os.path.join(BASE_DIR, "text2sql_model", "text2sql_tokenizer")
model_path = os.path.join(BASE_DIR, "text2sql_model", "text2sql_full_model.pt")

# Debug prints to verify paths and file existence.
print("Current working directory:", os.getcwd())
print("Tokenizer path:", tokenizer_path)
print("Model path:", model_path)
print("Contents of tokenizer directory:", os.listdir(tokenizer_path))
print("Contents of model directory:", os.listdir(os.path.join(BASE_DIR, "text2sql_model")))
assert os.path.exists(model_path), "Model file not found!"

# 1. Load the T5 tokenizer from the tokenizer directory.
tokenizer = T5Tokenizer.from_pretrained(tokenizer_path, local_files_only=True)

# 2. Load the configuration from the tokenizer directory.
config = T5Config.from_pretrained(tokenizer_path, local_files_only=True)

# 3. Load the full model checkpoint (saved via torch.save(model, ...)).
with safe_globals({"transformers.models.t5.modeling_t5.T5ForConditionalGeneration": T5ForConditionalGeneration}):
    model = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
model.eval()

# Generation configuration parameters.
MAX_INPUT_LEN = 256
MAX_OUTPUT_LEN = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(DEVICE)

def build_input_prompt(schema: str, question: str) -> str:
    """
    Build a prompt that instructs the model to generate plain SQL without any markup tokens.
    """
    return (
        "Given the following database schema:\n"
        f"{schema.strip()}\n\n"
        "Generate a valid SQL query (output only standard SQL without any markup tags) that answers the following question:\n"
        f"Question: {question.strip()}\n\n"
        "SQL Query:"
    )

def clean_generated_sql(raw_sql: str) -> str:
    """
    Remove any leftover markup tokens and stray markers.
    This updated version explicitly removes tokens like 'tab>' and 'col>',
    while preserving genuine comparison operators.
    """
    # Remove complete markup tags.
    cleaned = re.sub(r"</?tab>", "", raw_sql)
    cleaned = re.sub(r"</?col>", "", cleaned)
    # Additionally, remove any stray occurrences of "tab>" and "col>".
    cleaned = re.sub(r"(tab>|col>)", "", cleaned)
    
    # Remove excessive spaces.
    cleaned = " ".join(cleaned.split())
    
    # (Optional) Enforce SQL keywords to be uppercase.
    keywords = ["select", "from", "join", "on", "where", "and", "or", "as"]
    for kw in keywords:
        cleaned = re.sub(r"\b" + kw + r"\b", kw.upper(), cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def generate_sql(schema: str, question: str) -> str:
    prompt = build_input_prompt(schema, question)
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_INPUT_LEN
    )
    # Move inputs to the proper device.
    inputs = {key: tensor.to(DEVICE) for key, tensor in inputs.items()}
    outputs = model.generate(
        **inputs,
        num_beams=5,
        max_length=MAX_OUTPUT_LEN,
        early_stopping=True
    )
    raw_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    cleaned_sql = clean_generated_sql(raw_sql)
    return cleaned_sql

# Example usage for testing.
if __name__ == '__main__':
    schema = (
        "<tab>singer</tab>(<col>singer_id</col>, <col>name</col>, <col>age</col>)\n"
        "<tab>album</tab>(<col>album_id</col>, <col>title</col>, <col>release_year</col>, <col>singer_id</col>)"
    )
    question = "List the names of singers who released an album after 2010."
    generated_sql = generate_sql(schema, question)
    print("Generated SQL:", generated_sql)
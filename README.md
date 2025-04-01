1. Download Spider dataset in a folder called data

git clone https://github.com/taoyds/spider.git data

2. Download sqlcoder model (make sure it is in models folder)

wget -O models/sqlcoder-7b.Q4_K_M.gguf https://huggingface.co/defog/sqlcoder-7b-GGUF/resolve/main/sqlcoder-7b.Q4_K_M.gguf

3. Create a venv and install required packages 

python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

4. Run main.py

python3 main.py


-----------------------------------------------

What we currently have:

	•	Schema matcher using sentence-transformers
 	•	Fine-Grained Schema Parsing
  	•	Prompt Formatting
	•	SQL generation via SQLCoder-7B (GGUF, local inference)
	•	SQL syntax validation
	•	Schema relevance check via embedding similarity
 	•	Column/Table Validation
	•	Query formatting and evaluation against Spider

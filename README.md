1. Download Spider dataset in a folder called data

git clone https://github.com/taoyds/spider.git data

2. Download sqlcoder model

mkdir -p models
wget -O models/sqlcoder-7b.Q4_K_M.gguf https://huggingface.co/defog/sqlcoder-7b-GGUF/resolve/main/sqlcoder-7b.Q4_K_M.gguf

3. Create a venv and install required packages 

python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

4. Run main.py

python3 main.py


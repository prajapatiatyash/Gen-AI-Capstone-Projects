Create a short README with these steps:

1. Create a virtualenv and install requirements:
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Fill config/*.yaml with your secrets (or set env vars: DB_PASSWORD, SECRET_KEY, MILVUS_TOKEN, MILVUS_URI).

3. Ensure your Postgres DB is populated with the schema & seed data (you already provided a create script earlier). Run that.


4. Start the FastAPI server:
uvicorn src.main:app --reload --port 8000


5. Start Streamlit examples (in separate terminals):
streamlit run streamlit_app/employee_ui.py
streamlit run streamlit_app/manager_ui.py
streamlit run streamlit_app/hr_ui.py

6. Test the flows:

Employee sends travel message → confirm ticket → manager lists pending → manager approves → HR approves & book.
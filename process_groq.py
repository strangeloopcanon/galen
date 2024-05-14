import os
from dotenv import load_dotenv
import json
import subprocess
import instructor
from pydantic import BaseModel, Field
from groq import Groq
from util import read_json, get_schema_and_table_list, execute_function_call, visualise
load_dotenv()

class Query(BaseModel):
    purpose: str
    sql: list[str] = Field(..., description="One comprehensive, perfect SQL query that does what the query asks")

def main(request):
    groq_api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=groq_api_key)
    client = instructor.from_groq(client, mode=instructor.Mode.JSON)
    resp: Query = client.chat.completions.create(
        model="llama3-70b-8192",
        response_model=Query,
        messages=[
            {"role": "user", "content": request},
        ],
        temperature=0,
    )

    sql_query = resp.sql[0]
    # Extract the dataframe
    df = execute_function_call(sql_query)
    
    # Visualize the dataframe
    if df is not None:
        chart = visualise(df)
        return chart
    else:
        print("Failed to extract dataframe")
        return None

if __name__ == '__main__':
    dirname = os.getcwd()
    config_path = os.path.join(dirname, 'config')
    subprocess.run(['python3', 'get_table_schema.py'])
    final_schema, tables = get_schema_and_table_list(config_path)
    request = f"""Extract dependency data for gene EP300, group them by OncotreeLineage and calculate averages. The schema was {final_schema} and {tables}.
    The databases are already attached as: 
    ATTACH DATABASE 'db/ProteinNetwork.db' AS ProteinNetwork
    ATTACH DATABASE 'db/DepMap.db' AS DepMap

    So ensure we use those names. You do not need to attach them again. You are writing a SQL query to answer the question from SQLITE."""
    
    result = main(request)
    if result:
        print("Visualization complete. Chart generated.")
    else:
        print("Failed to generate chart.")

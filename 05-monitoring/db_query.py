from dataclasses import dataclass

from db_init import get_db_connection
from metrics import LLMCallRecord

 # helper to return the queried tuples into data class record: 
def row_to_record(row):
    return LLMCallRecord(
        model=row[4],
        prompt=row[6],
        instructions=row[5],
        answer=row[2],
        prompt_tokens=row[7],
        completion_tokens=row[8],
        total_tokens=row[9],
        response_time=row[10],
        cost=row[11],
        timestamp=row[12],
    )

# fetch data (last 10 records ordered by timestamp): 

# remark: as the table grows, add an index on timestamp to make ordering by timestamp faster!
def get_conversations(limit=10):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, question, answer, course, model,
                       instructions, prompt,
                       prompt_tokens, completion_tokens, total_tokens,
                       response_time, cost, timestamp
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [row_to_record(row) for row in rows]


# STREAMLIT DASHBOARD QUERIES 

# want to show in the dashboard: 
# how many records are in the db
# total cost 
# avg tokens

# for example. 





if __name__ == "__main__":
    records = get_conversations()
    for record in records:
        print(record)

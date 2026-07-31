# Setup:

```
uv init --no-workspace

PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main

wget ${PREFIX}/01-agentic-rag/code/ingest.py
wget ${PREFIX}/01-agentic-rag/code/rag_helper.py

uv add python-dotenv openai requests minsearch  jupyter

```

# Monitoring 

Online monitoring: 

We are going to reuse the simple RAG application and then we'll add monitoring on top of that: 

* save all user interations to pgdb 
* and create simple dashboard 
* and create grafana dashboard 

## Creating interface: 

* save instructions 
* save prompt 
* save model used
* save how many tokes were sent / received
* how much money spent
* how much waiting / response times for us and for the user 
* ...

We are going to focus more on RAG rather than agents, for agents the approach is pretty similar.

# chat app: 

* streamlit very simple interface 

# capturing metrics: 

We want to capture
* what model
* what prompt 
* what instructions 
* what answers rec
* how many tokes sent
* how many tokes we got back 
* how much time it took to respond 
* how much money was spent 
* time stamp 


We will use data class "Metrics". 

# capturing llm data

* before now, the rag_helper script.llm method didn't capture anything so we neeed to modify it. 

# storing the log_response in a database: we choose postgres and we use docker to run postgres

Later in this lesson we are also going to run grafana, and in grafana we will need to connect to postgres, this is why we first will create a network! 

```
docker network create monitoring

docker run -it \
    --name course-assistant-pg \
    --network monitoring \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=course_assistant \
    -p 5432:5432 \
    -v pgdata:/var/lib/postgresql/data \
    postgres:17

uv add "psycopg[binary]"
```

Once we setup the db, we can create the table (called conversations which is not ideal but anyway): better, we would call it the same as the data class, for example!

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    course TEXT NOT NULL,
    model TEXT NOT NULL,
    instructions TEXT NOT NULL,
    prompt TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    response_time FLOAT NOT NULL,
    cost FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
)

We are not going to execute the sql manually by logging into the postgres container, but execute through python!

That we use psycopg for to connect to postgres and create a table there! 

Also we want to create the time stamp WITH TIMEZONE WHICH IS IMPORTANT FOR GRAFANA, TO CAPTURE THE TIME ZONE TOO!!!

* WE EXECUTRE: db_init.py (usually done only once, also when we create postgres, we have this named volume, and everytime we run we attach to the same data so we don't really need to run this again unless we change something with the schema.)

* we create db_save and test 

* note how we don't save the original question within LLMCallRecord, but we do save it in our postgres db!! 

* test: 

```
docker exec -it course-assistant-pg psql -U user -d course_assistant \
    -c "SELECT id, question, response_time, cost FROM conversations;"

```

# Querying the data and building the dashboard 

* usually we would experiment with different queries in the jupyter notebook and in this course we'll just go to the script part directly 

* script: db_query.py

# Dashboard

* won't use grafana yet, instead everything into a simple streamlit dashboard: often we don't even need postgres and don't need to bother and use sqlite, the reason we use postgres now is that we will want to connect it with grafana later. 


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

# Streamlit Dashboard

* won't use grafana yet, instead everything into a simple streamlit dashboard: often we don't even need postgres and don't need to bother and use sqlite, the reason we use postgres now is that we will want to connect it with grafana later. -> for project: in order to have something lightweight, this would be sufficient


* run: 

```
uv run streamlit run dashboard.py --server.port 8502
```

# User feedback: we captured light weigtht metrics so far 

* we could collect the user feedback for example +1 / -1 and monitor this in our dashboard, for example: why so many negative feedbacks today, what is happening?

* we'll create, besides conversation table, a separate table called 'feedback' to capture user feedback, and always reference conversation id 

* this will happen in db_init: uv run python db_init.py

* we create db_feedback.py that inserts feedback data into the db

# improvements: 

* for db_ .. we could create a module
* ideally show these feedback buttons only after the response displays
* add grafana to make file: make grafana -> gaood 

# automated feedback: built-in judge 

* We also want to collect automated feedback, which comes from another LLM. 

* Last time we used other LLM as a judge, we had ground truth data available. Now, we don't have that! 

* This step will definitely latency, and should be done asynchronously: first save the feedback to the database, and then run the judge during an asynch process for scoring, it should run separately from our web interface. 

* This works how ??? THE IDEA OF THIS JUDGE IS TO: After each answer, we ask a judge whether it's relevant to the question. We'll use a function from a previous lesson, where we used also structured output!  

* WE CAN NOT EXCEPT WONDERS FROM THIS JUDGE SOMETIMES IT MIGHT SAY THAT SOMETHING IS RELEVANT WHEN IT'S NOT AND SOMETIMES THE OPPOSITE, BUT IT'S A GOOD STARTING POINT!

* https://www.youtube.com/watch?v=uMNYVw4jh-8: 
Automated Prompt Optimization - Mikhail Sveshnikov -> this requires user data though

* now we want to save this: source="judge"

* Right now the relevance evaluation also costs money, and should somehow be monitored separately for example in table "juge-feedback" containing relevance feedback costs, so we can monitor how much we spend in total not only on processing user inputs, but also on processing through the judges

* Once we have a lot of users, maybe we can sample and only do this for 0.1 of the users. 

* We could show this in streamlit now as well but we won't and instead we will move on from this and practise using grafana for monitoring now!

# add feedback to dashboard: 

* get_relevance_stats, get_user_feedback_stats into db_query.py ->  dashboard.py

# synthetic data, because  with only a few real conversations, the charts look empty.

* generate_data.py contains a script that has function generate_live() which inserts one new conversation with optional feedback, per second, until interrupted with ctrl+c. 


# grafana to show all these things 

* grafana is also flexible but its separate application and therefore a little more heavy, (so we cant choose to either save everything to sqlite and call it a day) but grafana can: 

- alerts 
- connet to many diferent data sources including postgres 
- and more 

```
docker run -d \
    --name grafana \
    --network monitoring \
    -p 3000:3000 \
    -v grafana_data:/var/lib/grafana \
    grafana/grafana
```

* login: admin/admin
* menu -> connections -> data sources

* new dashboaed -> save -> editr 

```
SELECT
  timestamp AS time,
  response_time
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp
```


time: for grafana ti detect time serue

where from to is oimportant for the date rane range fearyure to work

# SUMMARY of what we did today: 

* we took our rag and created a simple interface for this rag and started acquiring data and putting it into the postgres db 
* built simple dashboard and now we can track and display any information we want and use any dahsboard tool we want 
*  we also built grafana dashboard now we have visibility and we also have logs!!! 

* We don't always need this level of visibility 
* we can use frameworks also such as language, streamlit, phoenix, his favorite=pydantic logfire, evaluation=evidently ai ... 

Next steps: 
* this system here is not necessarily production ready
* we need asynch way of setting up relevance evaluation 
* postgres is not the best way to store logs, some people use kafka and some other system are used to store and process these logs somewhere 

for production: 
* langsmith
* openTelemetry= easy to setup 
* logfire adds instrumentation to the code, i dont need to do naything and already have a dashboard with all the metrics, but the downside is if i want to change anything i need to go to the framework and figure out how to change anything 


OUR GOAL WAS MAINLY TO UNDERSTAND WHAT IS THE POINT OF MONITORING AND WHAT KINDS OF THINGS WOULD BE MONITORED, AND ONCE WE DO IT CONCEPTUALLY IT WILL BE THE SAME BUT TECHNOLOGY-WISE WE WILL DO SOMETHING ELSE 


Next time we set this up, we will use docker compose because we have 3 services but we need to start everything separately, and run into issues frequently etc. 

https://github.com/DataTalksClub/llm-zoomcamp/blob/main/05-monitoring/lessons/13-docker-compose.md


# dtc-llm-zoomcamp-2026


# setup: 

python version:

- curl -LsSf https://astral.sh/uv/install.sh | sh
- uv init
- uv python install 3.14
- uv venv --python 3.14 

env auto load:
```
uv tool install dirdotenv
echo 'eval "$(dirdotenv hook bash)"' >> ~/.bashrc
```

LLM provider: 

- create .env and save openai api key from https://platform.openai.com project after adding 5 euro balance

RAG (Retrieval Augmented Generation)

RAG is still what people mostly use with LLMs in the industry.

Question <-> Assistant <-> LLM : the LLM, asked a course specific question, can not really help.

We passed context. The LLM was then able to generate the correct answer.

In RAG: G-part is handled by the LLM. 
R-part is retrieval, that is synonym with search: we perform search before performing the answer.

For example, if the question contained the word course, then we search in the context everywhere for the word 'course', 
and pass everything found to the LLM (we don't know yet if it's useful).

QUESTION <-> ASSISTANT ->, <-d1,...d5 KB (1.R)
                           -d1,...d5> PROMPT (2) -> LLM (3) -> ASSISTANT


# The course FAQ dataset 

For the date we use json endpoint https://datatalks.club/faq/json/data-engineering-zoomcamp.json.
Next step would be to index the data in such a way that we can search the data.

For that we use request library.

# Search 

Now we will take the faq data and index it in such a way to perform search on it.
And then we will put it into our knowledgebase.

For that search we will use a search engine, a library that can find the the documents efficiently. 

Now we will index the data in such a way that we can get the most relevant things. 

POPULAR SEARCH ENGINES: 
- apache lucene
- elastic search (based on lucene)
- apache solr

All of those libraries are quite heavy, for examle for elastic search we need to run a docker container, etc.

Another lightweight alternative library is minsearch library:

We index the question, section, and answer fields as text (they'll be tokenized and ranked),
and the course field as a keyword (for filtering).

ex.:

{'id': '74eb249bbf',
 'course': 'llm-zoomcamp',
 'section': 'General Course-Related Questions',
 'question': 'I just discovered the course. Can I still join?',
 'answer': 'Yes, but if you want to receive a certificate, you need to submit your project while we’re still accepting submissions.'}

 text f: all the fields that an b usd  to oerform a search

keyword field: soething that we need an exact match for



BOOSTING:

We can say that certain fields will be more useful than others.

# 3 steps of rag pipeline: 1. retrieval, 2. building prompt, 3. doing the llm -> now we need to build the prompt. 

When we build AI systems, the prompts consists of 2 parts:

1st part never changes (instructions)
2nd part is user prompt (user)


# RAG helpers 

* we will now try to replace some of the modular functionalities such as search etc. 
* we created ingest.py, and rag_helper.py (with RAGBase class). 
* additionally we want to be able to replace the search library and use instead of minsearch for example elastiquesearch or sqlitesearch


# using sqlitesearch instead in in-mem minsearch 

* if the data set is larger or i want to persist that across multiple sesssions and i and i dont want to do that every time i use this 
* e.g. elasticsearch is persistent 
* e.g. sqlitesearch is persistent


Now: 


[FAQ.json -> INGEST ] -> [persistent KB]  <--> [ASSISTANT <-> USER
                                          -> PROMPT -> LLM]

* in sqlitesearch there is this thing called FTS5 (Full-text-search)
* in this case the persistent db is sqlite, in our project it can be postgres, elasticsearch, quadrant, or whatever 

* in the vectorsearch lesson we'll use other db 

* Comparison: 

With minsearch (single process): Startup: fetch data -> parse -> index -> ready; Every restart: repeat all steps

With sqlitesearch (two processes): Ingestion (runs once): fetch data -> parse -> write to faq.db; Query (runs every time): open faq.db -> search -> ready




# If i wanted to use elasticsearch, i woul need to extend the rag class and redefine function search to use elasticsearch!


# wrap up: 
* rag is most common application for llms in the industry

* ingestion, 1. retrieval, 2. building prompt, 3. doing the llm 

* different db: e.g. vector search db 
* different llms 
* search function: rag becomes the basis for agents 

* next: for the agents: llm between user and the database and let the llm decide what to send to the db
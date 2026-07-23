# setup


## obtain api keys

* Gemini API Key from Google AI Studio
* OpenAI API Key (required for flow 3) from platform.openai.com 
* Tavily API Key (required for web search: flows 3, 5, and 6) from Visit Tavily


## export the api keys to the machine 

```
export GEMINI_API_KEY="your-gemini-api-key-here" # required
export SECRET_GEMINI_API_KEY=$(echo -n $GEMINI_API_KEY | base64) # required
export SECRET_OPENAI_API_KEY=$(echo -n "your-openai-api-key-here" | base64)   # required for flow 3
export SECRET_TAVILY_API_KEY=$(echo -n "your-tavily-api-key-here" | base64)   # optional
```

## start kestra

* docker compose up -d (/ docker compose down)

## visit kestra ui 
* localhost:8080
* we have the ai copilot included because of the api key and a few secrets: we can describe our idea and it will turn it into a workflow

## import example flows from ./flows

```
cd 03-orchestration

# Adjust username and password to match your Kestra setup
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/1_chat_without_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/2_chat_with_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/3_rag_with_websearch.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/4_simple_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/5_web_research_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/6_multi_agent_research.yaml
```

## working gemini model: 

```
model-name: gemini-3.1-flash-lite
```

The gemini-2.5-flash has apparently been already deprecated.



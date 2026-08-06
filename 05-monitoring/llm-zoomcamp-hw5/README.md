# setup directory 

```
mkdir llm-zoomcamp-hw5 && cd llm-zoomcamp-hw5
uv init --no-workspace
uv add gitsource minsearch openai python-dotenv
uv add --dev ipykernel
```

Setup kernel for this project:

```
uv run python -m ipykernel install --user --name llm-zoomcamp-hw2 --display-name "llm-zoomcamp-hw2"
```

# setup rag

Download starter package:

PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/cohorts/2026/05-monitoring
wget $PREFIX/rag_helper.py
wget $PREFIX/starter.py


run: 

```
from starter import rag

query = "How does the agentic loop keep calling the model until it stops?"
answer = rag.rag(query)
print(answer)
```

# setup OpenTelemetry

```
uv add opentelemetry-api opentelemetry-sdk
```

Terms: 
* trace
* span
* attribute


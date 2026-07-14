# setup 

```
uv add --dev ipykernel
```

```
uv add requests minsearch openai jupyter python-dotenv
```



## 2.9 - Using ONNX Runtime instead of PyTorch

* sentence transformer dwl half the internet e.g. pytorch and lot of stuff, and for production it is too much overhead
* onnx embedder: is library to serve pytorch models among other things, we don't luckily need to convert the model


## 2.10 - wrapup 

* when we use vector search: we need to encode the entire dataset, and also the user query needs to be transformed into a vector. adding a lot of overhead (transforming everything to vectors, and adding everything into a db)

* we need to ask: is it really worth it? in many articles about RAG, they always assume directly that we need to use vector search, and don't even consider that we could also use text search. 

* WE SHOULD ALWAYS START AND TRY WITH TEXT SEARCH, AS SIMPLE AS POSSIBLE IN THE VERSION 1, AND LATER ON TOP, ADD VECTOR SEARCH!

* How do I know if vector search is justified: we will answer this question during module "04-EVALUATION"!

* Hybrid search and reranking will be covered in module "BEST PRACTISES"

* text search = lexical search 
* vector search = semantic search 
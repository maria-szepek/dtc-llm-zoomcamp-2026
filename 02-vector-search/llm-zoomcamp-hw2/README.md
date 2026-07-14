```
mkdir llm-zoomcamp-onnx && cd llm-zoomcamp-onnx
uv init --no-workspace
uv add onnxruntime tokenizers numpy tqdm minsearch
uv add --dev huggingface-hub jupyter
```

Setup kernel for this project:

```
uv run python -m ipykernel install --user --name llm-zoomcamp-hw2 --display-name "llm-zoomcamp-hw2"
```

Copy here: 

* https://github.com/DataTalksClub/llm-zoomcamp/blob/main/02-vector-search/embed/download.py
* https://github.com/DataTalksClub/llm-zoomcamp/blob/main/02-vector-search/embed/embedder.py

```

PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/02-vector-search/embed
wget $PREFIX/download.py
wget $PREFIX/embedder.py
```

Then dwl model: 

```
uv run python download.py
```

Then do homework: 




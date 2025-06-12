from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_embedding(text: str):
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()  # Convert numpy array to list for DB storage

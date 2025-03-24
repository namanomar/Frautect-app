import faiss
import numpy as np
import os
# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")

FAISS_INDEX_FILE = "faiss_index.bin"

def save_faiss_index(index):
    faiss.write_index(index, FAISS_INDEX_FILE)

def load_faiss_index(dimension):
    if os.path.exists(FAISS_INDEX_FILE):
        return faiss.read_index(FAISS_INDEX_FILE)
    else:
        return faiss.IndexFlatL2(dimension)

def embed_app(app_details, reviews):
    text = f"{app_details['title']} {app_details['description']}"
    for review in reviews[:5]:  # Use top 5 reviews
        text += " " + review["content"]

    # return model.encode(text, convert_to_numpy=True)

def add_app_to_faiss(index, app_id, app_details, reviews):
    vector = embed_app(app_details, reviews)
    index.add(np.array([vector], dtype=np.float32))
    save_faiss_index(index)  # Save after adding
    return vector


def find_similar_apps(index, new_app_details, new_reviews, top_k=3):
    new_vector = embed_app(new_app_details, new_reviews)
    D, I = index.search(np.array([new_vector], dtype=np.float32), top_k)

    return I  # Indices of similar apps


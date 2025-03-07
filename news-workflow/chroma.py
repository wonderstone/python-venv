import asyncio
import chromadb


# ~ Method 1: Using Sentence Transformers ~
# ~ local model
from chromadb.utils import embedding_functions
model_name = 'models/sentence-transformers/all-MiniLM-L6-v2'
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)

# ~ Method 2: Using Ollama ~
# ~ customized embedding function
from langchain_ollama import OllamaEmbeddings
import numpy as np

# Define a custom embedding function for ChromaDB using Ollama
class ChromaDBEmbeddingFunction:
    """
    Custom embedding function for ChromaDB using embeddings from Ollama.
    """
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input):
        # Ensure the input is in a list format for processing
        if isinstance(input, str):
            input = [input]
        embeddings = self.langchain_embeddings.embed_documents(input)
        # Convert embeddings to NumPy array
        return np.array(embeddings)

# Initialize the embedding function with Ollama embeddings
custom_ollama_ef = ChromaDBEmbeddingFunction(
    OllamaEmbeddings(
        model="Qwen2.5:14b",
        base_url="http://localhost:11434"  # Adjust the base URL as per your Ollama server configuration
    )
)

# ~ Method 3: Using Ollama with ChromaDB ~
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# create EF with custom endpoint
chromaDB_ollama_ef = OllamaEmbeddingFunction(
    model_name="Qwen2.5:14b",
    url="http://localhost:11434/api/embeddings",
)


async def CreateCollection(nm, ef):
    client = await chromadb.AsyncHttpClient()

    collection = await client.create_collection(name=nm,embedding_function=ef)
    await collection.upsert(
        documents=["hello world", "蜜雪冰城", "浦发银行"],
        ids=["id1", "id2", "id3"],
    )

# delete the collection
async def DeleteCollection(nm):
    client = await chromadb.AsyncHttpClient()
    await client.delete_collection(name=nm)


if __name__ == "__main__":

    name = "my_collection"
    # ef = sentence_transformer_ef
    # ef = chromaDB_ollama_ef
    ef = custom_ollama_ef


    asyncio.run(DeleteCollection(name))
    asyncio.run(CreateCollection(name, ef))
    # Query the collection
    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_collection("my_collection", embedding_function=ef)


    collection.upsert(
        documents=["hello world", "蜜雪冰城", "浦发银行"],
        ids=["id1", "id2", "id3"],
    )

    res = collection.query(
        query_texts=["hello wor"],
        n_results=1,
    )
    print(res)

    res = collection.query(
        query_texts=["蜜雪"],
        n_results=1,
    )
    print(res)

    res = collection.query(
        query_texts=["浦发行"],
        n_results=1,
    )
    print(res)
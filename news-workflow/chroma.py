import asyncio
import chromadb

from langchain_huggingface import HuggingFaceEmbeddings

import os
os.environ['HF_HOME'] = '/Users/mac/.cache/huggingface/hub/'
os.environ['TRANSFORMERS_CACHE'] = '/Users/mac/.cache/huggingface/hub/'
# model_name = "/Users/mac/.cache/huggingface/hub/"

embedding = HuggingFaceEmbeddings(model_name='BAAI/bge-large-zh-v1.5',cache_folder='/Users/mac/.cache/huggingface/')



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
    from chromadb.utils import embedding_functions

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    )


    name = "my_collection"

    asyncio.run(DeleteCollection(name))

    # asyncio.run(CreateCollection(name, embedding))
    # Query the collection
    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_collection("my_collection")


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
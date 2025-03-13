# Save news summary in chroma
# Assume chroma already provided.
# Assume news item at least has summary attribute(target interested) and unique id stored in some db(say, MySQL) 
# ! Quit the clash before running


# ~ 01 func : create a collection in chroma
# input : collection name, embedding function
# output : whether collection created successfully
import asyncio
import chromadb
from colorama import Fore, Style, init

init()

async def CreateCollection(nm, ef) -> tuple[bool, Exception]:
    client = await chromadb.AsyncHttpClient()

    # check if collection already exists
    collections = await client.list_collections()
    if nm in collections:
        print(Fore.YELLOW + f"Collection {nm} already exists.")
        return False, None
    
    # try to create collection
    try:
        collection = await client.create_collection(name=nm,embedding_function=ef)
        return True, None
    except Exception as e:
        return False, e
    
# ~ 01 func : delete a collection in chroma
# input : collection name
# output : whether collection deleted successfully
async def DeleteCollection(nm) -> tuple[bool, Exception]:
    client = await chromadb.AsyncHttpClient()

    # check if collection exists
    collections = await client.list_collections()
    if nm not in collections:
        print(Fore.CYAN + f"Collection {nm} does not exist.")
        return False, None

    # try to delete collection
    try:
        await client.delete_collection(name=nm)
        return True, None
    except Exception as e:
        return False, e

# ~  02 func : upsert news summary
# input : collection name, news summary, unique id, embedding function
# & Official Doc recommand once provide the embedding function, get the collection also with the embedding function parameter
# & but i think it's not necessary, since the collection is already created with the embedding function
# & so we try it in delete func and see if it works
# output : whether news summary upserted successfully
async def UpsertSummary(nm, summary, id, ef) -> tuple[bool, Exception]:
    client = await chromadb.AsyncHttpClient()
    collection = await client.get_collection(name=nm, embedding_function=ef)

    # check if collection exists
    if collection is None:
        print(f"Collection {nm} does not exist.")
        return False, None

    # try to upsert news summary
    try:
        await collection.upsert(
            documents=[summary],
            ids=[id],
        )
        return True, None
    except Exception as e:
        print(e)
        return False , e


# ~ 02 func : delete news summary
# input : collection name, unique id

# output : whether news summary deleted successfully
async def DeleteSummary(nm, id) -> tuple[bool, Exception]:
    client = await chromadb.AsyncHttpClient()
    collection = await client.get_collection(name=nm)

    # check if collection exists
    if collection is None:
        print(f"Collection {nm} does not exist.")
        return False, None

    # try to delete news summary
    try:
        await collection.delete(ids=[id])
        return True, None
    except Exception as e:
        return False, e
    
# ~ 03 func : query news summary
# input : collection name, embedding function, query text, n_results
# output : query results

def QuerySummary(nm, ef, query_texts, n_results) -> list:
    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_collection(nm, embedding_function=ef)

    # check if collection exists
    if collection is None:
        print(f"Collection {nm} does not exist.")
        return []
    
    # try to query news summary
    try:
        res = collection.query(
            query_texts=query_texts,
            n_results=n_results,
        )
        return res
    except Exception as e:
        print(f"Error: {e}")
        return []   



if __name__ == "__main__":
    # * 01  collection name
    name = "summary_collection"
    
    # * 02  embedding function
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

    # create EF with custom endpoint
    chromaDB_ollama_ef = OllamaEmbeddingFunction(
        model_name="Qwen2.5:14b",
        url="http://localhost:11434/api/embeddings",
    )

    # * 03  news summary
    summary = "hello world"
    id = "id1"

    # * 04  query text
    query_texts = ["hello wor"]
    n_results = 1

    # * 05  create collection
    print(Fore.LIGHTGREEN_EX + "Start to Test collection related Method!")
    asyncio.run(DeleteCollection(name))
    asyncio.run(CreateCollection(name, chromaDB_ollama_ef))

    # * 06  upsert news summary
    asyncio.run(UpsertSummary(name, summary, id, chromaDB_ollama_ef))

    # * 07  query news summary
    res = QuerySummary(name, chromaDB_ollama_ef, query_texts, n_results)
    print(res)

    # * 08  delete news summary
    print(Fore.LIGHTYELLOW_EX)

    print("Delete the summary")
    asyncio.run(DeleteSummary(name, id))
    res = QuerySummary(name, chromaDB_ollama_ef, query_texts, n_results)

    print(res)


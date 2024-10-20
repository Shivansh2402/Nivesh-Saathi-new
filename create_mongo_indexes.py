from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.server_api import ServerApi

from metahackathonfinance import settings


def connect():
    global db
    client = MongoClient(settings.mongo_atlas_connection_uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client["metahackathon-health"]


def create_index(collection: str, dimension: int, similarity: str):
    global db
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "vector",
                    "numDimensions": dimension,
                    "similarity": similarity
                }
            ]
        },
        name="vector_index",
        type="vectorSearch",
    )
    collection_obj = db[collection]
    if collection_obj.create_search_index(model=search_index_model) == "vector_index":
        print("Index created successfully")


def create_atlas_vector_search_index(collection: str):
    collection_obj = db[collection]
    search_index_model = SearchIndexModel(
        definition={
            "mappings": {
                "dynamic": True
            },
        },
        name="text_index",
    )
    if collection_obj.create_search_index(model=search_index_model) == "text_index":
        print("Index created successfully")



def create_semantic_cache_index(collection: str):
    collection_obj = db[collection]
    search_index_model = SearchIndexModel({
      "fields": [
        {
          "numDimensions": 1536,
          "path": "embedding",
          "similarity": "cosine",
          "type": "vector"
        },
        {
          "name": "vector_index",
          "path": "llm_string",
          "type": "filter"
        }
      ]
    })
    if collection_obj.create_search_index(model=search_index_model) == "vector_index":
        print("Index created successfully")



if __name__ == "__main__":
    connect()
    collection_name = "aarogya-assist"
    create_index(collection_name, 1536, "euclidean")
    create_atlas_vector_search_index(collection_name)
    # create_semantic_cache_index(collection_name)
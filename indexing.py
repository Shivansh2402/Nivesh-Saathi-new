import csv
import json
import os.path
import time
from ast import literal_eval
from functools import lru_cache
from uuid import UUID

import numpy as np
import openai
import pandas as pd
import requests

from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.read_preferences import SecondaryPreferred
from pymongo.server_api import ServerApi

from hnsw.hnsw import get_index

openai.api_key = "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"
uri = "mongodb+srv://developer:3C01meWAequk8vja@mongopoc.3vi4o.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client["genai"]


def delete_documents(collection: str, filter: dict = {}):
    global db
    collection_obj = db[collection]
    response = collection_obj.delete_many(filter)
    print(f"Deleted {response.deleted_count} documents")


def update_index(collection: str):
    collection_obj = db[collection]
    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "vector",
                "numDimensions": 1536,
                "similarity": "cosine"
            },
            {
                "type": "filter",
                "path": "category"
            },
            {
                "type": "filter",
                "path": "title"
            },
            {
                "type": "filter",
                "path": "col"
            }
        ]
    }
    if collection_obj.update_search_index("vector_index", definition):
        print(f"Index vector_index updated successfully")


def create_index_vector_index(collection: str, dimension: int, similarity: str):
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "vector",
                    "numDimensions": dimension,
                    "similarity": similarity
                },
                {
                    "type": "filter",
                    "path": "category"
                },
                {
                    "type": "filter",
                    "path": "title"
                },
                {
                    "type": "filter",
                    "path": "botRef"
                }
            ]
        },
        name="vector_index",
        type="vectorSearch",
    )
    collection_obj = db[collection]
    try:
        if collection_obj.create_search_index(model=search_index_model) == "vector_index":
            print("Index created successfully")
    except Exception:
        print("Index already exists")


def create_atlas_search_index(collection: str):
    collection_obj = db[collection]
    search_index_model = SearchIndexModel(
        definition={
            "analyzer": "lucene.standard",
            "searchAnalyzer": "lucene.standard",
            "mappings": {
                "dynamic": False,
                "fields": {
                    "title": {
                        "type": "string",
                    },
                    "category": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "primary-category": {
                        "type": "string"
                    },
                    "document": {
                        "type": "string"
                    },
                }
            }
        },
        type="search",
        name="fts_index",
    )
    response = collection_obj.list_search_indexes('fts_index')

    try:
        if "fts_index" not in response and collection_obj.create_search_index(model=search_index_model) == "fts_index":
            print("Index created successfully")
    except Exception:
        print("Index already exists")


def index_nova(collection: str):
    global db
    all_data = get_data('nova')
    collection_obj = db[collection]
    if all_data:
        batch = 100
        for i in range(0, len(all_data), batch):
            data_batch = all_data[i:i + batch]
            for j, doc in enumerate(data_batch):
                doc['botRef'] = 'nova'
            res = collection_obj.insert_many(data_batch)
            print(f"Indexed {len(res.inserted_ids)} documents : {res.acknowledged}")
    else:
        all_data = []
        embeddings, uuids = get_index("a12059be-33b6-42bb-88a1-9919bcbd5278", "../nova", {}, 6000).get_embeddings()
        print(f"Length of embeddings: {len(embeddings)} and Length of uuids: {len(uuids)}")
        with open("../nova/output.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = dict(row)
                doc = {'document': data['document'], 'vector': embeddings[uuids.index(UUID(data['uuid']))],
                       'url': literal_eval(data['metadata']).get('source', None),
                       'category': literal_eval(data['metadata']).get('category', "default"), 'botRef': 'nova'}
                all_data.append(doc)
        collection_obj = db[collection]
        batch = 100
        for i in range(0, len(all_data), batch):
            data_batch = all_data[i:i + batch]
            docs = [d['document'] for d in data_batch]
            embeds = openai.embeddings.create(
                input=docs,
                model="text-embedding-ada-002"
            ).data
            # # embeds = np.load('embeddings.npy')
            for j, doc in enumerate(data_batch):
                doc['botRef'] = 'nova'
                doc['vector'] = embeds[j].embedding
                embeddings.append(embeds[j].embedding)
            res = collection_obj.insert_many(data_batch)
            print(f"Indexed {len(res.inserted_ids)} documents : {res.acknowledged}")
        np.save(f'{collection_name}.npy', np.array(embeddings))


def index_fnp(collection: str):
    global db
    all_data = get_data('fnp_products_2')
    if not all_data:
        embeddings = []
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                data = dict(row)
                title = data['title']
                category = data['category']
                primary_category = data['primary-category']
                description = data['description']
                data['document'] = f"""A Product titled {title} who's category is {category} and can be sold as
                 {primary_category} whose 
                description 
                starts with {description}"""
                data['col'] = 'fnp'
                all_data.append(data)
                i = i + 1
    collection_obj = db[collection]
    batch = 100
    for i in range(0, len(all_data), batch):
        data_batch = all_data[i:i + batch]
        # docs = [d['document'] for d in data_batch]
        # embeds = openai.embeddings.create(
        #     input=docs,
        #     model="text-embedding-ada-002"
        # ).data
        # embeds = np.load('fnp_products_2.npy')
        for j, doc in enumerate(data_batch):
            # doc['vector'] = embeds[j].tolist()
            doc['botRef'] = 'fnp'
            # embeddings.append(embeds[j].embedding)
        res = collection_obj.insert_many(data_batch)
        print(f"Indexed {len(res.inserted_ids)} documents : {res.acknowledged}")
    # np.save(f'{collection_name}.npy', np.array(embeddings))


def aggregation(collection: str, pipeline: list):
    global db
    t1 = time.time()
    collection_obj = db.get_collection(collection, read_preference=SecondaryPreferred())
    t2 = time.time()
    response = collection_obj.aggregate(pipeline)
    # print(f"Time taken: {t2 - t1} seconds")
    docs = []
    for doc in response:
        docs.append(doc)
    return docs, t2 - t1


def run_search(collection_name: str, query: list[float], filter: dict, exact=False):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "vector",
                "queryVector": [],
                "limit": 5,
                "exact": exact
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "category": 1,
                "primary-category": 1,
                "description": 1,
                "document": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]
    if not exact:
        pipeline[0]["$vectorSearch"]["numCandidates"] = 50
    pipeline[0]["$vectorSearch"]["queryVector"] = query
    if filter:
        pipeline[0]["$vectorSearch"]["filter"] = filter
    return aggregation(collection_name, pipeline)


def run_text_search(collection_name: str, query: str):
    pipeline = [
        {
            "$search": {
                "index": "fts_index",
                "text": {"query": query, "path": ['document', 'title', 'category', 'primary-category', 'description']},
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "category": 1,
                "primary-category": 1,
                "description": 1,
                "document": 1,
                "score": {
                    "$meta": "searchScore"
                }
            }
        },
        {
            "$limit": 5
        }
    ]
    return aggregation(collection_name, pipeline)


make_array = {
    "$group": {"_id": None, "docs": {"$push": "$$ROOT"}}
}

add_rank = {
    "$unwind": {"path": "$docs", "includeArrayIndex": "rank"}
}


def make_projection_doc(score_field_name):
    return {
        "$project": {
            score_field_name: 1,
            "_id": "$docs._id",
            "title": "$docs.title",
            "category": "$docs.category",
            "description": "$docs.description",
            "document": "$docs.document",
            "primary-category": "$docs.primary-category"
        }
    }


def make_compute_score_doc(priority, score_field_name):
    return {
        "$addFields": {
            score_field_name: {
                "$divide": [
                    1.0,
                    {"$add": ["$rank", priority, 60]}
                ]
            }
        }
    }


def run_hybrid_search(collection: str, query: str, vector: list[float]):
    vector_search = {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "vector",
            "queryVector": vector,
            "numCandidates": 50,
            "limit": 5
        }
    }
    text_search = {
        "$search": {
            "index": "fts_index",
            "text": {"query": query, "path": {"wildcard": "*"}},
        }
    }

    limit_results = {
        "$limit": 5
    }

    combine_search_results = {
        "$group": {
            "_id": "$_id",
            "vs_score": {"$max": "$vs_score"},
            "ts_score": {"$max": "$ts_score"},
            "title": {"$first": "$title"},
            "category": {"$first": "$category"},
            "description": {"$first": "$description"},
            "document": {"$first": "$document"},
            "primary-category": {"$first": "$primary-category"}
        }
    }

    project_combined_results = {
        "$project": {
            "_id": 1,
            "title": 1,
            "category": 1,
            "description": 1,
            "document": 1,
            "primary-category": 1,
            "score": {
                "$let": {
                    "vars": {
                        "vs_score": {"$ifNull": ["$vs_score", 0]},
                        "ts_score": {"$ifNull": ["$ts_score", 0]}
                    },
                    "in": {"$add": ["$$vs_score", "$$ts_score"]}
                }
            }
        }
    }

    sort_results = {
        "$sort": {"score": -1}
    }

    pipeline = [
        vector_search,
        make_array,
        add_rank,
        make_compute_score_doc(1, "vs_score"),
        make_projection_doc("vs_score"),
        {
            "$unionWith": {"coll": collection,
                           "pipeline": [
                               text_search,
                               limit_results,
                               make_array,
                               add_rank,
                               make_compute_score_doc(0.9, "ts_score"),
                               make_projection_doc("ts_score")
                           ]
                           }
        },
        combine_search_results,
        project_combined_results,
        sort_results,
        limit_results
    ]
    return aggregation(collection, pipeline)


test_queries = ["i want to gift something special for this fathers day",
                "photo frames for mothers day",
                "7 x 7 inche Photo Frame",
                "Photo frame and Ferrero rocher for mothers day",
                "i want a gift a personalised floral pendent for my girl friend for this valentiens day",
                "i want a gift a small teddy bear for my girl friend for this valentiens day",
                "Personalised Mug along with 4 ferrero rocher and a 6 x 4 inches photo frame for mothers day",
                "i want a plush toy of a brown bear with rose combo",
                "what should i gift my wife for her birthday",
                "anything for 1st birthday",
                "can you suggest some birthday gifts for guys",
                "Serene Vibes Bouquet and Luscious 500gms Black forest cake",
                "Personalised Mugs set of 2 with personalised images on them for valentines day",
                "Timeless Love Red Roses Bouquet",
                "Timeless Love Red Roses Bouquet with 10 Red Roses",
                "premium decorations for fathers day",
                "premium baloon decorations for fathers day",
                "Do you have any combo with a chocolate cake and gutarist for birthday?",
                "chocolate cake and gutarist combo for birthday?"]


def fts_chroma(collection_uuid: str, query: str):
    url = "http://engati-chroma.qa.engati.local:8091/api/v1/collections/" + collection_uuid + "/fts"
    response = requests.post(
        url,
        data=json.dumps(
            {
                "query": query,
                "language": "en",
                "n_results": 50,
            }
        ),
    )
    response = response.json()
    docs = []
    i = 0
    for result in zip(
            response["documents"][0],
            response["metadatas"][0],
            response["ids"][0],
    ):
        doc = {"document": result[0], "metadata": result[1], "score": 0}
        docs.append(doc)
        i = i + 1
        if i == 5:
            break
    return docs


def knn_remote_chroma(collection_uuid: str, query_embed: list[float], k: int):
    url = "http://engati-chroma.qa.engati.local:8091/api/v1/collections/" + collection_uuid + "/query"
    response = requests.post(
        url,
        data=json.dumps(
            {
                "query_embeddings": [query_embed],
                "where": {},
                "where_document": {},
                "include": ['documents', 'metadatas'],
                "n_results": 50,
            }
        ),
    )
    response = response.json()
    docs = []
    i = 0
    for result in zip(
            response["documents"][0],
            response["metadatas"][0],
            response["ids"][0],
    ):
        doc = {"document": result[0], "metadata": result[1], "score": 0}
        docs.append(doc)
        i = i + 1
        if i == k:
            break
    return docs


def knn_chroma(collection_uuid: str, query_embed: list[float], k: int):
    embeddings, uuids = get_index(collection_uuid, "../nova", {}, 5523).get_embeddings()
    index = get_index(collection_uuid, "../nova", {}, 5523)
    uuids, scores = index.get_nearest_neighbors([query_embed], 500, uuids)
    all_data = []
    i = 0
    with open("../nova/output.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = dict(row)
            if UUID(data['uuid']) in uuids[0]:
                all_data.append({'document': data['document'], 'score': scores[0][i], 'metadata': data['metadata']})
                i = i + 1
                if i == k:
                    break
    return all_data


def search_nova(collection_name: str, queries: list[str], filter: dict = {}):
    df = pd.DataFrame()
    query_list = []
    response_list = []
    text_response = []
    enn_response = []
    chroma_remote = []
    chroma_fts = []
    for query in queries:
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        embeddings = response.data[0].embedding
        for i in range(5):
            query_list.append(query)
        response = run_search(collection_name, embeddings, filter, exact=False)
        response_list = extract_response(response_list, query, response)
        response = run_search(collection_name, embeddings, filter, exact=True)
        enn_response = extract_response(enn_response, query, response)
        response = run_text_search(collection_name, query)
        text_response = extract_response(text_response, query, response)
        response = knn_remote_chroma('c4d5aa4d-f44a-4536-920e-f6ec2a764ef4', embeddings, 5)
        chroma_remote = extract_response(chroma_remote, query, response)
        response = fts_chroma('c4d5aa4d-f44a-4536-920e-f6ec2a764ef4', query)
        chroma_fts = extract_response(chroma_fts, query, response)

    df['Query'] = query_list
    df['Mongo ANN'] = response_list
    df['Mongo ENN'] = enn_response
    df['Chroma ANN'] = chroma_remote
    df['Mongo FTS'] = text_response
    df['Chroma FTS'] = chroma_fts

    df.to_csv(f'{collection_name}_results.csv', index=False)


def search(collection_name: str, queries: list[str], filter: dict = {}):
    df = pd.DataFrame()
    query_list = []
    response_list = []
    text_response = []
    hybrid_list = []
    enn_result = []
    for query in queries:
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        embeddings = response.data[0].embedding
        for i in range(5):
            query_list.append(query)
        response = run_search(collection_name, embeddings, filter, exact=False)
        response_list = extract_response(response_list, query, response)
        response = run_search(collection_name, embeddings, filter, exact=True)
        enn_result = extract_response(enn_result, query, response)
        response = run_text_search(collection_name, query)
        text_response = extract_response(text_response, query, response)
        response = run_hybrid_search(collection_name, query, embeddings)
        hybrid_list = extract_response(hybrid_list, query, response)
    df['Query'] = query_list
    df['ANN Response'] = response_list
    df['ENN Response'] = enn_result
    df['Text Search Response'] = text_response
    df['Hybrid Search Response'] = hybrid_list
    name = collection_name + "_filter_results.csv" if filter else collection_name + "_results.csv"
    df.to_csv(name, index=False)


def extract_response(list_res, query, response):
    if not response:
        for i in range(5):
            list_res.append(f"No results found for query: {query}")
    for res in response:
        list_res.append(
            f"""{res['document']} Score: {res['score']}""")
    return list_res


def get_data(collection_name: str):
    global db
    collection_obj = db[collection_name]
    response = collection_obj.find({})
    docs = []
    for doc in response:
        del doc['_id']
        docs.append(doc)
    return docs


def index_duplciate_data(collection_name: str):
    global db
    all_data = get_data()
    collection_obj = db[collection_name]
    batch = 100
    for i in range(0, len(all_data), batch):
        data_batch = all_data[i:i + batch]
        res = collection_obj.insert_many(data_batch)
        print(f"Indexed {len(res.inserted_ids)} documents : {res.acknowledged}")


import sqlite3

conn = sqlite3.connect('../engoma.db')
c = conn.cursor()


def data_from_sqlite(uuid: str, botRef: str):
    c.execute(
        'SELECT document,metadata from embeddings where uuid=? and collection_uuid in(select uuid from collections '
        'where name=?)',
        (uuid, botRef,))
    data = c.fetchall()
    return data


def get_data_from_jsonl(file_name, botRef: str):
    with open(file_name, 'r') as f:
        batch = []
        for line in f:
            try:
                d = json.loads(line)
            except:
                print(f"Skipping line:{line}")
                continue
            doc = {'vector': d['response']['body']['data'][0]['embedding']}
            s = data_from_sqlite(str(d["custom_id"]).split("_")[1], botRef)
            doc['document'] = s[0][0]
            try:
                metadata = literal_eval(s[0][1])
            except:
                print(f"Error in metadata:{s[0][1]}")
                metadata = {}
            doc['category'] = metadata.get('category', 'default')
            doc['url'] = metadata.get('source', None)
            doc['botRef'] = botRef
            batch.append(doc)
            if len(batch) >= 100:
                yield batch
                batch = []
        yield batch


def index_all_data(collection_name: str):
    global db
    qa_bots_data = [{"count": 34518, "botRef": 49065},
                    {"count": 30592, "botRef": 48247},
                    {"count": 28295, "botRef": 48265},
                    {"count": 27731, "botRef": 48266},
                    {"count": 23958, "botRef": 55899},
                    {"count": 22689, "botRef": 48228},
                    {"count": 21492, "botRef": 60056},
                    {"count": 20855, "botRef": 50605},
                    {"count": 20322, "botRef": 44284},
                    {"count": 20145, "botRef": 56816}]
    for bot in qa_bots_data:
        if str(bot.get("botRef")) in db.list_collection_names():
            print(f"Collection for bot {bot.get('botRef')} already exists")
            collection_obj = db[str(bot.get("botRef"))]
        else:
            collection_obj = db.create_collection(str(bot.get("botRef")))
        create_index_vector_index(str(bot.get("botRef")), 1536, "euclidean")
        response = collection_obj.count_documents({"botRef": bot.get("botRef")})
        if response == bot.get("count"):
            print(f"Data for bot {bot.get('botRef')} already exists")
            continue
        if os.path.exists(f"../data/qa_{bot.get('botRef')}_output.jsonl"):
            i = 0
            for data in get_data_from_jsonl(f"../data/qa_{bot.get('botRef')}_output.jsonl", str(bot.get('botRef'))):
                res = collection_obj.insert_many(data)
                i = i + 1
                print(f"Indexed {len(res.inserted_ids)} documents : {res.acknowledged} batch:{i}")


nova_queries = ["Tell me about PCOS",
                "Can we have a baby boy in twins through IVF",
                "Is there a higher chance of pregnancy through IVF (in vitro fertilization)?",
                "What is the cost of IUI treatment",
                "What are the steps of IVF treatment",
                "Gifts for fathers day", ]

inc_queries = ["where is the taj mahal?", "Beautiful spots in Jaipur", "Tell me about Bhangarh", "best places to visit "
                                                                                                 "in Jharkhand",
               "What are the opening and closing timings of taj mahal?", "What are the best places to visit in "
                                                                         "Lakshadweep",
               "Book flights to travel to Delhi", "traditional sweets of Rajasthan"]

if __name__ == '__main__':
    # collection_name = "fnp_products_2"
    # delete_documents(collection_name)
    # index_fnp(collection_name)
    # create_index_vector_index(collection_name, 1536, "euclidean")
    # create_atlas_search_index(collection_name)
    # search(collection_name, test_queries)

    # collection_name = "nova_0"
    # delete_documents(collection_name, {"col": {"$eq": "fnp"}})
    # cols = ['sample_snappy_compression']
    # for col in cols:
    #     index_nova(col)

    collections_list = ["49065", "48247", "48265", "48266", "55899", "48228", "60056", "50605", "44284",
                        "56816", "sample_snappy_compression", "sample_zstd_compression", "sample_zlib_compression"]
    for col in collections_list:
        create_index_vector_index(col, 1536, "euclidean")
    # create_index_vector_index(collection_name, 1536, "euclidean")
    # create_atlas_search_index(collection_name)
    # index_fnp(collection_name)
    # update_index(collection_name)
    # search_nova(collection_name, nova_queries, {})
    # search(collection_name, test_queries, {"col": {"$eq": "fnp"}})
    # index_nova(collection_name)
    # collection_name = "all"
    # delete_documents(collection_name)
    # index_all_data("")
    # create_index_vector_index(collection_name, 1536, "euclidean")
    # delete_documents(collection_name, {"botRef": {"$eq": "nova"}})
    # search(collection_name, test_queries, {})
    # create_atlas_search_index("60056")
    # search_nova("60056", inc_queries)
# # from langchain_community.document_loaders import WebBaseLoader, UnstructuredURLLoader
# # from langchain_experimental.text_splitter import SemanticChunker
# # from langchain_openai import OpenAIEmbeddings
# # # from langchain_text_splitters import RecursiveCharacterTextSplitter
# # # from langchain.embeddings import BedrockEmbeddings
# # import boto3
# # import os
# #
# # # export AWS_ACCESS_KEY_ID=AKIAU7EBQ25OHVC7ZZNX
# # # export AWS_SECRET_ACCESS_KEY=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
# # # export AWS_DEFAULT_REGION=us-east-1
# #
# # os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAU7EBQ25OHVC7ZZNX'
# # os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
# # API_KEY = "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"
# #
# # loader = WebBaseLoader(["https://www.teachforindia.org/about-us"])
# # bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
# #
# # region_name ="us-east-1"
# # credentials_profile_name = "bedrock-runtime"
# # model_id = "us.meta.llama3-2-90b-instruct-v1:0"
# #
# # # be = BedrockEmbeddings(
# # #     credentials_profile_name=credentials_profile_name,
# # #     region_name=region_name,
# # #     model_id=model_id
# # # )
# #
# #
# # # data = loader.load()
# # # text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
# # loader = WebBaseLoader(["https://www.incredibleindia.gov.in/en/jharkhand"])
# # data = loader.load()
# # text_splitter = SemanticChunker(OpenAIEmbeddings(openai_api_key=API_KEY))
# # # all_splits = text_splitter.split_documents(data)
# # document_list = [doc.page_content for doc in data]
# # # text_splitter = SemanticChunker(be)
# # docs = text_splitter.create_documents(document_list)
# # print(len(docs))
# # print(docs[0].page_content)
# # print("--------------------------------")
# # print(docs[1].page_content)
#
#
#
#
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai.embeddings import OpenAIEmbeddings
# import urllib.request
# import xml.etree.ElementTree as ET
#
# def semantic_split(docs):
#     splitter = SemanticChunker(
#         OpenAIEmbeddings(), breakpoint_threshold_type="percentile"
#     )
#     return splitter.split_documents(docs)
#
#
# def get_all_links_from_xml(sitemap_url):
#     try:
#         all_urls = []
#
#         xml_data = urllib.request.urlopen(sitemap_url).read()
#         tree = ET.fromstring(xml_data)
#         urls = self.find_urls_from_sitemap_tree(tree, "sitemap")
#         if len(urls) == 0:
#             urls = self.find_urls_from_sitemap_tree(tree, "url")
#             for sub_url in urls:
#                 all_urls.append(sub_url)
#         else:
#             for url in urls:
#                 xml_data = urllib.request.urlopen(url).read()
#                 tree = ET.fromstring(xml_data)
#                 sub_urls = self.find_urls_from_sitemap_tree(tree, "url")
#                 for sub_url in sub_urls:
#                     all_urls.append(sub_url)
#         return all_urls
#     except Exception as e:
#         raise Exception(e)
#
# def find_urls_from_sitemap_tree(tree, tree_type):
#     if tree_type == "sitemap":
#         return [
#             sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
#             for sitemap in tree.findall(
#                 "{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"
#             )
#             if sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
#             is not None
#         ]
#     if tree_type == "url":
#         return [
#             sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
#             for sitemap in tree.findall(
#                 "{http://www.sitemaps.org/schemas/sitemap/0.9}url"
#             )
#             if sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
#             is not None
#         ]
#
#
# if __name__ == "__main__":
#     urls = get_all_links_from_xml("https://zerodha.com/varsity/chapter-sitemap2.xml")
#     print(urls)



import threading
import time
import csv

import openai
import pandas as pd

from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.server_api import ServerApi

openai.api_key = "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"
uri = "mongodb+srv://developer:3C01meWAequk8vja@metahackathon.3vi4o.mongodb.net/"


def connect():
    global db
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client["metahackathon-health"]


def create_index(collection: str, dimension: int, similarity: str):
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


# def index_fnp(collection: str):
#     global db
#     all_data = []
#     with open('products-1.csv') as csvfile:
#         reader = csv.DictReader(csvfile)
#         i = 0
#         for row in reader:
#             data = dict(row)
#             title = data['title']
#             category = data['category']
#             primary_category = data['primary-category']
#             description = data['description']
#             data['document'] = f"""A Product titled {title} who's category is {category} and can be sold as
#              {primary_category} whose
#             description
#             starts with {description}"""
#             data['vector'] = openai.embeddings.create(
#                 input=data['document'],
#                 model="text-embedding-ada-002"
#             ).data[0].embedding
#             all_data.append(data)
#             i = i + 1
#     collection_obj = db[collection]
#     res = collection_obj.insert_many(all_data)
#     print(f"Indexed {res.inserted_ids} documents : {res.acknowledged}")
#
#
# def aggregation(collection: str, pipeline: list):
#     global db
#     collection_obj = db[collection]
#     response = collection_obj.aggregate(pipeline)
#     docs = []
#     for doc in response:
#         docs.append(doc)
#     return docs


# collection_name = "fnp"
# index_fnp(collection_name)
# create_index(collection_name, 1536, "euclidean")
# create_atlas_vector_search_index(collection_name)

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "vector",
            "queryVector": [],
            "numCandidates": 50,
            "limit": 5
        }
    },
    {
        "$project": {
            "_id": 0,
            "title": 1,
            "category": 1,
            "primary-category": 1,
            "description": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
    }
]


def run_search(query: str):
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    query_embedding = response.data[0].embedding
    pipeline[0]["$vectorSearch"]["queryVector"] = list(query_embedding)
    return aggregation(collection_name, pipeline)


def run_text_search(query: str):
    pipeline = [
        {
            "$search": {
                "index": "text_index",
                "text": {"query": query, "path": "title"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "category": 1,
                "primary-category": 1,
                "description": 1,
                "score": {
                    "$meta": "searchScore"
                }
            }
        }
    ]
    return aggregation(collection_name, pipeline)


# openai.api_key = "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"

# test_queries = ["birthday cake for 2 year old son",
#                 "suggest 2kg cake for 3 year old kid",
#                 "show more gifts for parents",
#                 "show bouquets for parents",
#                 "fitness enthu, loves traveling, budget is below 2000",
#                 "suggest me a gift for - 40 yrs old and a good friend, birthday",
#                 "40 yrs old and a good friend, birthday",
#                 "suggest anniversary gifts",
#                 "gifts for parents",
#                 "suggest gifts for fitness enthusiast freint",
#                 "i want to give a gift to my friend",
#                 "suggest 2kg cake for 3 year old boy birthday",
#                 "suggest 2kg cake for 2 year old kid",
#                 "i need pink flowers only and below 1000 rs",
#                 "do you have flowers",
#                 "do you have more products or thats it",
#                 "not this car for kids my brother is 28 year old",
#                 "Sports related gifts for brother",
#                 "gift for mothers birthday, she likes cooking and travelling",
#                 "gifts for 2 year kid below 1000 rs",
#                 "gifts for anniversary",
#                 "want flowers for my girlfriend",
#                 "i need to buy gifts for my sister , suggest me something",
#                 "I want to gift a purse can you suggest?"]


# def search():
#     df = pd.DataFrame()
#     query_list = []
#     response_list = []
#     text_response = []
#     for query in test_queries:
#         t1 = time.time()
#         response = run_search(query)
#         for res in response:
#             query_list.append(query)
#             product = res
#             response_list.append(
#                 f"""Score: {product['score']} Product Title: {product['title']} Product Category:
#                 {product['category']} Primary Category {product['primary-category']} Description: {product['description']}""")
#         t2 = time.time()
#         print(f"Time taken for query: {query} is {t2 - t1} seconds")
#         response = run_text_search(query)
#         for res in response:
#             text_response.append(
#                 f"""Score: {res['score']} Product Title: {res['title']} Product Category:
#                 {res['category']} Primary Category {res['primary-category']} Description: {res['description']}""")
#     df['Query'] = query_list
#     df['ANN Response'] = response_list
#     df['Text Search Response'] = text_response
#     df.to_csv('Mongo_Vector_Search.csv', index=False)
#
#
# search()

# threads = []
#
# for i in range(10):
#     t = threading.Thread(target=search)
#     threads.append(t)
#     t.start()
#
# for t in threads:
#     t.join()
#

# client.close()


if __name__ == "__main__":
    connect()
    collection_name = "test"
    # create_index(collection_name, 1536, "euclidean")
    create_atlas_vector_search_index(collection_name)

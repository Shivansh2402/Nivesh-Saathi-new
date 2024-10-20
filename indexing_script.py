from langchain_community.document_loaders import WebBaseLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from uuid import uuid4
# from metahackathonfinance import settings
import pandas as pd
from pymongo import MongoClient


client_uri = "mongodb+srv://developer:3C01meWAequk8vja@metahackathon.3vi4o.mongodb.net/"
DB_NAME = "metahackathon-finance"
COLLECTION_NAME = "nivesh-saathi"
VECTOR_INDEX = "vector_index"
TEXT_INDEX = "text_index"

client = MongoClient(client_uri)

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

embeddings = OpenAIEmbeddings(openai_api_key="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")
vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=VECTOR_INDEX,
)

text_splitter = SemanticChunker(embeddings=embeddings, breakpoint_threshold_type="gradient")

def clean_text(text):
    return ' '.join(text.split())

def load_urls(url_list):
    loader = WebBaseLoader(url_list)
    data = loader.load()
    return data

def create_embeddings(data):
    cleaned_data = []
    for doc in data:
        cleaned_doc = doc
        cleaned_doc.page_content = clean_text(doc.page_content)
        cleaned_data.append(cleaned_doc)

    document_list = []
    metadata_list = []
    for doc in cleaned_data:
        document_list.append(doc.page_content)
        metadata_list.append(doc.metadata)
    docs = text_splitter.create_documents(document_list, metadata_list)
    total_number_of_documents = len(docs)

    uuids = [str(uuid4()) for _ in range(total_number_of_documents)]
    print(f"Total number of documents trained are {total_number_of_documents}")

    return docs, uuids

# Example usage
if __name__ == "__main__":
    url_df = pd.read_csv("/Users/jaymehta/Downloads/nivesh_saathi_urls.csv")
    url_list = url_df['URL'].tolist()
    data = load_urls(url_list)

    docs, uuids = create_embeddings(data)
    vector_store.add_documents(docs, uuids)

    print("All documents indexed...")
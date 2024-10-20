from fastapi import HTTPException, Request
from metahackathonfinance.service.mongo_handler import MongoHandler

from metahackathonfinance import app, settings
from metahackathonfinance.models.requests import MongoInsertRequest, MongoSearchOrDeleteRequest

mongo_handler = MongoHandler(
    connection_uri=settings.mongo_atlas_connection_uri,
    db_name=settings.mongo_atlas_db_name
)


@app.post("/insert")
def insert_document(request: MongoInsertRequest):
    collection_name = request.collection_name
    document = request.document
    try:
        inserted_id = mongo_handler.insert_document(collection_name, document)
        return {"inserted_id": str(inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def find_documents(request: MongoSearchOrDeleteRequest):
    collection_name = request.collection_name
    query = request.query
    try:
        documents = mongo_handler.find_documents(collection_name, query)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
def delete_document(request: MongoSearchOrDeleteRequest):
    collection_name = request.collection_name
    query = request.query
    try:
        deleted_count = mongo_handler.delete_document(collection_name, query)
        return {"deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def close_mongo_connection():
    mongo_handler.close_connection()
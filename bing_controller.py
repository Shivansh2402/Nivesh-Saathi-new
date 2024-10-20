from metahackathonfinance import app
from metahackathonfinance.service.bing_search import search_query_on_bing

from fastapi import HTTPException, Request
from metahackathonfinance.models.requests import QueryRequest


@app.post("/bing-search")
def search_on_bing(request: QueryRequest):
    try:
        response = search_query_on_bing(request.query)
        if response:
            return response
        else:
            raise HTTPException(status_code=500, detail="Failed to get matching response from external API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


import json

from metahackathonfinance import app, my_logger as log
from metahackathonfinance.models.requests import ProcessorRequest
from metahackathonfinance.service.searcher import execute_searcher_request

from fastapi import HTTPException


@app.post("/chat_with_nivesh_sathi")
def match_response(request: ProcessorRequest):
    try:
        # body = request.json()
        log.info(f"Request for Search: {request}")
        response = execute_searcher_request(request)
        if response:
            return response
        else:
            raise HTTPException(status_code=500, detail="Failed to get matching response from external API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
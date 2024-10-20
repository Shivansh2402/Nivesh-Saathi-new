from metahackathonfinance import app
from metahackathonfinance.service import answers_retrofit

from fastapi import HTTPException
from metahackathonfinance.models.requests import AnswersRequest


@app.post("/match_response")
def match_response(request: AnswersRequest):
    try:
        body = request.json()
        response = answers_retrofit.get_matching_response(body)
        if response:
            return response
        else:
            raise HTTPException(status_code=500, detail="Failed to get matching response from external API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


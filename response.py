from pydantic import BaseModel
from jsonobject import StringProperty, FloatProperty, ListProperty, ObjectProperty, JsonObject, BooleanProperty, \
    IntegerProperty
from typing import Optional


import enum


class Status(BaseModel):
        code: int
        message: str


class BaseResponse(BaseModel):
        status : Status
        response : dict


class Thresholds(JsonObject):
    show_matches_above = FloatProperty()
    max_score_diff = FloatProperty()
    related_matches_max_count = IntegerProperty()


class AnswerTypes(enum.Enum):
    SHOW_RELATED_MATCHES = "SHOW_RELATED_MATCHES"
    SMALL_TALK = "SMALL_TALK"
    EXACT_MATCH = "EXACT_MATCH"
    NORMAL_RESPONSE = "NORMAL_RESPONSE"


class BestMatch(BaseModel):
    statement_id: Optional[int] = 0
    response_ref: Optional[int] = 0
    sentence: Optional[str] = None
    category: Optional[str] = None
    entities: Optional[list] = []
    resolved_entities: Optional[list] = []
    locale: Optional[str] = None
    response_type: Optional[str] = None
    response: Optional[str] = None
    flow_key: Optional[str] = None
    debugParams: Optional[dict] = None
    type: Optional[str] = None
    val: Optional[float] = None
    llm_metadata: Optional[dict] = {}
    is_streaming_response: Optional[bool] = False


class ResponseObj(BaseModel):
    answerType: Optional[str] = None
    bestMatch: Optional[BestMatch] = None
    matches: Optional[list] = []
    showRelatedMatchesPrompt: Optional[str] = None
    tags: Optional[list] = []

class Params(BaseModel):
    synonymMap: Optional[dict] = {}
    context: Optional[dict] = {}
    attributesToSet: Optional[dict] = {}


class SearchResponse(BaseModel):
    confident: Optional[bool] = None
    response: Optional[ResponseObj] = None
    params: Optional[Params]= {}
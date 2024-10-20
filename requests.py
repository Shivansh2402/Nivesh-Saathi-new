from typing import Optional

from pydantic import BaseModel
from jsonobject import *


class QueryRequest(BaseModel):
    query: str


class QueryRequestForDetails(BaseModel):
    query: str
    key: str


class MongoInsertRequest(BaseModel):
    collection_name: str
    document: dict


class MongoSearchOrDeleteRequest(BaseModel):
    collection_name: str
    query: dict


class BingQueryRequest(BaseModel):
    query: str


class Tag(JsonObject):
    startOffset: int 
    endOffset: int
    entities: list


class AnswersRequest(BaseModel):
    bot_ref: int
    bot_locale: list
    default_locale: str
    query: str
    categories: list
    excluded_categories: Optional[list] = None
    user_id: str
    api_ai_client_token: str
    custom_logic: Optional[str] = None
    small_talk_enabled: bool
    spell_check_enabled: str
    is_instance: Optional[bool] = None
    bot_category: Optional[str] = None
    is_context_enabled: bool
    tags: list
    entity_enabled: bool
    semantic_search_status: str
    is_ecom_ner_enabled: bool
    is_llm_enabled: bool
    cid: int
    query_timestamp: int


class ProcessorRequest(BaseModel):
    userQuery: Optional[str] = None
    userInfo: Optional[dict] = None
    botId: Optional[int] = None
    cid: Optional[int] = None
    queryTimestamp: Optional[int] = None
    channel: Optional[str] = None
    portalUserId: Optional[int] = None
    masterBotRef: Optional[int] = None
    userQueryId: Optional[str] = None
    enableBotLlmUpload: Optional[bool] = None
    textAndFlowKey: Optional[str] = None
    userType: Optional[str] = None
    llmStreamingTopic: Optional[str] = None
    botKey: Optional[str] = None
    originalQuery: Optional[str] = None
    packetType: Optional[str] = None
